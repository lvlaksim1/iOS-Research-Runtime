namespace IOSResearchRuntime.Services;

public sealed class RamdiskProvisioningService
{
    private readonly RuntimeLayout _layout;
    private readonly ExternalProcessRunner _processRunner;
    private readonly TrustCacheBuilder _trustCacheBuilder;

    public RamdiskProvisioningService(
        RuntimeLayout layout,
        ExternalProcessRunner processRunner,
        TrustCacheBuilder trustCacheBuilder)
    {
        _layout = layout;
        _processRunner = processRunner;
        _trustCacheBuilder = trustCacheBuilder;
    }

    public event EventHandler<string>? ProgressChanged;

    public async Task PrepareAsync(CancellationToken cancellationToken = default)
    {
        _layout.EnsureDirectories();

        var sourceRamdisk = Path.Combine(_layout.FirmwareDirectory, "ramdisk.dmg");
        var baseTrustCache = Path.Combine(_layout.FirmwareDirectory, "ramdisk.base.tc");
        RequireFile(sourceRamdisk, "Исходный recovery ramdisk не подготовлен.");
        RequireFile(baseTrustCache, "Штатный recovery trustcache не подготовлен.");
        RequireFile(_layout.RamdiskToolExecutable, "Не найден встроенный ios-ramdisk-tool.exe.");
        RequireFile(_layout.RcodesignExecutable, "rcodesign.exe не установлен.");
        RequireFile(_layout.IosCliToolsArchive, "iOS CLI runtime resource не подготовлен.");
        RequireFile(_layout.LaunchdPlist, "Не найден launchd plist для root shell.");

        var stagingDirectory = Path.Combine(
            _layout.CacheDirectory,
            $"ramdisk-{Guid.NewGuid():N}");
        Directory.CreateDirectory(stagingDirectory);

        var patchedRamdisk = Path.Combine(stagingDirectory, "ramdisk.dmg");
        var hashList = Path.Combine(stagingDirectory, "all_hashes");
        var trustCache = Path.Combine(stagingDirectory, "ramdisk.tc");
        var apfsEvidence = Path.Combine(_layout.LogDirectory, "apfs-structural-evidence.json");

        try
        {
            ProgressChanged?.Invoke(
                this,
                "[ramdisk] APFS rebuild, Mach-O signing и сбор CDHash…");

            var result = await _processRunner.RunAsync(
                _layout.RamdiskToolExecutable,
                [
                    "--input", sourceRamdisk,
                    "--output", patchedRamdisk,
                    "--sysroot-tar", _layout.IosCliToolsArchive,
                    "--launchd-plist", _layout.LaunchdPlist,
                    "--rcodesign", _layout.RcodesignExecutable,
                    "--hashes-out", hashList,
                    "--nx-evidence-out", apfsEvidence
                ],
                _layout.DataDirectory,
                cancellationToken);

            result.EnsureSuccess("ios-ramdisk-tool");

            if (!File.Exists(patchedRamdisk))
            {
                throw new InvalidDataException(
                    "ios-ramdisk-tool не создал patched ramdisk.");
            }

            if (!File.Exists(hashList))
            {
                throw new InvalidDataException(
                    "ios-ramdisk-tool не создал список CDHash.");
            }

            if (!File.Exists(apfsEvidence) || new FileInfo(apfsEvidence).Length == 0)
            {
                throw new InvalidDataException(
                    "ios-ramdisk-tool не создал APFS structural evidence.");
            }

            ProgressChanged?.Invoke(
                this,
                $"[apfs-evidence] APFS_STRUCTURAL_EVIDENCE={apfsEvidence}");

            var hashCount = File.ReadLines(hashList)
                .Count(line => !string.IsNullOrWhiteSpace(line));

            if (hashCount == 0)
            {
                throw new InvalidDataException(
                    "Список CDHash пуст; trust cache не может быть создан.");
            }

            ProgressChanged?.Invoke(
                this,
                $"[trustcache] Объединение Apple recovery trustcache с {hashCount} новыми CDHash…");

            var merge = _trustCacheBuilder.MergeFile(
                baseTrustCache,
                hashList,
                trustCache);

            ProgressChanged?.Invoke(
                this,
                $"[trustcache] v{merge.Version}: Apple {merge.BaseEntries}, добавлено {merge.AddedEntries}, всего {merge.TotalEntries}.");

            if (!File.Exists(trustCache) || new FileInfo(trustCache).Length == 0)
            {
                throw new InvalidDataException("ramdisk.tc не был создан.");
            }

            CommitPair(
                patchedRamdisk,
                Path.Combine(_layout.FirmwareDirectory, "ramdisk.dmg"),
                trustCache,
                Path.Combine(_layout.FirmwareDirectory, "ramdisk.tc"));

            ProgressChanged?.Invoke(
                this,
                $"[ramdisk] Готово: patched ramdisk + объединённый trust cache.");
        }
        finally
        {
            if (Directory.Exists(stagingDirectory))
            {
                Directory.Delete(stagingDirectory, recursive: true);
            }
        }
    }

    private static void CommitPair(
        string firstSource,
        string firstDestination,
        string secondSource,
        string secondDestination)
    {
        var firstBackup = firstDestination + ".previous";
        var secondBackup = secondDestination + ".previous";

        File.Delete(firstBackup);
        File.Delete(secondBackup);

        if (File.Exists(firstDestination))
        {
            File.Copy(firstDestination, firstBackup, overwrite: true);
        }

        if (File.Exists(secondDestination))
        {
            File.Copy(secondDestination, secondBackup, overwrite: true);
        }

        try
        {
            File.Copy(firstSource, firstDestination, overwrite: true);
            File.Copy(secondSource, secondDestination, overwrite: true);
        }
        catch
        {
            if (File.Exists(firstBackup))
            {
                File.Copy(firstBackup, firstDestination, overwrite: true);
            }

            if (File.Exists(secondBackup))
            {
                File.Copy(secondBackup, secondDestination, overwrite: true);
            }
            else
            {
                File.Delete(secondDestination);
            }

            throw;
        }
        finally
        {
            File.Delete(firstBackup);
            File.Delete(secondBackup);
        }
    }

    private static void RequireFile(string path, string message)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException(message, path);
        }
    }
}
