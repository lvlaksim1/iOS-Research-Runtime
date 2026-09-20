package main

import (
	"bytes"
	"encoding/binary"
	"testing"
)

func TestReadNXSnapshotUsesContainerRelativeOffsets(t *testing.T) {
	const offset = 512
	const blockSize = 4096
	image := make([]byte, offset+14*blockSize)
	block := image[offset:]
	copy(block[32:36], []byte("NXSB"))
	binary.LittleEndian.PutUint32(block[36:40], blockSize)
	binary.LittleEndian.PutUint64(block[40:48], 1234)
	binary.LittleEndian.PutUint64(block[16:24], 77)
	binary.LittleEndian.PutUint64(block[88:96], 99)
	binary.LittleEndian.PutUint64(block[96:104], 78)
	binary.LittleEndian.PutUint32(block[104:108], 2)
	binary.LittleEndian.PutUint64(block[112:120], 12)
	binary.LittleEndian.PutUint64(block[120:128], 34)

	checkpoint := image[offset+13*blockSize:]
	copy(checkpoint[32:36], []byte("NXSB"))
	binary.LittleEndian.PutUint64(checkpoint[16:24], 81)
	binary.LittleEndian.PutUint64(checkpoint[96:104], 82)

	snapshot, err := readNXSnapshot(bytes.NewReader(image), offset)
	if err != nil {
		t.Fatal(err)
	}
	if snapshot.BlockSize != 4096 || snapshot.BlockCount != 1234 || snapshot.XID != 77 || snapshot.NextOID != 99 {
		t.Fatalf("unexpected snapshot: %+v", snapshot)
	}
	if snapshot.XpDescBase != 12 || snapshot.XpDataBase != 34 {
		t.Fatalf("unexpected checkpoint geometry: %+v", snapshot)
	}
	if snapshot.LatestCheckpointXID != 81 || snapshot.LatestCheckpointNextXID != 82 || snapshot.LatestCheckpointBlock != 13 {
		t.Fatalf("unexpected latest checkpoint evidence: %+v", snapshot)
	}
}

func TestReadNXSnapshotRejectsWrongLayer(t *testing.T) {
	_, err := readNXSnapshot(bytes.NewReader(make([]byte, 0x580)), 0)
	if err == nil {
		t.Fatal("expected missing NXSB error")
	}
}
