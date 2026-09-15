namespace IOSResearchRuntime.Models;

public sealed record ProvisioningProfile(
    string DisplayName,
    string DeviceName,
    string BoardName,
    string KernelExtension,
    string ChipName,
    string SystemSdk,
    string IpswUrl)
{
    public static ProvisioningProfile Default { get; } = new(
        DisplayName: "iPhone 16 / iOS 27.0 (24A437)",
        DeviceName: "iPhone17,3",
        BoardName: "d47ap",
        KernelExtension: "iphone17",
        ChipName: "t8140",
        SystemSdk: "iphoneos",
        IpswUrl: "https://updates.cdn-apple.com/2026FallFCS/5130b3f9-3b4e-469a-b60e-93f6b310cdd9/iPhone17,3_27.0_24A437_Restore.ipsw");
}
