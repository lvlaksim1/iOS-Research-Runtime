using IOSResearchRuntime.Models;

namespace IOSResearchRuntime.Services;

public sealed class ResourceBootstrapService : IDisposable
{
    private readonly RuntimeLayout _layout;
    private readonly HttpClient _httpClient = new();
    private readonly string _manifestPath;

    public ResourceBootstrapService(RuntimeLayout layout)
    {
        _layout = layout;
        _manifestPath = Path.Combine(AppContext.BaseDirectory, "runtime", "resources.json");
    }

    public event EventHandler<string>? ProgressChanged;

    public async Task BootstrapAllAsync(CancellationToken cancellationToken = default)
    {
        _layout.EnsureDirectories();
        var manifest = await LoadManifestAsync(cancellationToken);

        foreach (var resource in manifest.Resources)
        {
            await BootstrapResourceAsync(resource, cancellationToken);
        }
    }

    private async Task<ResourceManifest> LoadManifestAsync(CancellationToken cancellationToken)
    {
        if (!File.Exists(_manifestPath))
        {
            throw new FileNotFoundException("Не найден runtime/resources.json.", _manifestPath);
        }

        await using var stream = File.OpenRead(_manifestPath);
        var manifest = await JsonSerializer.DeserializeAsync<ResourceManifest>(
            stream,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true },
            cancellationToken);

        return manifest ?? throw new InvalidDataException("runtime/resources.json имеет неверный формат.");
    }

    private async Task BootstrapResourceAsync(
        ResourceDefinition resource,
        CancellationToken cancellationToken)
    {
        var destination = Path.Combine(_layout.ResourceDirectory, resource.FileName);

        if (File.Exists(destination))
        {
            var existingHash = await ComputeSha256Async(destination, cancellationToken);
            if (string.Equals(existingHash, resource.Sha256, StringComparison.OrdinalIgnoreCase))
            {
                ProgressChanged?.Invoke(
                    this,
                    $"[resources] {resource.Name} {resource.Version}: уже подготовлен.");
                return;
            }

            File.Delete(destination);
        }

        ProgressChanged?.Invoke(
            this,
            $"[resources] {resource.Name} {resource.Version}: загрузка…");

        using var response = await _httpClient.GetAsync(
            resource.Url,
            HttpCompletionOption.ResponseHeadersRead,
            cancellationToken);
        response.EnsureSuccessStatusCode();

        await using (var source = await response.Content.ReadAsStreamAsync(cancellationToken))
        await using (var output = File.Create(destination))
        {
            await source.CopyToAsync(output, cancellationToken);
        }

        var actualHash = await ComputeSha256Async(destination, cancellationToken);
        if (!string.Equals(actualHash, resource.Sha256, StringComparison.OrdinalIgnoreCase))
        {
            File.Delete(destination);
            throw new InvalidDataException(
                $"SHA-256 ресурса {resource.Name} не совпадает. Ожидалось {resource.Sha256}, получено {actualHash}.");
        }

        ProgressChanged?.Invoke(
            this,
            $"[resources] {resource.Name}: SHA-256 подтверждён.");
    }

    private static async Task<string> ComputeSha256Async(
        string path,
        CancellationToken cancellationToken)
    {
        await using var stream = File.OpenRead(path);
        using var sha256 = SHA256.Create();
        var hash = await sha256.ComputeHashAsync(stream, cancellationToken);
        return Convert.ToHexString(hash).ToLowerInvariant();
    }

    public void Dispose()
    {
        _httpClient.Dispose();
    }
}
