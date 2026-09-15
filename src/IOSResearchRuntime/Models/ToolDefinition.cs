namespace IOSResearchRuntime.Models;

public sealed class ToolManifest
{
    public required List<ToolDefinition> Tools { get; init; }
}

public sealed class ToolDefinition
{
    public required string Name { get; init; }
    public required string Version { get; init; }
    public required string ArchiveUrl { get; init; }
    public required string Sha256 { get; init; }
    public required string ExecutableName { get; init; }
    public required string InstallDirectory { get; init; }
}
