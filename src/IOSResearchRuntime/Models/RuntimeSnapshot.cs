using IOSResearchRuntime.Core;

namespace IOSResearchRuntime.Models;

public sealed record RuntimeSnapshot(
    RuntimeState State,
    string Message,
    IReadOnlyList<string> MissingItems)
{
    public static RuntimeSnapshot NotReady(string message, IReadOnlyList<string> missingItems) =>
        new(RuntimeState.NotReady, message, missingItems);

    public static RuntimeSnapshot Ready(string message) =>
        new(RuntimeState.Ready, message, Array.Empty<string>());
}
