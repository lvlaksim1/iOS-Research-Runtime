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

            if (!string.IsNullOrWhiteSpace(result.StandardOutput))
            {
                ProgressChanged?.Invoke(this, $"[ios-ramdisk-tool stdout] {result.StandardOutput.Trim()}");
            }

            if (!string.IsNullOrWhiteSpace(result.StandardError))
            {
                ProgressChanged?.Invoke(this, $"[ios-ramdisk-tool stderr] {result.StandardError.Trim()}");
            }

            result.EnsureSuccess("ios-ramdisk-tool");

            var sourceSignedExecutables = ParseSourceSignedExecutableDiagnostics(result.StandardOutput);

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

            var sourceRamdiskBytes = new FileInfo(sourceRamdisk).Length;
            var patchedRamdiskBytes = new FileInfo(patchedRamdisk).Length;
            ProgressChanged?.Invoke(
                this,
                $"[ramdisk-packaging] source_dmg_bytes={sourceRamdiskBytes} patched_dmg_bytes={patchedRamdiskBytes}");

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

            var baseTrustCacheBytes = File.ReadAllBytes(baseTrustCache);
            var injectedHashes = File.ReadLines(hashList)
                .Where(line => !string.IsNullOrWhiteSpace(line))
                .ToArray();

            foreach (var path in new[] { "/bin/cat", "/usr/libexec/xpcproxy" })
            {
                if (!sourceSignedExecutables.TryGetValue(path, out var cdHash))
                {
                    ProgressChanged?.Invoke(
                        this,
                        $"[trustcache-membership] path={path} primary_cdhash=UNAVAILABLE base=UNAVAILABLE injected=UNAVAILABLE merged=UNAVAILABLE");
                    continue;
                }

                var membership = _trustCacheBuilder.ClassifyMembership(
                    baseTrustCacheBytes,
                    injectedHashes,
                    cdHash);
                ProgressChanged?.Invoke(
                    this,
                    $"[trustcache-membership] path={path} primary_cdhash={cdHash} base={membership.Base} injected={membership.Injected} merged={membership.Merged}");
            }

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

    private static IReadOnlyDictionary<string, string> ParseSourceSignedExecutableDiagnostics(string? standardOutput)
    {
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        if (string.IsNullOrWhiteSpace(standardOutput))
        {
            return result;
        }

        foreach (var line in standardOutput.Split('\n', StringSplitOptions.RemoveEmptyEntries))
        {
            var trimmed = line.Trim();
            if (!trimmed.StartsWith("source-signed-exec ", StringComparison.Ordinal))
            {
                continue;
            }

            var fields = trimmed.Split(' ', StringSplitOptions.RemoveEmptyEntries)
                .Skip(1)
                .Select(part => part.Split('=', 2))
                .Where(parts => parts.Length == 2)
                .ToDictionary(parts => parts[0], parts => parts[1], StringComparer.Ordinal);

            if (fields.TryGetValue("path", out var path) &&
                fields.TryGetValue("cdhash_ok", out var cdHashOk) &&
                string.Equals(cdHashOk, "true", StringComparison.OrdinalIgnoreCase) &&
                fields.TryGetValue("primary_cdhash", out var cdHash) &&
                !string.IsNullOrWhiteSpace(cdHash))
            {
                result[path] = cdHash;
            }
        }

        return result;
    }

    private static void RequireFile(string path, string message)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException(message, path);
        }
    }
}
