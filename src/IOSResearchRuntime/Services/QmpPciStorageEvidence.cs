using System.Text.Json;

namespace IOSResearchRuntime.Services;

/// <summary>
/// Classifies a QMP query-pci reply. This is host-side PCI-model evidence only:
/// it cannot establish that an iOS IOKit driver bound or that /dev/disk exists.
/// </summary>
public static class QmpPciStorageEvidence
{
    public sealed record NvmeCandidate(int Bus, int Slot, int Function, string? QdevId);

    public sealed record Result(
        bool ValidQueryPciReply,
        IReadOnlyList<NvmeCandidate> HostNvmeCandidates,
        string Classification,
        bool GuestNvmeBound = false,
        bool Stage1Accepted = false);

    public static Result Evaluate(string? qmpReply)
    {
        if (string.IsNullOrWhiteSpace(qmpReply))
        {
            return Invalid();
        }

        try
        {
            using var document = JsonDocument.Parse(qmpReply);
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object ||
                !root.TryGetProperty("return", out var buses) ||
                buses.ValueKind != JsonValueKind.Array)
            {
                // QMP greetings, events, errors and command acknowledgements
                // are not successful query-pci topology responses.
                return Invalid();
            }

            var candidates = new List<NvmeCandidate>();
            foreach (var bus in buses.EnumerateArray())
            {
                if (bus.ValueKind != JsonValueKind.Object)
                {
                    return Invalid();
                }

                WalkBus(bus, candidates);
            }

            return new Result(
                true,
                candidates.AsReadOnly(),
                candidates.Count == 0
                    ? "NO_HOST_NVME_CLASS_OBSERVED"
                    : "HOST_NVME_CLASS_OBSERVED_GUEST_BINDING_UNPROVEN");
        }
        catch (JsonException)
        {
            return Invalid();
        }
    }

    private static void WalkBus(JsonElement bus, List<NvmeCandidate> candidates)
    {
        if (!bus.TryGetProperty("devices", out var devices) ||
            devices.ValueKind != JsonValueKind.Array)
        {
            return;
        }

        var busNumber = Number(bus, "bus") ?? -1;
        foreach (var device in devices.EnumerateArray())
        {
            if (device.ValueKind != JsonValueKind.Object)
            {
                continue;
            }

            if (device.TryGetProperty("class_info", out var classInfo) &&
                classInfo.ValueKind == JsonValueKind.Object &&
                Number(classInfo, "class") is int pciClass &&
                (pciClass == 0x0108 || (pciClass >> 8) == 0x0108))
            {
                var id = device.TryGetProperty("qdev_id", out var qdevId) &&
                         qdevId.ValueKind == JsonValueKind.String
                    ? qdevId.GetString()
                    : null;
                candidates.Add(new NvmeCandidate(
                    Number(device, "bus") ?? busNumber,
                    Number(device, "slot") ?? -1,
                    Number(device, "function") ?? -1,
                    id));
            }

            if (device.TryGetProperty("pci_bridge", out var bridge) &&
                bridge.ValueKind == JsonValueKind.Object)
            {
                // query-pci nests downstream devices inside pci_bridge.devices.
                // The secondary bus number is in bus.number in QEMU's response.
                if (bridge.TryGetProperty("bus", out var childBus) &&
                    childBus.ValueKind == JsonValueKind.Object)
                {
                    WalkBus(childBus, candidates);
                }
                else
                {
                    WalkBus(bridge, candidates);
                }
            }
        }
    }

    private static int? Number(JsonElement element, string name)
    {
        return element.TryGetProperty(name, out var value) &&
               value.ValueKind == JsonValueKind.Number &&
               value.TryGetInt32(out var number)
            ? number
            : null;
    }

    private static Result Invalid() => new(
        false,
        Array.Empty<NvmeCandidate>(),
        "NOT_A_VALID_QUERY_PCI_REPLY");
}
