using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class BootProgressDetectorTests
{
    [Fact]
    public void Observe_AdvancesThroughDarwinVmBootMarkers()
    {
        var detector = new BootProgressDetector();

        Assert.Equal(BootStage.QemuStarted, detector.MarkQemuStarted().Stage);
        Assert.Equal(
            BootStage.Kernel,
            detector.Observe(
                "Darwin Kernel Version 27.0.0: Tue Aug 11 22:05:33 PDT 2026; root:xnu-13432.1.9~3/RELEASE_ARM64_T8142\r\n")!.Stage);
        Assert.Equal(
            BootStage.Launchd,
            detector.Observe(
                "com.apple.xpc.launchd|1970-01-01 00:00:29.466851 <Notice>: Darwin Bootstrapper Version 7.0.0\r\n")!.Stage);
        Assert.Equal(
            BootStage.RootShell,
            detector.Observe("bash-3.2# ")!.Stage);
    }

    [Fact]
    public void Observe_DetectsPromptWithoutTrailingNewlineAcrossChunks()
    {
        var detector = new BootProgressDetector();

        detector.MarkQemuStarted();
        Assert.Null(detector.Observe("Darwin Kernel Ver"));
        Assert.Equal(
            BootStage.Kernel,
            detector.Observe("sion 27.0.0\r\n")!.Stage);
        Assert.Null(detector.Observe("com.apple.xpc."));
        Assert.Equal(
            BootStage.Launchd,
            detector.Observe("launchd| boot complete\r\n")!.Stage);
        Assert.Null(detector.Observe("bash-3."));
        Assert.Equal(
            BootStage.RootShell,
            detector.Observe("2# ")!.Stage);
    }

    [Fact]
    public void Observe_DoesNotRegressOrRepeatStages()
    {
        var detector = new BootProgressDetector();

        detector.MarkQemuStarted();
        detector.Observe("Darwin Kernel Version 27.0.0\r\n");
        detector.Observe("com.apple.xpc.launchd| boot\r\n");

        Assert.Null(detector.Observe("Darwin Kernel Version 27.0.0\r\n"));
        Assert.Null(detector.Observe("com.apple.xpc.launchd| another line\r\n"));
        Assert.Equal(BootStage.Launchd, detector.Stage);
    }

    [Fact]
    public void Reset_AllowsASecondBoot()
    {
        var detector = new BootProgressDetector();
        detector.MarkQemuStarted();
        detector.Observe("bash-3.2# ");

        detector.Reset();

        Assert.Equal(BootStage.None, detector.Stage);
        Assert.Equal(BootStage.QemuStarted, detector.MarkQemuStarted().Stage);
    }
}
