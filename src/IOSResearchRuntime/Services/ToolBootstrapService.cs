using IOSResearchRuntime.Models;

namespace IOSResearchRuntime.Services;

public sealed class ToolBootstrapService : IDisposable
{
    private readonly RuntimeLayout _layout;
    private readonly HttpClient _httpClient = new();
    private readonly string _manifestPath;

    public ToolBootstrapService(RuntimeLayout layout)
    {
        _layout = layout;
        _manifestPath = Path.Combine(_layout.ApplicationDirectory, "runtime", "tools.json");
    }

    public event EventHandler<string>? ProgressChanged;

    public async Task BootstrapAllAsync(CancellationToken cancellationToken = default)
    {
        _layout.EnsureDirectories();
        var manifest = await LoadManifestAsync(cancellationToken);

        foreach (var tool in manifest.Tools)
        {
            await BootstrapToolAsync(tool, cancellationToken);
        }

        ProgressChanged?.Invoke(this, "[tools] Все закреплённые инструменты подготовлены.");
    }

    private async Task<ToolManifest> LoadManifestAsync(CancellationToken cancellationToken)
    {
        if (!File.Exists(_manifestPath))
        {
            throw new FileNotFoundException("Не найден runtime/tools.json.", _manifestPath);
        }

        await using var stream = File.OpenRead(_manifestPath);
        var manifest = await JsonSerializer.DeserializeAsync<ToolManifest>(
            stream,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true },
            cancellationToken);

        return manifest ?? throw new InvalidDataException("runtime/tools.json имеет неверный формат.");
    }

    private async Task BootstrapToolAsync(
        ToolDefinition tool,
        CancellationToken cancellationToken)
    {
        var installDirectory = Path.Combine(_layout.ToolDirectory, tool.InstallDirectory);
        var executablePath = Path.Combine(installDirectory, tool.ExecutableName);
        var versionMarker = Path.Combine(installDirectory, ".version");

        if (File.Exists(executablePath) &&
            File.Exists(versionMarker) &&
            string.Equals(
                await File.ReadAllTextAsync(versionMarker, cancellationToken),
                tool.Version,
                StringComparison.Ordinal))
        {
            ProgressChanged?.Invoke(
                this,
                $"[tools] {tool.Name} {tool.Version}: уже установлен.");
            return;
        }

        var archivePath = Path.Combine(
            _layout.CacheDirectory,
            $"{tool.InstallDirectory}-{tool.Version}.zip");

        ProgressChanged?.Invoke(
            this,
            $"[tools] {tool.Name} {tool.Version}: загрузка…");

        await DownloadAsync(tool.ArchiveUrl, archivePath, cancellationToken);
        await VerifySha256Async(archivePath, tool.Sha256, cancellationToken);

        ProgressChanged?.Invoke(
            this,
            $"[tools] {tool.Name}: SHA-256 подтверждён, распаковка…");

        var temporaryDirectory = Path.Combine(
            _layout.CacheDirectory,
            $"extract-{tool.InstallDirectory}-{Guid.NewGuid():N}");

        Directory.CreateDirectory(temporaryDirectory);

        try
        {
            ZipFile.ExtractToDirectory(archivePath, temporaryDirectory, overwriteFiles: true);

            var sourceExecutable = Directory
                .EnumerateFiles(
                    temporaryDirectory,
                    tool.ExecutableName,
                    SearchOption.AllDirectories)
                .SingleOrDefault();

            if (sourceExecutable is null)
            {
                throw new InvalidDataException(
                    $"В архиве {tool.Name} не найден {tool.ExecutableName}.");
            }

            var sourceDirectory = Path.GetDirectoryName(sourceExecutable)
                ?? throw new InvalidDataException("Не удалось определить каталог инструмента.");

            if (Directory.Exists(installDirectory))
            {
                Directory.Delete(installDirectory, recursive: true);
            }

            CopyDirectory(sourceDirectory, installDirectory);
            await File.WriteAllTextAsync(versionMarker, tool.Version, cancellationToken);

            if (!File.Exists(executablePath))
            {
                throw new InvalidDataException(
                    $"После установки отсутствует {tool.ExecutableName}.");
            }

            ProgressChanged?.Invoke(
                this,
                $"[tools] {tool.Name} {tool.Version}: готов.");
        }
        finally
        {
            if (Directory.Exists(temporaryDirectory))
            {
                Directory.Delete(temporaryDirectory, recursive: true);
            }
        }
    }

    private async Task DownloadAsync(
        string url,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync(
            url,
            HttpCompletionOption.ResponseHeadersRead,
            cancellationToken);
        response.EnsureSuccessStatusCode();

        await using var source = await response.Content.ReadAsStreamAsync(cancellationToken);
        await using var destination = File.Create(destinationPath);
        await source.CopyToAsync(destination, cancellationToken);
    }

    private static async Task VerifySha256Async(
        string filePath,
        string expectedHash,
        CancellationToken cancellationToken)
    {
        await using var stream = File.OpenRead(filePath);
        using var sha256 = SHA256.Create();
        var hash = await sha256.ComputeHashAsync(stream, cancellationToken);
        var actualHash = Convert.ToHexString(hash).ToLowerInvariant();

        if (!string.Equals(actualHash, expectedHash, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidDataException(
                $"SHA-256 не совпадает. Ожидалось {expectedHash}, получено {actualHash}.");
        }
    }

    private static void CopyDirectory(string sourceDirectory, string destinationDirectory)
    {
        Directory.CreateDirectory(destinationDirectory);

        foreach (var file in Directory.EnumerateFiles(sourceDirectory))
        {
            File.Copy(
                file,
                Path.Combine(destinationDirectory, Path.GetFileName(file)),
                overwrite: true);
        }

        foreach (var directory in Directory.EnumerateDirectories(sourceDirectory))
        {
            CopyDirectory(
                directory,
                Path.Combine(destinationDirectory, Path.GetFileName(directory)));
        }
    }

    public void Dispose()
    {
        _httpClient.Dispose();
    }
}
