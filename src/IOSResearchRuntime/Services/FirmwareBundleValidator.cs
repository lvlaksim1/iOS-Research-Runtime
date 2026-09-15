using IOSResearchRuntime.Models;

namespace IOSResearchRuntime.Services;

public sealed class FirmwareBundleValidator
{
    private static readonly string[] RequiredFirmwareFiles =
    [
        "bootkc",
        "dtree",
        "ramdisk.tc",
        "ramdisk.dmg"
    ];

    private readonly RuntimeLayout _layout;

    public FirmwareBundleValidator(RuntimeLayout layout)
    {
        _layout = layout;
    }

    public RuntimeSnapshot Validate()
    {
        _layout.EnsureDirectories();

        var missing = new List<string>();

        if (!File.Exists(_layout.QemuExecutable))
        {
            missing.Add(@"tools\qemu-sptm\qemu-system-aarch64.exe");
        }

        foreach (var fileName in RequiredFirmwareFiles)
        {
            if (!File.Exists(Path.Combine(_layout.FirmwareDirectory, fileName)))
            {
                missing.Add($@"firmware\{fileName}");
            }
        }

        var hasSptm = File.Exists(Path.Combine(_layout.FirmwareDirectory, "sptm"));
        var hasTxm = File.Exists(Path.Combine(_layout.FirmwareDirectory, "txm"));

        if (hasSptm != hasTxm)
        {
            missing.Add(hasSptm ? @"firmware\txm" : @"firmware\sptm");
        }

        if (missing.Count > 0)
        {
            return RuntimeSnapshot.NotReady(
                "Среда ещё не подготовлена. Отсутствуют обязательные компоненты.",
                missing);
        }

        return RuntimeSnapshot.Ready("Среда подготовлена. Можно запускать iOS runtime.");
    }
}
