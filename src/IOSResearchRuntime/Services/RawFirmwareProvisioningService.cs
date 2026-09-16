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

            await ExtractKernelAsync(
                profile,
                downloadsDirectory,
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

    private async Task ExtractKernelAsync(
        ProvisioningProfile profile,
        string downloadsDirectory,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        var expectedName = $"kernelcache.release.{profile.KernelExtension}";
        ProgressChanged?.Invoke(
            this,
            $"[ipsw] Извлечение BootKC для {profile.DeviceName} через штатный kernel extractor…");

        var result = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "extract",
                "--remote", profile.IpswUrl,
                "--output", downloadsDirectory,
                "--flat",
                "--kernel",
                "--device", profile.DeviceName,
                "-j"
            ],
            _layout.DataDirectory,
            cancellationToken);

        result.EnsureSuccess($"ipsw extract --kernel {profile.DeviceName}");

        var candidates = ParseJsonPaths(result.StandardOutput, _layout.DataDirectory);
        var kernelPath = candidates.FirstOrDefault(path =>
            string.Equals(
                Path.GetFileName(path),
                expectedName,
                StringComparison.OrdinalIgnoreCase));

        kernelPath ??= candidates.FirstOrDefault(path =>
            Path.GetFileName(path).Contains(
                expectedName,
                StringComparison.OrdinalIgnoreCase));

        if (kernelPath is null)
        {
            throw new InvalidDataException(
                $"ipsw kernel extractor не вернул {expectedName}. Получено: " +
                string.Join(", ", candidates.Select(Path.GetFileName)));
        }

        Directory.CreateDirectory(Path.GetDirectoryName(destinationPath)!);
        File.Copy(kernelPath, destinationPath, overwrite: true);

        ProgressChanged?.Invoke(
            this,
            $"[ipsw] BootKC выбран: {Path.GetFileName(kernelPath)} ({new FileInfo(destinationPath).Length:N0} байт).");

        await ValidateBootKernelCollectionAsync(destinationPath, cancellationToken);
        ProgressChanged?.Invoke(this, "[ipsw] bootkc готов и содержит AppleImage4.");
    }

    private async Task ValidateBootKernelCollectionAsync(
        string bootKernelCollectionPath,
        CancellationToken cancellationToken)
    {
        var kexts = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "kernel",
                "kexts",
                bootKernelCollectionPath
            ],
            _layout.DataDirectory,
            cancellationToken);

        kexts.EnsureSuccess("ipsw kernel kexts bootkc");

        var listing = string.Concat(
            kexts.StandardOutput,
            Environment.NewLine,
            kexts.StandardError);

        if (!listing.Contains(
                "com.apple.security.AppleImage4",
                StringComparison.Ordinal))
        {
            throw new InvalidDataException(
                "Извлечённый BootKC не содержит fileset com.apple.security.AppleImage4. " +
                "Такой kernelcache несовместим с текущим qemu-sptm boot path.");
        }

        var version = await _processRunner.RunAsync(
            _layout.IpswExecutable,
            [
                "kernel",
                "version",
                bootKernelCollectionPath
            ],
            _layout.DataDirectory,
            cancellationToken);

        version.EnsureSuccess("ipsw kernel version bootkc");

        var versionLine = version.StandardOutput
            .Split(
                ['\r', '\n'],
                StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .FirstOrDefault();

        if (!string.IsNullOrWhiteSpace(versionLine))
        {
            ProgressChanged?.Invoke(this, $"[ipsw] BootKC: {versionLine}");
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
        return ParseJsonPaths(json, workingDirectory).First();
    }

    private static IReadOnlyList<string> ParseJsonPaths(
        string json,
        string workingDirectory)
    {
        using var document = JsonDocument.Parse(json);
        var rawPaths = new List<string>();

        static void AddString(JsonElement element, List<string> paths)
        {
            if (element.ValueKind != JsonValueKind.String)
            {
                return;
            }

            var value = element.GetString();
            if (!string.IsNullOrWhiteSpace(value))
            {
                paths.Add(value);
            }
        }

        switch (document.RootElement.ValueKind)
        {
            case JsonValueKind.Array:
                foreach (var item in document.RootElement.EnumerateArray())
                {
                    AddString(item, rawPaths);
                }
                break;

            case JsonValueKind.Object:
                foreach (var property in document.RootElement.EnumerateObject())
                {
                    rawPaths.Add(property.Name);
                    AddString(property.Value, rawPaths);
                }
                break;

            case JsonValueKind.String:
                AddString(document.RootElement, rawPaths);
                break;
        }

        var resolved = rawPaths
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .Select(path =>
                Path.IsPathRooted(path)
                    ? path
                    : Path.GetFullPath(path, workingDirectory))
            .Where(File.Exists)
            .ToArray();

        if (resolved.Length == 0)
        {
            throw new InvalidDataException(
                "ipsw не вернул существующих путей к извлечённым файлам.");
        }

        return resolved;
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
