using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class QmpPciStorageEvidenceTests
{
    [Fact]
    public void NestedPcieBridge_ReportsHostNvmeButNeverGuestBinding()
    {
        const string reply = """
            {"return":[{"bus":0,"devices":[
              {"bus":0,"slot":1,"function":0,"class_info":{"class":1540},
               "pci_bridge":{"bus":{"number":0,"secondary":1,"subordinate":1},"devices":[
                 {"bus":1,"slot":0,"function":0,"qdev_id":"iosm3nvme",
                  "class_info":{"class":264,"desc":"Non-Volatile memory controller"}}
               ]}}
            ]}],"id":"iosm3-query-pci"}
            """;
        var result = QmpPciStorageEvidence.Evaluate(reply);
        Assert.True(result.ValidQueryPciReply);
        var nvme = Assert.Single(result.HostNvmeCandidates);
        Assert.Equal(1, nvme.Bus);
        Assert.Equal(0, nvme.Slot);
        Assert.Equal(0, nvme.Function);
        Assert.Equal("iosm3nvme", nvme.QdevId);
        Assert.Equal("HOST_NVME_CLASS_OBSERVED_GUEST_BINDING_UNPROVEN", result.Classification);
        Assert.False(result.GuestNvmeBound);
        Assert.False(result.Stage1Accepted);
    }

    [Fact]
    public void NestedPcieBridge_UsesSecondaryBusWhenChildOmitsBus()
    {
        const string reply = """
            {"return":[{"bus":0,"devices":[{"slot":1,"class_info":{"class":1540},
            "pci_bridge":{"bus":{"number":0,"secondary":4,"subordinate":4},
            "devices":[{"slot":2,"function":0,"qdev_id":"nvme-test",
            "class_info":{"class":264}}]}}]}]}
            """;
        var result = QmpPciStorageEvidence.Evaluate(reply);
        Assert.True(result.ValidQueryPciReply);
        var nvme = Assert.Single(result.HostNvmeCandidates);
        Assert.Equal(4, nvme.Bus);
        Assert.Equal(2, nvme.Slot);
        Assert.False(result.GuestNvmeBound);
        Assert.False(result.Stage1Accepted);
    }

    [Fact]
    public void UnconfiguredBridge_DoesNotClaimDownstreamNvme()
    {
        // QEMU omits pci_bridge.devices while PCI_SECONDARY_BUS == 0.
        const string reply = """
            {"return":[{"bus":0,"devices":[{"slot":1,"class_info":{"class":1540},
            "pci_bridge":{"bus":{"number":0,"secondary":0,"subordinate":0}}}]}]}
            """;
        var result = QmpPciStorageEvidence.Evaluate(reply);
        Assert.True(result.ValidQueryPciReply);
        Assert.Empty(result.HostNvmeCandidates);
        Assert.Equal("NO_HOST_NVME_CLASS_OBSERVED", result.Classification);
        Assert.False(result.GuestNvmeBound);
        Assert.False(result.Stage1Accepted);
    }

    [Fact]
    public void NonNvmeDevice_DoesNotProduceCandidate()
    {
        const string reply = """
            {"return":[{"bus":0,"devices":[{"bus":0,"slot":1,"function":0,
            "class_info":{"class":512},"qdev_id":"disk-looking-device"}]}]}
            """;
        var result = QmpPciStorageEvidence.Evaluate(reply);
        Assert.True(result.ValidQueryPciReply);
        Assert.Empty(result.HostNvmeCandidates);
        Assert.Equal("NO_HOST_NVME_CLASS_OBSERVED", result.Classification);
        Assert.False(result.Stage1Accepted);
    }

    [Theory]
    [InlineData("")]
    [InlineData("BSD root: md0\\nlaunchd pid1")]
    [InlineData("{\"event\":\"RESET\"}")]
    [InlineData("{\"error\":{\"class\":\"GenericError\"}}")]
    [InlineData("{\"return\":{}}")]
    [InlineData("{\"return\":[]")]
    public void NotQueryPciReply_NeverReportsStorage(string input)
    {
        var result = QmpPciStorageEvidence.Evaluate(input);
        Assert.False(result.ValidQueryPciReply);
        Assert.Empty(result.HostNvmeCandidates);
        Assert.False(result.GuestNvmeBound);
        Assert.False(result.Stage1Accepted);
    }

    [Fact]
    public void FullClassCodeForm_IsRecognizedButNeverAcceptedAsStage1()
    {
        const string reply = """
            {"return":[{"bus":0,"devices":[{"slot":2,"function":0,
            "class_info":{"class":67586}}]}]}
            """;
        var result = QmpPciStorageEvidence.Evaluate(reply);
        Assert.Single(result.HostNvmeCandidates);
        Assert.False(result.Stage1Accepted);
    }
}
