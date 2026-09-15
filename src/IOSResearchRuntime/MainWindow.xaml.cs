using System.Windows;
using IOSResearchRuntime.Core;
using IOSResearchRuntime.Models;
using IOSResearchRuntime.Services;

namespace IOSResearchRuntime;

public partial class MainWindow : Window
{
    private readonly RuntimeCoordinator _coordinator;

    public MainWindow()
    {
        InitializeComponent();

        var layout = new RuntimeLayout();
        var validator = new FirmwareBundleValidator(layout);
        var commandBuilder = new QemuCommandBuilder(layout);
        var runtime = new QemuRuntime(layout, commandBuilder);
        _coordinator = new RuntimeCoordinator(validator, runtime);

        _coordinator.StatusChanged += CoordinatorOnStatusChanged;
        _coordinator.LogReceived += CoordinatorOnLogReceived;

        Loaded += (_, _) => RenderSnapshot(_coordinator.Refresh());
        Closed += (_, _) => _coordinator.Dispose();
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

    private void CoordinatorOnStatusChanged(object? sender, RuntimeSnapshot snapshot)
    {
        Dispatcher.Invoke(() => RenderSnapshot(snapshot));
    }

    private void CoordinatorOnLogReceived(object? sender, string line)
    {
        Dispatcher.Invoke(() =>
        {
            LogTextBox.AppendText(line + Environment.NewLine);
            LogTextBox.ScrollToEnd();
        });
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
        RefreshButton.IsEnabled = !busy && snapshot.State != RuntimeState.Running;
        StartButton.IsEnabled = snapshot.State == RuntimeState.Ready;
        StopButton.IsEnabled = snapshot.State is RuntimeState.Running or RuntimeState.Booting;
    }
}
