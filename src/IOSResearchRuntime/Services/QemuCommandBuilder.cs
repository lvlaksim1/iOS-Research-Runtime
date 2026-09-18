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
            // The 0x...0dad50 block is now proven to construct the bad X0 itself:
            // ADRP/LDR X8 from 0x...0921f8, ADRP/LDR X9 from 0x...091040,
            // SUB X8,X22,X8, then ADD X0,X8,X9. The previous TB-level trace only
            // shows entry and exit register sets. Force one instruction per TB and
            // keep the log filter tightly on this seven-instruction block so the
            // next evidence exposes both loaded globals and the exact arithmetic.
            "-one-insn-per-tb",
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
