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
            // Keep guest serial on raw stdio. The QEMU monitor is disabled so
            // root-proof commands cannot be consumed by the stdio multiplexer.
            "-qmp", $"unix:{Path.Combine(_layout.DataDirectory, "ios-m3-qmp.sock")},server=on,wait=off",
            "-monitor", "none",
            "-serial", "stdio",
            // BootKC contains IONVMeFamily while VirtIO storage is absent. Probe the
            // smallest host-backed transport without staging SystemOS: expose an
            // empty raw image through QEMU NVMe and let the guest tell us whether
            // this darwin machine maps it to an IONVMe-compatible controller.
            "-drive", $"file={Path.Combine(_layout.DataDirectory, "ios-m3-nvme-probe.img")},if=none,format=raw,id=iosm3nvme",
            "-device", "pcie-root-port,id=iosm3rp,bus=pcie.0,addr=1,chassis=1,slot=1",
            "-device", "nvme,drive=iosm3nvme,serial=IOSM3PROBE,bus=iosm3rp",
            "-m", "8G",
            // The exact b1295ce E2E trace still first sees 0x12ed0000 at
            // the load from boot-state slot 0x...090b80 at 0x...0b3978.
            // The newly traced 0x...0b2000 page contains no earlier carrier,
            // so continue the producer search one page farther upstream while
            // preserving one-insn TCG and both SPTM proof windows unchanged.
            "-accel", "tcg,one-insn-per-tb=on",
            "-D", debugLog,
            "-d", "in_asm,exec,nochain,cpu,int,unimp,guest_errors,cpu_reset",
            "-dfilter", "0xfffffff0070b1000+0x2b60,0xfffffff0070d7b50+0x50,0xfffffff0070dad50+0x20"
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
