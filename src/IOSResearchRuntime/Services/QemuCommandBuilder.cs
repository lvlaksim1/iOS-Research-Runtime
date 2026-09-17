namespace IOSResearchRuntime.Services;

public sealed class QemuCommandBuilder
{
    private readonly RuntimeLayout _layout;

    public QemuCommandBuilder(RuntimeLayout layout)
    {
        _layout = layout;
    }

    public IReadOnlyList<string> BuildArguments()
    {
        var firmware = _layout.FirmwareDirectory;
        var arguments = new List<string>
        {
            "-M", "darwin",
            "-bootkc", Path.Combine(firmware, "bootkc"),
            "-dtree", Path.Combine(firmware, "dtree"),
            "-tc", Path.Combine(firmware, "ramdisk.tc"),
            "-ramdisk", Path.Combine(firmware, "ramdisk.dmg"),
            "-args", "rd=md0 serial=3 -v -noprogress wdt=-1 wlan-olyhal-abort",
            "-nographic",
            "-serial", "mon:stdio",
            "-m", "8G",
            // The bounded physical trace reaches the MMU handoff at
            // 0x100070a37a4, but the assumed high virtual range did not capture
            // the first translated block after that handoff. Trace translated
            // blocks without an address filter so the next E2E run records the
            // actual destination. in_asm logs newly translated blocks rather
            // than the high-volume exception/memory-access streams that caused
            // the earlier diagnostic flood.
            "-d", "in_asm,unimp,guest_errors,cpu_reset"
        };

        var sptm = Path.Combine(firmware, "sptm");
        var txm = Path.Combine(firmware, "txm");

        if (File.Exists(sptm) && File.Exists(txm))
        {
            arguments.Add("-sptm");
            arguments.Add(sptm);
            arguments.Add("-txm");
            arguments.Add(txm);
        }

        return arguments;
    }
}
