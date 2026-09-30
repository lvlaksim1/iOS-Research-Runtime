package main

import (
	"archive/tar"
	"compress/gzip"
	"encoding/binary"
	"io/fs"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfswrite"
)

func TestSourceRecoveryExecutableInventoryDeterministic(t *testing.T) {
	root := &apfswrite.Entry{Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{
		{Name: "usr", Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{{Name: "ztool", Mode: 0o755, Data: []byte{0xcf, 0xfa, 0xed, 0xfe}, Xattrs: map[string][]byte{"z": {1, 2}, "a": {3}}}}},
		{Name: "bin", Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{
			{Name: "data", Mode: 0o644, Data: []byte("x")},
			{Name: "sh", Mode: 0o755, Data: []byte("#!/bin/sh\n")},
		}},
	}}
	got := sourceRecoveryExecutableInventory(root)
	want := []string{
		"source-exec path=/bin/sh mode=0755 macho=false size=10 decmpfs_type=none xattrs=[]",
		"source-exec path=/usr/ztool mode=0755 macho=true size=4 decmpfs_type=none xattrs=[a:1,z:2]",
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("inventory = %#v, want %#v", got, want)
	}
}

func TestSourceRecoveryExecutableInventoryReportsDecmpfsType(t *testing.T) {
	attr := make([]byte, 16)
	copy(attr[:4], []byte("fpmc"))
	binary.LittleEndian.PutUint32(attr[4:8], 11)
	root := &apfswrite.Entry{Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{{Name: "bin", Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{{Name: "cat", Mode: 0o755, Xattrs: map[string][]byte{"com.apple.decmpfs": attr}}}}}}
	got := sourceRecoveryExecutableInventory(root)
	want := []string{"source-exec path=/bin/cat mode=0755 macho=false size=0 decmpfs_type=11 xattrs=[com.apple.decmpfs:16]"}
	if !reflect.DeepEqual(got, want) { t.Fatalf("inventory = %#v, want %#v", got, want) }
}

func TestStripFirstPathComponent(t *testing.T) {
	got, ok := stripFirstPathComponent("./prebuilt/bin/bash")
	if !ok || got != "bin/bash" {
		t.Fatalf("got %q, %v", got, ok)
	}
}

func TestReplaceLaunchDaemons(t *testing.T) {
	root := &apfswrite.Entry{Mode: fs.ModeDir | 0o755}
	system := &apfswrite.Entry{Name: "System", Mode: fs.ModeDir | 0o755}
	library := &apfswrite.Entry{Name: "Library", Mode: fs.ModeDir | 0o755}
	launchDaemons := &apfswrite.Entry{Name: "LaunchDaemons", Mode: fs.ModeDir | 0o755}
	root.Children = []*apfswrite.Entry{system}
	system.Children = []*apfswrite.Entry{library}
	library.Children = []*apfswrite.Entry{launchDaemons}

	if err := replaceLaunchDaemons(root, []byte("plist")); err != nil {
		t.Fatal(err)
	}

	if findChildOrNil(library, "LaunchDaemons.old") == nil {
		t.Fatal("LaunchDaemons.old not created")
	}

	current := findChildOrNil(library, "LaunchDaemons")
	if current == nil || len(current.Children) != 1 {
		t.Fatal("new LaunchDaemons not created")
	}
	if current.Children[0].UID != 0 || current.Children[0].GID != 0 {
		t.Fatal("plist ownership is not root:wheel numeric 0:0")
	}
}

func TestMergeSysrootTarAssignsRootOwnershipAndMode(t *testing.T) {
	dir := t.TempDir()
	archive := filepath.Join(dir, "sysroot.tar.gz")
	file, err := os.Create(archive)
	if err != nil {
		t.Fatal(err)
	}
	gz := gzip.NewWriter(file)
	tw := tar.NewWriter(gz)

	payload := []byte("#!/bin/sh\n")
	if err := tw.WriteHeader(&tar.Header{
		Name:     "prebuilt/bin/bash",
		Mode:     0o755,
		Size:     int64(len(payload)),
		Typeflag: tar.TypeReg,
	}); err != nil {
		t.Fatal(err)
	}
	if _, err := tw.Write(payload); err != nil {
		t.Fatal(err)
	}
	if err := tw.Close(); err != nil {
		t.Fatal(err)
	}
	if err := gz.Close(); err != nil {
		t.Fatal(err)
	}
	if err := file.Close(); err != nil {
		t.Fatal(err)
	}

	root := &apfswrite.Entry{Mode: fs.ModeDir | 0o755}
	if err := mergeSysrootTar(root, archive); err != nil {
		t.Fatal(err)
	}

	bash, err := findPath(root, "bin/bash")
	if err != nil {
		t.Fatal(err)
	}
	if bash.UID != 0 || bash.GID != 0 {
		t.Fatalf("ownership = %d:%d", bash.UID, bash.GID)
	}
	if bash.Mode.Perm() != 0o755 {
		t.Fatalf("mode = %o", bash.Mode.Perm())
	}
}

func TestMaterializeRawDecmpfsType9(t *testing.T) {
	payload := []byte("hello")
	attr := make([]byte, 17+len(payload))
	copy(attr[:4], []byte("fpmc"))
	binary.LittleEndian.PutUint32(attr[4:8], 9)
	binary.LittleEndian.PutUint64(attr[8:16], uint64(len(payload)))
	attr[16] = 0xCC
	copy(attr[17:], payload)

	got, materialized, err := materializeRawDecmpfs(
		map[string][]byte{"com.apple.decmpfs": attr})
	if err != nil {
		t.Fatal(err)
	}
	if !materialized {
		t.Fatal("type 9 was not materialized")
	}
	if string(got) != string(payload) {
		t.Fatalf("payload = %q, want %q", got, payload)
	}
}

func TestMaterializeRawDecmpfsType10(t *testing.T) {
	payload := []byte("rawfork")
	attr := make([]byte, 16)
	copy(attr[:4], []byte("fpmc"))
	binary.LittleEndian.PutUint32(attr[4:8], 10)
	binary.LittleEndian.PutUint64(attr[8:16], uint64(len(payload)))

	fork := make([]byte, 8+len(payload))
	binary.LittleEndian.PutUint32(fork[:4], 8)
	binary.LittleEndian.PutUint32(fork[4:8], uint32(8+len(payload)))
	copy(fork[8:], payload)

	got, materialized, err := materializeRawDecmpfs(map[string][]byte{
		"com.apple.decmpfs":      attr,
		"com.apple.ResourceFork": fork,
	})
	if err != nil {
		t.Fatal(err)
	}
	if !materialized {
		t.Fatal("type 10 was not materialized")
	}
	if string(got) != string(payload) {
		t.Fatalf("payload = %q, want %q", got, payload)
	}
}

func TestMaterializeRawDecmpfsLeavesSupportedCompressionUntouched(t *testing.T) {
	attr := make([]byte, 16)
	copy(attr[:4], []byte("fpmc"))
	binary.LittleEndian.PutUint32(attr[4:8], 11)

	got, materialized, err := materializeRawDecmpfs(
		map[string][]byte{"com.apple.decmpfs": attr})
	if err != nil {
		t.Fatal(err)
	}
	if materialized || got != nil {
		t.Fatal("supported type 11 should be preserved as compressed xattrs")
	}
}

func TestWriteRawRamdiskCopiesExactAPFSBytes(t *testing.T) {
	dir := t.TempDir()
	rawPath := filepath.Join(dir, "ramdisk.raw")
	outputPath := filepath.Join(dir, "ramdisk.dmg")

	payload := make([]byte, 8192)
	copy(payload[32:36], []byte("NXSB"))
	for i := 4096; i < len(payload); i++ {
		payload[i] = byte(i % 251)
	}
	if err := os.WriteFile(rawPath, payload, 0o600); err != nil {
		t.Fatal(err)
	}

	raw, err := os.Open(rawPath)
	if err != nil {
		t.Fatal(err)
	}
	defer raw.Close()

	if err := writeRawRamdisk(outputPath, raw, int64(len(payload))); err != nil {
		t.Fatal(err)
	}

	got, err := os.ReadFile(outputPath)
	if err != nil {
		t.Fatal(err)
	}
	if len(got) != len(payload) {
		t.Fatalf("output length = %d, want %d", len(got), len(payload))
	}
	if string(got) != string(payload) {
		t.Fatal("output is not the exact raw APFS byte stream")
	}
	if string(got[32:36]) != "NXSB" {
		t.Fatalf("APFS magic = %q, want NXSB", got[32:36])
	}
}

func TestMergeSysrootTarPreservesExistingRecoveryBash(t *testing.T) {
	dir := t.TempDir()
	archive := filepath.Join(dir, "sysroot.tar.gz")
	file, err := os.Create(archive)
	if err != nil { t.Fatal(err) }
	gz := gzip.NewWriter(file)
	tw := tar.NewWriter(gz)
	injected := []byte("sysroot bash")
	if err := tw.WriteHeader(&tar.Header{Name: "prebuilt/bin/bash", Mode: 0o755, Size: int64(len(injected)), Typeflag: tar.TypeReg}); err != nil { t.Fatal(err) }
	if _, err := tw.Write(injected); err != nil { t.Fatal(err) }
	if err := tw.Close(); err != nil { t.Fatal(err) }
	if err := gz.Close(); err != nil { t.Fatal(err) }
	if err := file.Close(); err != nil { t.Fatal(err) }

	original := []byte("apple recovery bash")
	root := &apfswrite.Entry{Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{{
		Name: "bin", Mode: fs.ModeDir | 0o755, Children: []*apfswrite.Entry{{
			Name: "bash", Mode: 0o755, UID: 0, GID: 0, Data: append([]byte(nil), original...),
		}},
	}}}
	if err := mergeSysrootTar(root, archive); err != nil { t.Fatal(err) }
	bash, err := findPath(root, "bin/bash")
	if err != nil { t.Fatal(err) }
	if string(bash.Data) != string(original) {
		t.Fatalf("recovery bash was overwritten: got %q, want %q", bash.Data, original)
	}
}

func TestFormatSourceSignedExecutableDiagnostic(t *testing.T) {
	got := formatSourceSignedExecutableDiagnostic("/usr/libexec/xpcproxy", []byte{0xcf, 0xfa, 0xed, 0xfe}, "0123456789abcdef0123456789abcdef01234567", true)
	want := "source-signed-exec path=/usr/libexec/xpcproxy macho=true size=4 cdhash_ok=true primary_cdhash=0123456789abcdef0123456789abcdef01234567"
	if got != want { t.Fatalf("diagnostic = %q, want %q", got, want) }
}
