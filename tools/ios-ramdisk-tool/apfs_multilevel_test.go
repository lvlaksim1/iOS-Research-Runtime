package main

import (
	"fmt"
	"io/fs"
	"os"
	"testing"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfs"
	"github.com/deploymenttheory/go-apfs-v2/pkg/apfswrite"
)

func TestPatchedAPFSWriterSupportsThreeLevelFSTreeAndTwoLevelOmap(t *testing.T) {
	const fileCount = 2500

	children := make([]*apfswrite.Entry, 0, fileCount)
	for i := 0; i < fileCount; i++ {
		children = append(children, &apfswrite.Entry{
			Name: fmt.Sprintf("file-%04d", i),
			Mode: 0o644,
			Data: nil,
		})
	}

	image, err := os.CreateTemp(t.TempDir(), "large-apfs-*.raw")
	if err != nil {
		t.Fatal(err)
	}
	imagePath := image.Name()
	defer image.Close()

	err = apfswrite.CreateContainer(image, 0, &apfswrite.CreateOptions{
		VolumeName: "LARGE",
		Root: &apfswrite.Entry{
			Mode:     fs.ModeDir | 0o755,
			Children: children,
		},
	})
	if err != nil {
		t.Fatalf("CreateContainer large tree: %v", err)
	}
	if err := image.Close(); err != nil {
		t.Fatal(err)
	}

	container, closer, err := apfs.OpenImage(imagePath, nil)
	if err != nil {
		t.Fatalf("open created APFS image: %v", err)
	}
	defer closer.Close()

	volume, err := container.VolumeBySelector("0")
	if err != nil {
		t.Fatal(err)
	}
	info, err := volume.Stat("file-2499")
	if err != nil {
		t.Fatalf("resolve file through multi-level trees: %v", err)
	}
	if info.Name() != "file-2499" {
		t.Fatalf("unexpected file name %q", info.Name())
	}
}
