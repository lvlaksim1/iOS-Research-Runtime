using IOSResearchRuntime.Core;
using IOSResearchRuntime.Models;
using IOSResearchRuntime.Services;

static string RequireOption(string[] args, string name)
{
    var index = Array.IndexOf(args, name);
    if (index < 0 || index + 1 >= args.Length || string.IsNullOrWhiteSpace(args[index + 1]))
    {
        throw new ArgumentException($"Missing required option {name}.");
    }

    return args[index + 1];
}

static int ReadIntOption(string[] args, string name, int defaultValue)
{
    var index = Array.IndexOf(args, name);
    if (index < 0)
    {
        return defaultValue;
    }

    if (index + 1 >= args.Length || !int.TryParse(args[index + 1], out var value) || value <= 0)
    {
        throw new ArgumentException($"Invalid value for {name}.");
    }

    return value;
}

var applicationDirectory = Path.GetFullPath(RequireOption(args, "--application-directory"));
var dataDirectory = Path.GetFullPath(RequireOption(args, "--data-directory"));
var timeoutMinutes = ReadIntOption(args, "--timeout-minutes", 45);

using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(timeoutMinutes));
var cancellationToken = timeout.Token;

Console.WriteLine($"APPLICATION_DIRECTORY={applicationDirectory}");
Console.WriteLine($"DATA_DIRECTORY={dataDirectory}");
Console.WriteLine($"TIMEOUT_MINUTES={timeoutMinutes}");

var layout = new RuntimeLayout(applicationDirectory, dataDirectory);
var processRunner = new ExternalProcessRunner();
var deviceTreePatcher = new AppleDeviceTreePatcher();

using var toolBootstrap = new ToolBootstrapService(layout);
using var resourceBootstrap = new ResourceBootstrapService(layout);
var rawProvisioning = new RawFirmwareProvisioningService(
    layout,
    processRunner,
    deviceTreePatcher);
var ramdiskProvisioning = new RamdiskProvisioningService(
    layout,
    processRunner,
    new TrustCacheBuilder());

toolBootstrap.ProgressChanged += (_, line) => Console.WriteLine(line);
resourceBootstrap.ProgressChanged += (_, line) => Console.WriteLine(line);
rawProvisioning.ProgressChanged += (_, line) => Console.WriteLine(line);
ramdiskProvisioning.ProgressChanged += (_, line) => Console.WriteLine(line);

Console.WriteLine("[integration] Provisioning start.");
await toolBootstrap.BootstrapAllAsync(cancellationToken);
await resourceBootstrap.BootstrapAllAsync(cancellationToken);
await rawProvisioning.PrepareAsync(ProvisioningProfile.Default, cancellationToken);
await ramdiskProvisioning.PrepareAsync(cancellationToken);

var validator = new FirmwareBundleValidator(layout);
var validation = validator.Validate();
if (validation.State != RuntimeState.Ready)
{
    throw new InvalidOperationException(
        "Provisioning did not produce a valid runtime bundle: " +
        string.Join(", ", validation.MissingItems));
}

Console.WriteLine("[integration] Provisioning validated.");

var commandBuilder = new QemuCommandBuilder(layout);
var qemuRuntime = new QemuRuntime(layout, commandBuilder);
using var coordinator = new RuntimeCoordinator(validator, qemuRuntime);

var proofCompleted = new TaskCompletionSource(
    TaskCreationOptions.RunContinuationsAsynchronously);

coordinator.LogReceived += (_, line) =>
{
    Console.WriteLine(line);

    if (line.StartsWith("[proof] Диагностика завершена;", StringComparison.Ordinal))
    {
        proofCompleted.TrySetResult();
    }

    if (line.StartsWith("[proof] ОШИБКА:", StringComparison.Ordinal))
    {
        proofCompleted.TrySetException(
            new InvalidOperationException(line));
    }
};

coordinator.StatusChanged += (_, snapshot) =>
{
    Console.WriteLine($"[state] {snapshot.State}: {snapshot.Message}");

    if (snapshot.State == RuntimeState.Failed)
    {
        proofCompleted.TrySetException(
            new InvalidOperationException(snapshot.Message));
    }
};

try
{
    Console.WriteLine("[integration] Boot start.");
    await coordinator.StartAsync(cancellationToken);

    await proofCompleted.Task.WaitAsync(cancellationToken);

    Console.WriteLine("BOOT_PROOF_OK");
    Console.WriteLine($"BOOT_EVIDENCE={qemuRuntime.CurrentLogPath}");
}
finally
{
    try
    {
        await coordinator.StopAsync(CancellationToken.None);
    }
    catch (Exception exception)
    {
        Console.WriteLine($"[integration] Stop warning: {exception.Message}");
    }
}

return 0;
