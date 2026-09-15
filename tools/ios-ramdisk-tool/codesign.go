package main

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfs"
)

var primaryCodeDirectoryPattern = regexp.MustCompile(`(?s)slot:\\s+CodeDirectory \\(0\\).*?sha256:\\s+([0-9a-fA-F]{64})`)

type machoSigner struct {
	executable string
}

func newMachoSigner(executable string) (*machoSigner, error) {
	if executable == "" {
		return nil, fmt.Errorf("--rcodesign is required")
	}
	if _, err := os.Stat(executable); err != nil {
		return nil, fmt.Errorf("rcodesign executable: %w", err)
	}
	return &machoSigner{executable: executable}, nil
}

func (s *machoSigner) Sign(data []byte) ([]byte, string, error) {
	if !isMachO(data) {
		return nil, "", fmt.Errorf("refusing to sign non-Mach-O data")
	}

	input, err := writeTempData("ios-rr-sign-input-*", data)
	if err != nil {
		return nil, "", err
	}
	defer os.Remove(input)

	outputFile, err := os.CreateTemp("", "ios-rr-sign-output-*")
	if err != nil {
		return nil, "", err
	}
	output := outputFile.Name()
	if err := outputFile.Close(); err != nil {
		return nil, "", err
	}
	if err := os.Remove(output); err != nil {
		return nil, "", err
	}
	defer os.Remove(output)

	command := exec.Command(s.executable, "sign", "-C", "/dev/null", input, output)
	if combined, err := command.CombinedOutput(); err != nil {
		return nil, "", fmt.Errorf("rcodesign sign: %w: %s", err, strings.TrimSpace(string(combined)))
	}

	signed, err := os.ReadFile(output)
	if err != nil {
		return nil, "", fmt.Errorf("read signed Mach-O: %w", err)
	}

	hash, ok, err := s.CDHashFile(output)
	if err != nil {
		return nil, "", err
	}
	if !ok {
		return nil, "", fmt.Errorf("signed Mach-O has no primary CodeDirectory")
	}

	return signed, hash, nil
}

func (s *machoSigner) CDHash(data []byte) (string, bool, error) {
	if !isMachO(data) {
		return "", false, nil
	}

	temp, err := writeTempData("ios-rr-cdhash-*", data)
	if err != nil {
		return "", false, err
	}
	defer os.Remove(temp)

	return s.CDHashFile(temp)
}

func (s *machoSigner) CDHashFile(filePath string) (string, bool, error) {
	command := exec.Command(s.executable, "print-signature-info", "-C", "/dev/null", filePath)
	combined, err := command.CombinedOutput()
	if err != nil {
		// Existing ramdisk files can legitimately be unsigned.
		return "", false, nil
	}

	match := primaryCodeDirectoryPattern.FindSubmatch(combined)
	if len(match) != 2 {
		return "", false, nil
	}

	sha256 := strings.ToLower(string(match[1]))
	return sha256[:40], true, nil
}

func collectVolumeCDHashes(volume *apfs.Volume, signer *machoSigner) (map[string]struct{}, error) {
	hashes := make(map[string]struct{})
	if err := collectDirectoryCDHashes(volume, ".", signer, hashes); err != nil {
		return nil, err
	}
	return hashes, nil
}

func collectDirectoryCDHashes(
	volume *apfs.Volume,
	directory string,
	signer *machoSigner,
	hashes map[string]struct{},
) error {
	entries, err := volume.ReadDir(directory)
	if err != nil {
		return err
	}

	for _, directoryEntry := range entries {
		name := directoryEntry.Name()
		fullPath := name
		if directory != "." {
			fullPath = directory + "/" + name
		}

		info, err := directoryEntry.Info()
		if err != nil {
			return fmt.Errorf("%s: info: %w", fullPath, err)
		}

		switch {
		case info.Mode().IsDir():
			if err := collectDirectoryCDHashes(volume, fullPath, signer, hashes); err != nil {
				return err
			}
		case info.Mode().IsRegular():
			data, isMacho, err := readMachOFile(volume, fullPath)
			if err != nil {
				return fmt.Errorf("%s: inspect for cdhash: %w", fullPath, err)
			}
			if !isMacho {
				continue
			}

			hash, ok, err := signer.CDHash(data)
			if err != nil {
				return fmt.Errorf("%s: cdhash: %w", fullPath, err)
			}
			if ok {
				hashes[hash] = struct{}{}
			}
		}
	}

	return nil
}

func readMachOFile(volume *apfs.Volume, filePath string) ([]byte, bool, error) {
	file, err := volume.Open(filePath)
	if err != nil {
		return nil, false, err
	}
	defer file.Close()

	magic := make([]byte, 4)
	n, err := file.Read(magic)
	if err != nil && err != io.EOF {
		return nil, false, err
	}
	if n < len(magic) || !isMachO(magic) {
		return nil, false, nil
	}

	data, err := volume.ReadFile(filePath)
	if err != nil {
		return nil, false, err
	}
	return data, true, nil
}

func writeCDHashes(filePath string, hashes map[string]struct{}) error {
	values := make([]string, 0, len(hashes))
	for hash := range hashes {
		values = append(values, hash)
	}
	sort.Strings(values)

	var buffer bytes.Buffer
	for _, hash := range values {
		buffer.WriteString(hash)
		buffer.WriteByte('\n')
	}

	if err := os.MkdirAll(filepath.Dir(filePath), 0o755); err != nil {
		return err
	}
	return os.WriteFile(filePath, buffer.Bytes(), 0o644)
}

func writeTempData(pattern string, data []byte) (string, error) {
	file, err := os.CreateTemp("", pattern)
	if err != nil {
		return "", err
	}
	path := file.Name()

	if _, err := file.Write(data); err != nil {
		file.Close()
		os.Remove(path)
		return "", err
	}
	if err := file.Close(); err != nil {
		os.Remove(path)
		return "", err
	}

	return path, nil
}

func isMachO(data []byte) bool {
	if len(data) < 4 {
		return false
	}

	magic := data[:4]
	return bytes.Equal(magic, []byte{0xcf, 0xfa, 0xed, 0xfe}) ||
		bytes.Equal(magic, []byte{0xfe, 0xed, 0xfa, 0xcf}) ||
		bytes.Equal(magic, []byte{0xca, 0xfe, 0xba, 0xbe}) ||
		bytes.Equal(magic, []byte{0xbe, 0xba, 0xfe, 0xca})
}
