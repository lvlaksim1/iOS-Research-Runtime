using System.Windows;
using IOSResearchRuntime.Core;
using IOSResearchRuntime.Models;
using IOSResearchRuntime.Services;

namespace IOSResearchRuntime;

public partial class MainWindow : Window
{
    private readonly RuntimeCoordinator _coordinator;
    private readonly ToolBootstrapService _toolBootstrap;
    private readonly ResourceBootstrapService _resourceBootstrap;
    private readonly RawFirmwareProvisioningService _rawFirmwareProvisioning;
    private readonly RamdiskProvisioningService _ramdiskProvisioning;

    public MainWindow()
    {
        InitializeComponent();

        var layout = new RuntimeLayout();
        var processRunner = new ExternalProcessRunner();
        var deviceTreePatcher = new AppleDeviceTreePatcher();
        var validator = new FirmwareBundleValidator(layout);
        var commandBuilder = new QemuCommandBuilder(layout);
        var runtime = new QemuRuntime(layout, commandBuilder);

        _coordinator = new RuntimeCoordinator(validator, runtime);
        _toolBootstrap = new ToolBootstrapService(layout);
        _resourceBootstrap = new ResourceBootstrapService(layout);
        _rawFirmwareProvisioning = new RawFirmwareProvisioningService(
            layout,
            processRunner,
            deviceTreePatcher);
        _ramdiskProvisioning = new RamdiskProvisioningService(
            layout,
            processRunner,
            new TrustCacheBuilder());

        _coordinator.StatusChanged += CoordinatorOnStatusChanged;
        _coordinator.LogReceived += CoordinatorOnLogReceived;
        _toolBootstrap.ProgressChanged += ToolBootstrapOnProgressChanged;
        _resourceBootstrap.ProgressChanged += ResourceBootstrapOnProgressChanged;
        _rawFirmwareProvisioning.ProgressChanged += RawFirmwareOnProgressChanged;
        _ramdiskProvisioning.ProgressChanged += RamdiskProvisioningOnProgressChanged;

        Loaded += (_, _) => RenderSnapshot(_coordinator.Refresh());
        Closed += (_, _) =>
        {
            _resourceBootstrap.Dispose();
            _toolBootstrap.Dispose();
            _coordinator.Dispose();
        };
    }

    private async void PrepareButton_Click(object sender, RoutedEventArgs e)
    {
        SetProvisioningButtons(enabled: false);

        try
        {
            StatusText.Text = "Подготовка";
            DetailsText.Text = "Загрузка инструментов и подготовка iOS/Darwin firmware bundle…";
            AppendLog("[provision] Полная подготовка iOS runtime…");
            await _toolBootstrap.BootstrapAllAsync();
            await _resourceBootstrap.BootstrapAllAsync();
            await _rawFirmwareProvisioning.PrepareAsync(ProvisioningProfile.Default);
            await _ramdiskProvisioning.PrepareAsync();
            AppendLog("[provision] Firmware bundle полностью подготовлен.");
        }
        catch (Exception exception)
        {
            AppendLog("[provision] ОШИБКА: " + exception.Message);
        }
        finally
        {
            SetProvisioningButtons(enabled: true);
            RenderSnapshot(_coordinator.Refresh());
        }
    }

    private async void StartButton_Click(object sender, RoutedEventArgs e)
    {
        await _coordinator.StartAsync();
    }

    private async void StopButton_Click(object sender, RoutedEventArgs e)
    {
        await _coordinator.StopAsync();
    }

    private void ToolBootstrapOnProgressChanged(object? sender, string line)
    {
        Dispatcher.Invoke(() => AppendLog(line));
    }

    private void ResourceBootstrapOnProgressChanged(object? sender, string line)
    {
        Dispatcher.Invoke(() => AppendLog(line));
    }

    private void RawFirmwareOnProgressChanged(object? sender, string line)
    {
        Dispatcher.Invoke(() => AppendLog(line));
    }

    private void RamdiskProvisioningOnProgressChanged(object? sender, string line)
    {
        Dispatcher.Invoke(() => AppendLog(line));
    }

    private void CoordinatorOnStatusChanged(object? sender, RuntimeSnapshot snapshot)
    {
        Dispatcher.Invoke(() => RenderSnapshot(snapshot));
    }

    private void CoordinatorOnLogReceived(object? sender, string line)
    {
        Dispatcher.Invoke(() => AppendLog(line));
    }

    private void AppendLog(string line)
    {
        LogTextBox.AppendText(line + Environment.NewLine);
        LogTextBox.ScrollToEnd();
    }

    private void SetProvisioningButtons(bool enabled)
    {
        PrepareButton.IsEnabled = enabled;
    }

    private void RenderSnapshot(RuntimeSnapshot snapshot)
    {
        StatusText.Text = snapshot.State switch
        {
            RuntimeState.NotReady => "Не готово",
            RuntimeState.Ready => "Готово",
            RuntimeState.Booting => "Загрузка",
            RuntimeState.Running => "Запущено",
            RuntimeState.Stopping => "Остановка",
            RuntimeState.Failed => "Ошибка",
            _ => snapshot.State.ToString()
        };

        DetailsText.Text = snapshot.MissingItems.Count == 0
            ? snapshot.Message
            : snapshot.Message + Environment.NewLine +
              string.Join(Environment.NewLine, snapshot.MissingItems.Select(item => "• " + item));

        var busy = snapshot.State is RuntimeState.Booting or RuntimeState.Stopping;
        PrepareButton.IsEnabled = PrepareButton.IsEnabled && !busy && snapshot.State != RuntimeState.Running;
        StartButton.IsEnabled = snapshot.State == RuntimeState.Ready;
        StopButton.IsEnabled = snapshot.State is RuntimeState.Running or RuntimeState.Booting;
    }
}
