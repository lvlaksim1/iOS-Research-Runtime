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
            // The exact 9651ad5 E2E trace proves 0x12ed0000 first appears
            // at the load from boot-state slot 0x...090b80 at 0x...0b3978.
            // No traced register carries that value from 0x...0b3600 until
            // this load, so the slot producer is earlier. Extend only this
            // caller window backward; keep both SPTM proof windows unchanged.
            "-accel", "tcg,one-insn-per-tb=on",
            "-D", debugLog,
            "-d", "in_asm,exec,nochain,cpu,int,unimp,guest_errors,cpu_reset",
            "-dfilter", "0xfffffff0070b3000+0xb60,0xfffffff0070d7b50+0x50,0xfffffff0070dad50+0x20"
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
