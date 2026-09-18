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
            // The callee at 0x...0dad50 is now proven to implement the usual
            // phys->virt translation X0 = X22 - phys_base + virt_base. Its globals
            // are 0x10000000000 and 0xfffffff000000000, while X22 arrives as only
            // 0x12ed0000. Trace the immediate caller as well as the translation so
            // the next evidence shows where that offset-valued X22 is produced.
            "-accel", "tcg,one-insn-per-tb=on",
            "-D", debugLog,
            "-d", "in_asm,exec,nochain,cpu,int,unimp,guest_errors,cpu_reset",
            "-dfilter", "0xfffffff0070d7b50+0x50,0xfffffff0070dad50+0x20"
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
