namespace IOSResearchRuntime.Services;

public sealed class RuntimeLayout
{
    public RuntimeLayout()
    {
        ApplicationDirectory = AppContext.BaseDirectory;
        DataDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "iOSResearchRuntime");
        FirmwareDirectory = Path.Combine(DataDirectory, "firmware");
        LogDirectory = Path.Combine(DataDirectory, "logs");
        CacheDirectory = Path.Combine(DataDirectory, "cache");
        ToolDirectory = Path.Combine(DataDirectory, "tools");
        IpswExecutable = Path.Combine(ToolDirectory, "ipsw", "ipsw.exe");
        ApfsExecutable = Path.Combine(ToolDirectory, "apfs", "apfs.exe");
        NvramTemplate = Path.Combine(
            ApplicationDirectory,
            "runtime",
            "firmware",
            "nvram.bin");
        QemuExecutable = Path.Combine(
            ApplicationDirectory,
            "tools",
            "qemu-sptm",
            "qemu-system-aarch64.exe");
    }

    public string ApplicationDirectory { get; }
    public string DataDirectory { get; }
    public string FirmwareDirectory { get; }
    public string LogDirectory { get; }
    public string CacheDirectory { get; }
    public string ToolDirectory { get; }
    public string IpswExecutable { get; }
    public string ApfsExecutable { get; }
    public string NvramTemplate { get; }
    public string QemuExecutable { get; }

    public void EnsureDirectories()
    {
        Directory.CreateDirectory(DataDirectory);
        Directory.CreateDirectory(FirmwareDirectory);
        Directory.CreateDirectory(LogDirectory);
        Directory.CreateDirectory(CacheDirectory);
        Directory.CreateDirectory(ToolDirectory);
    }
}
