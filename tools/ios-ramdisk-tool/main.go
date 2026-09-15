package main

import (
	"archive/tar"
	"compress/gzip"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfs"
	"github.com/deploymenttheory/go-apfs-v2/pkg/apfswrite"
	"github.com/deploymenttheory/go-apfs-v2/pkg/disk"
)

const symlinkXattrName = "com.apple.fs.symlink"

type options struct {
	input        string
	output       string
	sysrootTar   string
	launchdPlist string
	rcodesign    string
	hashesOut    string
}

func main() {
	var opts options

	flag.StringVar(&opts.input, "input", "", "source recovery ramdisk DMG")
	flag.StringVar(&opts.output, "output", "", "patched recovery ramdisk DMG")
	flag.StringVar(&opts.sysrootTar, "sysroot-tar", "", "iOS CLI sysroot tar.gz")
	flag.StringVar(&opts.launchdPlist, "launchd-plist", "", "launch daemon plist")
	flag.StringVar(&opts.rcodesign, "rcodesign", "", "path to rcodesign.exe")
	flag.StringVar(&opts.hashesOut, "hashes-out", "", "output file for collected CDHashes")
	flag.Parse()

	if err := run(opts); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func run(opts options) error {
	if opts.input == "" || opts.output == "" || opts.sysrootTar == "" || opts.launchdPlist == "" ||
		opts.rcodesign == "" || opts.hashesOut == "" {
		return errors.New("--input, --output, --sysroot-tar, --launchd-plist, --rcodesign and --hashes-out are required")
	}

	container, closer, err := apfs.OpenImage(opts.input, nil)
	if err != nil {
		return fmt.Errorf("open APFS ramdisk: %w", err)
	}
	defer closer.Close()

	volume, err := container.VolumeBySelector("0")
	if err != nil {
		return fmt.Errorf("open first APFS volume: %w", err)
	}

	signer, err := newMachoSigner(opts.rcodesign)
	if err != nil {
		return err
	}

	fmt.Println("collecting existing Mach-O CDHashes...")
	hashes, err := collectVolumeCDHashes(volume, signer)
	if err != nil {
		return fmt.Errorf("collect existing CDHashes: %w", err)
	}
	fmt.Printf("collected %d existing CDHashes\n", len(hashes))

	children, err := readDirectory(volume, ".")
	if err != nil {
		return fmt.Errorf("read APFS tree: %w", err)
	}

	root := &apfswrite.Entry{
		Mode:     fs.ModeDir | 0o755,
		UID:      0,
		GID:      0,
		Children: children,
	}

	launchdBytes, err := os.ReadFile(opts.launchdPlist)
	if err != nil {
		return fmt.Errorf("read launchd plist: %w", err)
	}

	if err := replaceLaunchDaemons(root, launchdBytes); err != nil {
		return err
	}

	if err := mergeSysrootTarWithSigner(root, opts.sysrootTar, signer, hashes); err != nil {
		return fmt.Errorf("merge sysroot: %w", err)
	}

	volumeName, err := volume.UTF8Name()
	if err != nil {
		return fmt.Errorf("read volume name: %w", err)
	}

	volumeUUID, err := volume.Identifier()
	if err != nil {
		return fmt.Errorf("read volume UUID: %w", err)
	}

	containerID, err := container.Identifier()
	if err != nil {
		return fmt.Errorf("read container UUID: %w", err)
	}
	if len(containerID) != 16 {
		return fmt.Errorf("unexpected container UUID length: %d", len(containerID))
	}
	var containerUUID [16]byte
	copy(containerUUID[:], containerID)

	role, err := volume.Role()
	if err != nil {
		return fmt.Errorf("read volume role: %w", err)
	}

	caseInsensitive, err := volume.IsCaseInsensitive()
	if err != nil {
		return fmt.Errorf("read case-sensitivity: %w", err)
	}

	groupID, err := volume.VolumeGroupIdentifier()
	if err != nil {
		return fmt.Errorf("read volume group: %w", err)
	}

	if groupID != ([16]byte{}) && role != apfs.VolumeRoleSystem {
		return errors.New("source volume has unsupported volume-group metadata")
	}

	rawFile, err := os.CreateTemp(filepath.Dir(opts.output), ".ios-ramdisk-*.raw")
	if err != nil {
		return fmt.Errorf("create raw APFS staging image: %w", err)
	}
	rawPath := rawFile.Name()
	defer func() {
		rawFile.Close()
		_ = os.Remove(rawPath)
	}()

	createOpts := &apfswrite.CreateOptions{
		VolumeName:    volumeName,
		CaseSensitive: !caseInsensitive,
		ContainerUUID: containerUUID,
		VolumeUUID:    volumeUUID,
		Role:          role,
		VolumeGroupID: groupID,
		Root:          root,
	}

	if err := apfswrite.CreateContainer(rawFile, 0, createOpts); err != nil {
		return fmt.Errorf("create patched APFS container: %w", err)
	}

	if err := rawFile.Sync(); err != nil {
		return fmt.Errorf("flush patched APFS container: %w", err)
	}

	stat, err := rawFile.Stat()
	if err != nil {
		return fmt.Errorf("stat patched APFS container: %w", err)
	}

	if err := disk.WrapRawImageDMGFrom(opts.output, rawFile, stat.Size(), "Apple_APFS", nil); err != nil {
		return fmt.Errorf("wrap patched APFS container in DMG: %w", err)
	}

	if err := writeCDHashes(opts.hashesOut, hashes); err != nil {
		return fmt.Errorf("write CDHashes: %w", err)
	}

	fmt.Printf("patched ramdisk: %s -> %s\n", opts.input, opts.output)
	fmt.Printf("trust-cache hashes: %s (%d entries)\n", opts.hashesOut, len(hashes))
	return nil
}

func readDirectory(volume *apfs.Volume, directory string) ([]*apfswrite.Entry, error) {
	entries, err := volume.ReadDir(directory)
	if err != nil {
		return nil, err
	}

	result := make([]*apfswrite.Entry, 0, len(entries))

	for _, directoryEntry := range entries {
		name := directoryEntry.Name()
		fullPath := name
		if directory != "." {
			fullPath = directory + "/" + name
		}

		info, err := directoryEntry.Info()
		if err != nil {
			return nil, fmt.Errorf("%s: info: %w", fullPath, err)
		}

		entry := &apfswrite.Entry{
			Name:    name,
			Mode:    info.Mode(),
			ModTime: info.ModTime(),
		}

		var inode *apfs.Inode
		if value, ok := info.Sys().(*apfs.Inode); ok {
			inode = value
			entry.UID = value.OwnerIdentifier
			entry.GID = value.GroupIdentifier
			if info.Mode().IsRegular() && value.NumberOfLinks > 1 {
				entry.LinkGroup = value.Identifier
			}
		}

		xattrs, err := volume.Xattrs(fullPath)
		if err == nil && len(xattrs) > 0 {
			entry.Xattrs = cloneXattrs(xattrs)
			delete(entry.Xattrs, symlinkXattrName)
			if len(entry.Xattrs) == 0 {
				entry.Xattrs = nil
			}
		}

		switch {
		case info.Mode()&fs.ModeSymlink != 0:
			target, err := volume.Readlink(fullPath)
			if err != nil {
				return nil, fmt.Errorf("%s: read symlink: %w", fullPath, err)
			}
			entry.Data = []byte(target)

		case info.Mode().IsDir():
			children, err := readDirectory(volume, fullPath)
			if err != nil {
				return nil, err
			}
			entry.Children = children

		case info.Mode().IsRegular():
			if inode != nil && inode.BSDFlags&apfs.BSDFlagCompressed != 0 {
				// The writer reconstructs transparently-compressed content from
				// com.apple.decmpfs (+ resource fork when present).
				entry.Data = nil
			} else {
				data, err := volume.ReadFile(fullPath)
				if err != nil {
					return nil, fmt.Errorf("%s: read file: %w", fullPath, err)
				}
				entry.Data = data
			}

		default:
			return nil, fmt.Errorf("%s: unsupported special file mode %v", fullPath, info.Mode())
		}

		result = append(result, entry)
	}

	return result, nil
}

func cloneXattrs(source map[string][]byte) map[string][]byte {
	result := make(map[string][]byte, len(source))
	for name, value := range source {
		result[name] = append([]byte(nil), value...)
	}
	return result
}

func replaceLaunchDaemons(root *apfswrite.Entry, plist []byte) error {
	system, err := findChild(root, "System")
	if err != nil {
		return err
	}
	library, err := findChild(system, "Library")
	if err != nil {
		return err
	}

	old, err := findChild(library, "LaunchDaemons")
	if err != nil {
		return err
	}

	if _, err := findChild(library, "LaunchDaemons.old"); err == nil {
		return errors.New("ramdisk already contains System/Library/LaunchDaemons.old")
	}

	old.Name = "LaunchDaemons.old"

	library.Children = append(library.Children, &apfswrite.Entry{
		Name: "LaunchDaemons",
		Mode: fs.ModeDir | 0o755,
		UID:  0,
		GID:  0,
		Children: []*apfswrite.Entry{
			{
				Name: "com.jprx.bash.plist",
				Mode: 0o644,
				UID:  0,
				GID:  0,
				Data: append([]byte(nil), plist...),
			},
		},
	})

	return nil
}

func mergeSysrootTar(root *apfswrite.Entry, archivePath string) error {
	return mergeSysrootTarWithSigner(root, archivePath, nil, nil)
}

func mergeSysrootTarWithSigner(
	root *apfswrite.Entry,
	archivePath string,
	signer *machoSigner,
	hashes map[string]struct{},
) error {
	file, err := os.Open(archivePath)
	if err != nil {
		return err
	}
	defer file.Close()

	gzipReader, err := gzip.NewReader(file)
	if err != nil {
		return err
	}
	defer gzipReader.Close()

	reader := tar.NewReader(gzipReader)
	linkGroups := map[string]uint64{}
	var nextLinkGroup uint64 = 1

	for {
		header, err := reader.Next()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			return err
		}

		relative, ok := stripFirstPathComponent(header.Name)
		if !ok || relative == "" {
			continue
		}

		cleaned := path.Clean(relative)
		if cleaned == "." || strings.HasPrefix(cleaned, "../") || path.IsAbs(cleaned) {
			return fmt.Errorf("unsafe tar path: %q", header.Name)
		}

		mode := fs.FileMode(header.Mode & 0o7777)

		switch header.Typeflag {
		case tar.TypeDir:
			_, err = ensureDirectory(root, cleaned, mode)

		case tar.TypeReg, tar.TypeRegA:
			data, readErr := io.ReadAll(reader)
			if readErr != nil {
				return fmt.Errorf("%s: read tar file: %w", cleaned, readErr)
			}

			if signer != nil && isMachO(data) {
				if strings.HasPrefix(cleaned, "bin/") {
					signed, hash, signErr := signer.Sign(data)
					if signErr != nil {
						return fmt.Errorf("%s: sign: %w", cleaned, signErr)
					}
					data = signed
					if hashes != nil {
						hashes[hash] = struct{}{}
					}
				} else {
					hash, ok, hashErr := signer.CDHash(data)
					if hashErr != nil {
						return fmt.Errorf("%s: cdhash: %w", cleaned, hashErr)
					}
					if ok && hashes != nil {
						hashes[hash] = struct{}{}
					}
				}
			}

			err = putRegularFile(root, cleaned, mode, data, 0)

		case tar.TypeSymlink:
			err = putSymlink(root, cleaned, mode, header.Linkname)

		case tar.TypeLink:
			target, targetOK := stripFirstPathComponent(header.Linkname)
			if !targetOK {
				return fmt.Errorf("%s: invalid hard-link target %q", cleaned, header.Linkname)
			}
			group, exists := linkGroups[target]
			if !exists {
				group = nextLinkGroup
				nextLinkGroup++
				linkGroups[target] = group
				if targetEntry, findErr := findPath(root, target); findErr == nil {
					targetEntry.LinkGroup = group
				}
			}
			targetEntry, findErr := findPath(root, target)
			if findErr != nil {
				return fmt.Errorf("%s: hard-link target %s not present: %w", cleaned, target, findErr)
			}
			err = putRegularFile(root, cleaned, mode, append([]byte(nil), targetEntry.Data...), group)

		default:
			// Device nodes and other special entries aren't needed by ios-cli-tools.
			continue
		}

		if err != nil {
			return fmt.Errorf("%s: %w", cleaned, err)
		}
	}

	return nil
}

func stripFirstPathComponent(value string) (string, bool) {
	cleaned := path.Clean(strings.ReplaceAll(value, "\\", "/"))
	cleaned = strings.TrimPrefix(cleaned, "./")
	parts := strings.Split(cleaned, "/")
	if len(parts) < 2 {
		return "", false
	}
	return strings.Join(parts[1:], "/"), true
}

func ensureDirectory(root *apfswrite.Entry, relative string, mode fs.FileMode) (*apfswrite.Entry, error) {
	parts := splitPath(relative)
	current := root

	for _, part := range parts {
		child := findChildOrNil(current, part)
		if child == nil {
			child = &apfswrite.Entry{
				Name: part,
				Mode: fs.ModeDir | 0o755,
				UID:  0,
				GID:  0,
			}
			current.Children = append(current.Children, child)
		} else if !isDirectory(child) {
			return nil, fmt.Errorf("%s exists and is not a directory", part)
		}
		current = child
	}

	if mode.Perm() != 0 {
		current.Mode = fs.ModeDir | mode.Perm()
	}
	current.UID = 0
	current.GID = 0
	return current, nil
}

func putRegularFile(root *apfswrite.Entry, relative string, mode fs.FileMode, data []byte, linkGroup uint64) error {
	parent, name, err := ensureParent(root, relative)
	if err != nil {
		return err
	}

	removeChild(parent, name)
	parent.Children = append(parent.Children, &apfswrite.Entry{
		Name:      name,
		Mode:      mode.Perm(),
		UID:       0,
		GID:       0,
		Data:      data,
		LinkGroup: linkGroup,
	})
	return nil
}

func putSymlink(root *apfswrite.Entry, relative string, mode fs.FileMode, target string) error {
	parent, name, err := ensureParent(root, relative)
	if err != nil {
		return err
	}

	removeChild(parent, name)
	parent.Children = append(parent.Children, &apfswrite.Entry{
		Name: name,
		Mode: fs.ModeSymlink | mode.Perm(),
		UID:  0,
		GID:  0,
		Data: []byte(target),
	})
	return nil
}

func ensureParent(root *apfswrite.Entry, relative string) (*apfswrite.Entry, string, error) {
	parts := splitPath(relative)
	if len(parts) == 0 {
		return nil, "", errors.New("empty path")
	}
	name := parts[len(parts)-1]
	if len(parts) == 1 {
		return root, name, nil
	}

	parent, err := ensureDirectory(root, strings.Join(parts[:len(parts)-1], "/"), 0o755)
	return parent, name, err
}

func findPath(root *apfswrite.Entry, relative string) (*apfswrite.Entry, error) {
	current := root
	for _, part := range splitPath(relative) {
		next := findChildOrNil(current, part)
		if next == nil {
			return nil, fmt.Errorf("path not found: %s", relative)
		}
		current = next
	}
	return current, nil
}

func findChild(parent *apfswrite.Entry, name string) (*apfswrite.Entry, error) {
	child := findChildOrNil(parent, name)
	if child == nil {
		return nil, fmt.Errorf("child not found: %s", name)
	}
	return child, nil
}

func findChildOrNil(parent *apfswrite.Entry, name string) *apfswrite.Entry {
	for _, child := range parent.Children {
		if child.Name == name {
			return child
		}
	}
	return nil
}

func removeChild(parent *apfswrite.Entry, name string) {
	filtered := parent.Children[:0]
	for _, child := range parent.Children {
		if child.Name != name {
			filtered = append(filtered, child)
		}
	}
	parent.Children = filtered
}

func isDirectory(entry *apfswrite.Entry) bool {
	return entry.Mode.IsDir() || (entry.Mode == 0 && entry.Children != nil)
}

func splitPath(value string) []string {
	cleaned := path.Clean(strings.ReplaceAll(value, "\\", "/"))
	if cleaned == "." || cleaned == "" {
		return nil
	}
	return strings.Split(cleaned, "/")
}
