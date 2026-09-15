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

        _coordinator.StatusChanged += CoordinatorOnStatusChanged;
        _coordinator.LogReceived += CoordinatorOnLogReceived;
        _toolBootstrap.ProgressChanged += ToolBootstrapOnProgressChanged;
        _resourceBootstrap.ProgressChanged += ResourceBootstrapOnProgressChanged;
        _rawFirmwareProvisioning.ProgressChanged += RawFirmwareOnProgressChanged;

        Loaded += (_, _) => RenderSnapshot(_coordinator.Refresh());
        Closed += (_, _) =>
        {
            _resourceBootstrap.Dispose();
            _toolBootstrap.Dispose();
            _coordinator.Dispose();
        };
    }

    private async void ToolsButton_Click(object sender, RoutedEventArgs e)
    {
        SetProvisioningButtons(enabled: false);

        try
        {
            AppendLog("[tools] Подготовка Windows-инструментов и runtime-ресурсов…");
            await _toolBootstrap.BootstrapAllAsync();
            await _resourceBootstrap.BootstrapAllAsync();
            AppendLog("[tools] Инструменты и runtime-ресурсы подготовлены.");
        }
        catch (Exception exception)
        {
            AppendLog("[tools] ОШИБКА: " + exception.Message);
        }
        finally
        {
            SetProvisioningButtons(enabled: true);
            RenderSnapshot(_coordinator.Refresh());
        }
    }

    private async void FirmwareButton_Click(object sender, RoutedEventArgs e)
    {
        SetProvisioningButtons(enabled: false);

        try
        {
            AppendLog("[ipsw] Начинаю подготовку базового firmware-комплекта.");
            await _rawFirmwareProvisioning.PrepareAsync(ProvisioningProfile.Default);
        }
        catch (Exception exception)
        {
            AppendLog("[ipsw] ОШИБКА: " + exception.Message);
        }
        finally
        {
            SetProvisioningButtons(enabled: true);
            RenderSnapshot(_coordinator.Refresh());
        }
    }

    private void RefreshButton_Click(object sender, RoutedEventArgs e)
    {
        RenderSnapshot(_coordinator.Refresh());
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
        ToolsButton.IsEnabled = enabled;
        FirmwareButton.IsEnabled = enabled;
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
        ToolsButton.IsEnabled = ToolsButton.IsEnabled && !busy && snapshot.State != RuntimeState.Running;
        FirmwareButton.IsEnabled = FirmwareButton.IsEnabled && !busy && snapshot.State != RuntimeState.Running;
        RefreshButton.IsEnabled = !busy && snapshot.State != RuntimeState.Running;
        StartButton.IsEnabled = snapshot.State == RuntimeState.Ready;
        StopButton.IsEnabled = snapshot.State is RuntimeState.Running or RuntimeState.Booting;
    }
}
