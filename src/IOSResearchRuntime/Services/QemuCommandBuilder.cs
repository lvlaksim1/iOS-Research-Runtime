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
        var debugLog = Path.Combine(_layout.LogDirectory, "qemu-debug.log");
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
            // Persist QEMU diagnostics directly into the runtime log directory.
            // The previous unfiltered in_asm trace proved that execution crosses
            // the MMU handoff and reaches the 0xfffffff0070bxxxx virtual region,
            // but in_asm only records translation and cannot reveal a tight loop
            // through already translated blocks. Trace executions in that narrow
            // region with chaining disabled so the next E2E run identifies the
            // repeatedly executed TB without recreating a whole-guest trace flood.
            "-D", debugLog,
            "-d", "in_asm,exec,nochain,unimp,guest_errors,cpu_reset",
            "-dfilter", "0xfffffff0070b0000+0x20000"
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
