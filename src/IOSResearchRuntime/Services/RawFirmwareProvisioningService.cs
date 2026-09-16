using IOSResearchRuntime.Models;

namespace IOSResearchRuntime.Services;

public sealed class RawFirmwareProvisioningService
{
    private readonly RuntimeLayout _layout;
    private readonly ExternalProcessRunner _processRunner;
    private readonly AppleDeviceTreePatcher _deviceTreePatcher;

    public RawFirmwareProvisioningService(
        RuntimeLayout layout,
        ExternalProcessRunner processRunner,
        AppleDeviceTreePatcher deviceTreePatcher)
    {
        _layout = layout;
        _processRunner = processRunner;
        _deviceTreePatcher = deviceTreePatcher;
    }

    public event EventHandler<string>? ProgressChanged;

    public async Task PrepareAsync(
        ProvisioningProfile profile,
        CancellationToken cancellationToken = default)
    {
        _layout.EnsureDirectories();

        if (!File.Exists(_layout.IpswExecutable))
        {
            throw new FileNotFoundException(
                "ipsw.exe не установлен. Выполните «Подготовить среду».",
                _layout.IpswExecutable);
        }

        if (!File.Exists(_layout.NvramTemplate))
        {
            throw new FileNotFoundException(
                "Не найден встроенный шаблон nvram.bin.",
                _layout.NvramTemplate);
        }

        var stagingRoot = Path.Combine(
            _layout.CacheDirectory,
            $"provision-{Guid.NewGuid():N}");
        var downloadsDirectory = Path.Combine(stagingRoot, "downloads");
        var firmwareDirectory = Path.Combine(stagingRoot, "firmware");

        Directory.CreateDirectory(downloadsDirectory);
        Directory.CreateDirectory(firmwareDirectory);

        try
        {
            ProgressChanged?.Invoke(
                this,
                $"[ipsw] Профиль: {profile.DisplayName}");

            await ExtractAndUnwrapPatternAsync(
                profile,
                downloadsDirectory,
                $"kernelcache.release.{profile.KernelExtension}",
                Path.Combine(firmwareDirectory, "bootkc"),
                cancellationToken);

            await ExtractAndUnwrapPatternAsync(
                profile,
                downloadsDirectory,
                $"sptm.{profile.ChipName}.release",
                Path.Combine(firmwareDirectory, "sptm"),
                cancellationToken);

            await ExtractAndUnwrapPatternAsync(
                profile,
                downloadsDirectory,
                $"txm.{profile.SystemSdk}.release",
                Path.Combine(firmwareDirectory, "txm"),
                cancellationToken);

            await ExtractAndUnwrapPatternAsync(
                profile,
                downloadsDirectory,
                $"DeviceTree.{profile.BoardName}",
                Path.Combine(firmwareDirectory, "dtree.raw"),
                cancellationToken);

            ProgressChanged?.Invoke(this, "[dtree] Применение qemu-sptm DeviceTree fixups…");
            _deviceTreePatcher.PatchFile(
                Path.Combine(firmwareDirectory, "dtree.raw"),
                Path.Combine(firmwareDirectory, "dtree"),
                _layout.NvramTemplate);
            File.Delete(Path.Combine(firmwareDirectory, "dtree.raw"));
            ProgressChanged?.Invoke(this, "[dtree] DeviceTree готов.");

            await ExtractAndUnwrapRamdiskAsync(
                profile,
                downloadsDirectory,
                Path.Combine(firmwareDirectory, "ramdisk.dmg"),
                Path.Combine(firmwareDirectory, "ramdisk.base.tc"),
                cancellationToken);

            CommitStagedFirmware(firmwareDirectory);

            ProgressChanged?.Invoke(
                this,
                "[ipsw] Firmware извлечён и DeviceTree пропатчен. Следующий этап: ramdisk patch + trust cache.");
        }
        finally
        {
            if (Directory.Exists(stagingRoot))
            {
                Directory.Delete(stagingRoot, recursive: true);
            }
        }
    }

    private async Task ExtractAndUnwrapPatternAsync(
        ProvisioningProfile profile,
        string downloadsDirectory,
        string pattern,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        ProgressChanged?.Invoke(this, $"[ipsw] Извлечение {pattern}…");

        var result = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "extract",
                "--remote", profile.IpswUrl,
                "--output", downloadsDirectory,
                "--flat",
                "--pattern", pattern,
                "-j"
            ],
            _layout.DataDirectory,
            cancellationToken);

        result.EnsureSuccess($"ipsw extract {pattern}");

        var downloadedPath = ParseFirstJsonPath(result.StandardOutput, _layout.DataDirectory);
        await UnwrapIm4pAsync(downloadedPath, destinationPath, cancellationToken);

        ProgressChanged?.Invoke(
            this,
            $"[ipsw] {Path.GetFileName(destinationPath)} готов.");
    }

    private async Task ExtractAndUnwrapRamdiskAsync(
        ProvisioningProfile profile,
        string downloadsDirectory,
        string destinationPath,
        string trustCacheDestinationPath,
        CancellationToken cancellationToken)
    {
        ProgressChanged?.Invoke(this, "[ipsw] Извлечение recovery ramdisk…");

        var result = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "extract",
                "--remote", profile.IpswUrl,
                "--output", downloadsDirectory,
                "--flat",
                "-j",
                "--dmg", "rdisk"
            ],
            _layout.DataDirectory,
            cancellationToken);

        result.EnsureSuccess("ipsw extract recovery ramdisk");

        var downloadedPath = ParseFirstJsonPath(result.StandardOutput, _layout.DataDirectory);
        var ramdiskName = Path.GetFileName(downloadedPath);
        if (!ramdiskName.EndsWith(".dmg", StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidDataException(
                $"Recovery ramdisk имеет неожиданный формат: {ramdiskName}");
        }

        await UnwrapIm4pAsync(downloadedPath, destinationPath, cancellationToken);
        ProgressChanged?.Invoke(this, "[ipsw] ramdisk.dmg готов.");

        var trustCacheName = ramdiskName + ".trustcache";
        ProgressChanged?.Invoke(
            this,
            $"[ipsw] Извлечение штатного recovery trustcache {trustCacheName}…");

        await ExtractAndUnwrapPatternAsync(
            profile,
            downloadsDirectory,
            trustCacheName,
            trustCacheDestinationPath,
            cancellationToken);
    }

    private async Task UnwrapIm4pAsync(
        string sourcePath,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        var result = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "img4",
                "im4p",
                "extract",
                sourcePath,
                "-o",
                destinationPath
            ],
            _layout.DataDirectory,
            cancellationToken);

        result.EnsureSuccess($"ipsw img4 extract {Path.GetFileName(sourcePath)}");

        if (!File.Exists(destinationPath))
        {
            throw new InvalidDataException(
                $"После IMG4 extraction отсутствует {destinationPath}.");
        }
    }

    private static string ParseFirstJsonPath(string json, string workingDirectory)
    {
        using var document = JsonDocument.Parse(json);

        if (document.RootElement.ValueKind != JsonValueKind.Array ||
            document.RootElement.GetArrayLength() == 0)
        {
            throw new InvalidDataException("ipsw не вернул путь к извлечённому файлу.");
        }

        var first = document.RootElement[0];

        if (first.ValueKind != JsonValueKind.String)
        {
            throw new InvalidDataException("Неожиданный JSON-ответ ipsw.");
        }

        var path = first.GetString();
        if (string.IsNullOrWhiteSpace(path))
        {
            throw new InvalidDataException("ipsw вернул пустой путь.");
        }

        var resolvedPath = Path.IsPathRooted(path)
            ? path
            : Path.GetFullPath(path, workingDirectory);

        if (!File.Exists(resolvedPath))
        {
            throw new FileNotFoundException(
                "Файл, указанный ipsw, не найден.",
                resolvedPath);
        }

        return resolvedPath;
    }

    private void CommitStagedFirmware(string stagedFirmwareDirectory)
    {
        foreach (var sourceFile in Directory.EnumerateFiles(stagedFirmwareDirectory))
        {
            var destinationFile = Path.Combine(
                _layout.FirmwareDirectory,
                Path.GetFileName(sourceFile));

            File.Copy(sourceFile, destinationFile, overwrite: true);
        }
    }
}
