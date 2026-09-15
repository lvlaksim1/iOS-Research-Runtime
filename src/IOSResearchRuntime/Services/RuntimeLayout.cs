namespace IOSResearchRuntime.Services;

public sealed class RuntimeLayout
{
    public RuntimeLayout(
        string? applicationDirectory = null,
        string? dataDirectory = null)
    {
        ApplicationDirectory = Path.GetFullPath(
            string.IsNullOrWhiteSpace(applicationDirectory)
                ? AppContext.BaseDirectory
                : applicationDirectory);
        DataDirectory = Path.GetFullPath(
            string.IsNullOrWhiteSpace(dataDirectory)
                ? Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "iOSResearchRuntime")
                : dataDirectory);
        FirmwareDirectory = Path.Combine(DataDirectory, "firmware");
        LogDirectory = Path.Combine(DataDirectory, "logs");
        CacheDirectory = Path.Combine(DataDirectory, "cache");
        ToolDirectory = Path.Combine(DataDirectory, "tools");
        ResourceDirectory = Path.Combine(DataDirectory, "resources");

        IpswExecutable = Path.Combine(ToolDirectory, "ipsw", "ipsw.exe");
        RcodesignExecutable = Path.Combine(ToolDirectory, "rcodesign", "rcodesign.exe");
        IosCliToolsArchive = Path.Combine(ResourceDirectory, "ios-cli-tools.tar.gz");

        NvramTemplate = Path.Combine(
            ApplicationDirectory,
            "runtime",
            "firmware",
            "nvram.bin");
        LaunchdPlist = Path.Combine(
            ApplicationDirectory,
            "runtime",
            "ramdisk",
            "com.jprx.bash.plist");
        QemuExecutable = Path.Combine(
            ApplicationDirectory,
            "tools",
            "qemu-sptm",
            "qemu-system-aarch64.exe");
        RamdiskToolExecutable = Path.Combine(
            ApplicationDirectory,
            "tools",
            "ios-ramdisk-tool.exe");
    }

    public string ApplicationDirectory { get; }
    public string DataDirectory { get; }
    public string FirmwareDirectory { get; }
    public string LogDirectory { get; }
    public string CacheDirectory { get; }
    public string ToolDirectory { get; }
    public string ResourceDirectory { get; }
    public string IpswExecutable { get; }
    public string RcodesignExecutable { get; }
    public string IosCliToolsArchive { get; }
    public string NvramTemplate { get; }
    public string LaunchdPlist { get; }
    public string QemuExecutable { get; }
    public string RamdiskToolExecutable { get; }

    public void EnsureDirectories()
    {
        Directory.CreateDirectory(DataDirectory);
        Directory.CreateDirectory(FirmwareDirectory);
        Directory.CreateDirectory(LogDirectory);
        Directory.CreateDirectory(CacheDirectory);
        Directory.CreateDirectory(ToolDirectory);
        Directory.CreateDirectory(ResourceDirectory);
    }
}
