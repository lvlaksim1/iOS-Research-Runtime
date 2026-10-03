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

static async Task SendProbeLineAsync(
    QemuRuntime runtime,
    string line,
    CancellationToken cancellationToken)
{
    await runtime.SendLineAsync(line, cancellationToken);
    await Task.Delay(TimeSpan.FromSeconds(15), cancellationToken);
}

var applicationDirectory = Path.GetFullPath(RequireOption(args, "--application-directory"));
var dataDirectory = Path.GetFullPath(RequireOption(args, "--data-directory"));
var timeoutMinutes = ReadIntOption(args, "--timeout-minutes", 45);
var bootProgressTimeoutMinutes = ReadIntOption(args, "--boot-progress-timeout-minutes", 5);

using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(timeoutMinutes));
var cancellationToken = timeout.Token;

Console.WriteLine($"APPLICATION_DIRECTORY={applicationDirectory}");
Console.WriteLine($"DATA_DIRECTORY={dataDirectory}");
Console.WriteLine($"TIMEOUT_MINUTES={timeoutMinutes}");
Console.WriteLine($"BOOT_PROGRESS_TIMEOUT_MINUTES={bootProgressTimeoutMinutes}");

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

var pinnedIoprintSha256 = "8d1425e8f63416da64ed4c5789109eff2535b44327469d879134eb89c31320ee";
var pinnedIoprint = Directory
    .EnumerateFiles(Path.GetTempPath(), "ioprint", SearchOption.AllDirectories)
    .Select(path => new FileInfo(path))
    .Where(file => file.Exists && file.Length > 0)
    .OrderByDescending(file => file.LastWriteTimeUtc)
    .FirstOrDefault(file =>
    {
        using var stream = file.OpenRead();
        return Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(stream))
            .Equals(pinnedIoprintSha256, StringComparison.OrdinalIgnoreCase);
    });

if (pinnedIoprint is not null)
{
    var repackedSysroot = Path.Combine(layout.DataDirectory, "ios-cli-tools-with-ioprint.tar");
    File.Copy(layout.IosCliToolsArchive, repackedSysroot, overwrite: true);
    await processRunner.RunAsync(
        "tar",
        new[] { "-rf", repackedSysroot, "-C", pinnedIoprint.DirectoryName!, "--transform=s,^ioprint$,usr/local/bin/ioprint,", "ioprint" },
        cancellationToken);
    File.Copy(repackedSysroot, layout.IosCliToolsArchive, overwrite: true);
    Console.WriteLine($"[integration] PINNED_IOPRINT_STAGED={pinnedIoprint.FullName}");
}

await ramdiskProvisioning.PrepareAsync(cancellationToken);

var apfsEvidencePath = Path.Combine(layout.LogDirectory, "apfs-structural-evidence.json");
if (!File.Exists(apfsEvidencePath) || new FileInfo(apfsEvidencePath).Length == 0)
{
    throw new InvalidDataException("Decoded APFS structural evidence was not produced by ios-ramdisk-tool.");
}
Console.WriteLine($"[apfs-evidence] APFS_STRUCTURAL_EVIDENCE={apfsEvidencePath}");

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
var bootProgress = new TaskCompletionSource(
    TaskCreationOptions.RunContinuationsAsynchronously);
var boundaryProbeCompleted = new TaskCompletionSource(
    TaskCreationOptions.RunContinuationsAsynchronously);

coordinator.LogReceived += (_, line) =>
{
    Console.WriteLine(line);

    if (line.Contains("Darwin Kernel Version", StringComparison.Ordinal) ||
        line.Contains("com.apple.xpc.launchd", StringComparison.Ordinal) ||
        line.StartsWith("bash-", StringComparison.Ordinal))
    {
        bootProgress.TrySetResult();
    }

    if (line.StartsWith("[proof] Диагностика завершена;", StringComparison.Ordinal))
    {
        proofCompleted.TrySetResult();
    }

    if (line.StartsWith("[proof] ОШИБКА:", StringComparison.Ordinal))
    {
        proofCompleted.TrySetException(
            new InvalidOperationException(line));
    }

    if (string.Equals(
            line.Trim(),
            "__IOS_M2_BOUNDARY_END__",
            StringComparison.Ordinal))
    {
        boundaryProbeCompleted.TrySetResult();
    }
};

coordinator.StatusChanged += (_, snapshot) =>
{
    Console.WriteLine($"[state] {snapshot.State}: {snapshot.Message}");

    if (snapshot.State == RuntimeState.Failed)
    {
        var exception = new InvalidOperationException(snapshot.Message);
        bootProgress.TrySetException(exception);
        proofCompleted.TrySetException(exception);
        boundaryProbeCompleted.TrySetException(exception);
    }
};

try
{
    Console.WriteLine("[integration] Boot start.");
    await coordinator.StartAsync(cancellationToken);

    using (var bootProgressTimeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken))
    {
        bootProgressTimeout.CancelAfter(TimeSpan.FromMinutes(bootProgressTimeoutMinutes));
        try
        {
            await bootProgress.Task.WaitAsync(bootProgressTimeout.Token);
            Console.WriteLine("[integration] XNU boot progress observed.");
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            var evidencePath = qemuRuntime.CurrentLogPath ?? "<not-created>";
            throw new TimeoutException(
                $"QEMU produced no XNU/launchd/root-shell progress within {bootProgressTimeoutMinutes} minute(s). " +
                $"Boot evidence: {evidencePath}");
        }
    }

    await proofCompleted.Task.WaitAsync(cancellationToken);

    Console.WriteLine("BOOT_PROOF_OK");
    Console.WriteLine($"BOOT_EVIDENCE={qemuRuntime.CurrentLogPath}");

    Console.WriteLine("[integration] IOS-M2 post-root boundary probe start.");
    var probeLines = new[]
    {
        "echo __IOS_M2_BOUNDARY_BEGIN__",
        "echo __IOS_M2_PROBE_MOUNTS__",
        "mount",
        "echo __IOS_M2_PROBE_SYSTEM_VOLUMES__",
        "ls -la /System/Volumes 2>&1",
        "echo __IOS_M2_PROBE_PREBOOT__",
        "ls -la /private/preboot 2>&1",
        "echo __IOS_M2_PROBE_DEV_DISKS__",
        "ls -la /dev/disk* 2>&1",
        "echo __IOS_M3_PROBE_IONVMEFAMILY_STAGE__",
        "ls -ld /System/Library/Extensions/IONVMeFamily.kext /System/Library/Extensions/IONVMeFamily.kext/Contents/MacOS/IONVMeFamily 2>&1",
        "echo __IOS_M3_PROBE_STORAGE_DIAG_TOOLS__",
        "ls -l /usr/sbin/kextstat /usr/bin/kmutil /usr/bin/dmesg /sbin/kextstat /usr/sbin/ioreg 2>&1",
        "echo __IOS_M3_PROBE_NVME_SUPPORT_TOOLS__",
        "ls -l /usr/bin/nvmefwupdater /System/Library/PrivateFrameworks/AppleNVMe.framework/AppleNVMe /usr/sbin/sysctl 2>&1",
        "echo __IOS_M3_PROBE_BINARY_INSPECTION_TOOLS__",
        "ls -l /usr/bin/otool /usr/bin/dyld_info /usr/bin/nm /usr/bin/strings /usr/bin/sysctl /sbin/sysctl /bin/sysctl 2>&1",
        "echo __IOS_M3_PROBE_PCI_TRANSPORT_STAGE__",
        "ls -l /usr/lib/libPCITransport.dylib /System/DriverKit/System/Library/Frameworks/PCIDriverKit.framework/PCIDriverKit 2>&1",
        "echo __IOS_M3_PROBE_IOREGISTRY_RUNTIME_DEPS__",
        "ls -l /usr/lib/libncurses* /System/Library/Frameworks/IOKit.framework/IOKit /usr/bin/ioreg /usr/sbin/ioreg 2>&1",
        "echo __IOS_M3_PROBE_IOPRINT_PCIE_PROVIDERS__",
        "if [ -x /usr/local/bin/ioprint ]; then echo __IOS_M3_IOPRINT_SHA256_EXPECTED_8d1425e8f63416da64ed4c5789109eff2535b44327469d879134eb89c31320ee__; echo __IOS_M3_IOPRINT_DEVICETREE__; /usr/local/bin/ioprint -p IODeviceTree 2>&1; echo __IOS_M3_IOPRINT_IOSERVICE__; /usr/local/bin/ioprint -p IOService 2>&1; else echo __IOS_M3_IOPRINT_UNAVAILABLE__; fi",
        "echo __IOS_M2_BOUNDARY_END__"
    };

    foreach (var probeLine in probeLines)
    {
        await SendProbeLineAsync(qemuRuntime, probeLine, cancellationToken);
    }

    using (var boundaryProbeTimeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken))
    {
        boundaryProbeTimeout.CancelAfter(TimeSpan.FromMinutes(4));
        try
        {
            await boundaryProbeCompleted.Task.WaitAsync(boundaryProbeTimeout.Token);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            var evidencePath = qemuRuntime.CurrentLogPath ?? "<not-created>";
            throw new TimeoutException(
                "IOS-M2 post-root boundary probe did not reach its terminal marker within 3 minutes. " +
                $"Boot evidence: {evidencePath}");
        }
    }

    Console.WriteLine("IOS_M2_BOUNDARY_PROBE_OK");
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
