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
            // The 0x...0dad50 block is proven to construct the bad X0 from two
            // globals and X22. The previous diagnostic used -one-insn-per-tb as a
            // top-level option, but this tested QEMU exits before guest execution.
            // one-insn-per-tb is a TCG accelerator property, so enable it through
            // -accel while keeping the trace restricted to the seven instructions.
            "-accel", "tcg,one-insn-per-tb=on",
            "-D", debugLog,
            "-d", "in_asm,exec,nochain,cpu,int,unimp,guest_errors,cpu_reset",
            "-dfilter", "0xfffffff0070dad50+0x20"
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
