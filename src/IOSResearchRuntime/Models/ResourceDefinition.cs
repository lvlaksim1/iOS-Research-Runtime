namespace IOSResearchRuntime.Models;

public sealed class ResourceManifest
{
    public required List<ResourceDefinition> Resources { get; init; }
}

public sealed class ResourceDefinition
{
    public required string Name { get; init; }
    public required string Version { get; init; }
    public required string Url { get; init; }
    public required string Sha256 { get; init; }
    public required string FileName { get; init; }
}
