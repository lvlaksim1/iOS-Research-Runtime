package main

import (
	"archive/tar"
	"compress/gzip"
	"encoding/binary"
	"io/fs"
	"os"
	"path/filepath"
	"testing"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfswrite"
)

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
