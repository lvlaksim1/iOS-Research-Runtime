package main

import (
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"

	"github.com/deploymenttheory/go-apfs-v2/pkg/disk"
)

type apfsNXSnapshot struct {
	BlockSize                  uint32 `json:"blockSize"`
	BlockCount                 uint64 `json:"blockCount"`
	Features                   uint64 `json:"features"`
	ReadOnlyCompatibleFeatures uint64 `json:"readOnlyCompatibleFeatures"`
	IncompatibleFeatures       uint64 `json:"incompatibleFeatures"`
	ContainerUUID              string `json:"containerUuid"`
	OID                        uint64 `json:"oid"`
	XID                        uint64 `json:"xid"`
	NextOID                    uint64 `json:"nextOid"`
	NextXID                    uint64 `json:"nextXid"`
	XpDescBlocks               uint32 `json:"xpDescBlocks"`
	XpDataBlocks               uint32 `json:"xpDataBlocks"`
	XpDescBase                 uint64 `json:"xpDescBase"`
	XpDataBase                 uint64 `json:"xpDataBase"`
	XpDescNext                 uint32 `json:"xpDescNext"`
	XpDataNext                 uint32 `json:"xpDataNext"`
	XpDescIndex                uint32 `json:"xpDescIndex"`
	XpDescLen                  uint32 `json:"xpDescLen"`
	XpDataIndex                uint32 `json:"xpDataIndex"`
	XpDataLen                  uint32 `json:"xpDataLen"`
	SpacemanOID                uint64 `json:"spacemanOid"`
	OmapOID                    uint64 `json:"omapOid"`
	ReaperOID                  uint64 `json:"reaperOid"`
	Flags                      uint64 `json:"flags"`
}

func readSourceNXSnapshot(filename string) (apfsNXSnapshot, error) {
	reader, offset, closer, err := disk.OpenWithOffset(filename)
	if err != nil {
		return apfsNXSnapshot{}, fmt.Errorf("open decoded APFS source: %w", err)
	}
	defer closer.Close()
	return readNXSnapshot(reader, offset)
}

func readNXSnapshot(reader io.ReaderAt, containerOffset int64) (apfsNXSnapshot, error) {
	buffer := make([]byte, 0x580)
	if _, err := reader.ReadAt(buffer, containerOffset); err != nil && err != io.EOF {
		return apfsNXSnapshot{}, fmt.Errorf("read NXSB block: %w", err)
	}
	if string(buffer[32:36]) != "NXSB" {
		return apfsNXSnapshot{}, fmt.Errorf("APFS NXSB magic missing at container offset 0x%x", containerOffset)
	}
	u32 := func(at int) uint32 { return binary.LittleEndian.Uint32(buffer[at : at+4]) }
	u64 := func(at int) uint64 { return binary.LittleEndian.Uint64(buffer[at : at+8]) }
	uuid := buffer[72:88]
	return apfsNXSnapshot{
		BlockSize: u32(36), BlockCount: u64(40), Features: u64(48),
		ReadOnlyCompatibleFeatures: u64(56), IncompatibleFeatures: u64(64),
		ContainerUUID: fmt.Sprintf("%s-%s-%s-%s-%s", hex.EncodeToString(uuid[0:4]), hex.EncodeToString(uuid[4:6]), hex.EncodeToString(uuid[6:8]), hex.EncodeToString(uuid[8:10]), hex.EncodeToString(uuid[10:16])),
		OID: u64(8), XID: u64(16), NextOID: u64(88), NextXID: u64(96),
		XpDescBlocks: u32(104), XpDataBlocks: u32(108), XpDescBase: u64(112), XpDataBase: u64(120),
		XpDescNext: u32(128), XpDataNext: u32(132), XpDescIndex: u32(136), XpDescLen: u32(140),
		XpDataIndex: u32(144), XpDataLen: u32(148), SpacemanOID: u64(152), OmapOID: u64(160), ReaperOID: u64(168), Flags: u64(0x4d8),
	}, nil
}
