package main

import (
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfs"
	"github.com/deploymenttheory/go-apfs-v2/pkg/disk"
)

type apfsTreeSnapshot struct {
	OID             uint64 `json:"oid"`
	PhysicalAddress uint64 `json:"physicalAddress"`
	HeaderOID       uint64 `json:"headerOid"`
	HeaderXID       uint64 `json:"headerXid"`
	HeaderType      uint32 `json:"headerType"`
	HeaderSubtype   uint32 `json:"headerSubtype"`
	StoredChecksum  uint64 `json:"storedChecksum"`
	ComputedChecksum uint64 `json:"computedChecksum"`
	ChecksumValid   bool   `json:"checksumValid"`
}

type apfsVolumeSnapshot struct {
	FSIndex                    uint32 `json:"fsIndex"`
	CompatibleFeatures         uint64 `json:"compatibleFeatures"`
	ReadOnlyCompatibleFeatures uint64 `json:"readOnlyCompatibleFeatures"`
	IncompatibleFeatures       uint64 `json:"incompatibleFeatures"`
	MetaCryptoMajorVersion     uint16 `json:"metaCryptoMajorVersion"`
	MetaCryptoMinorVersion     uint16 `json:"metaCryptoMinorVersion"`
	MetaCryptoFlags            uint32 `json:"metaCryptoFlags"`
	MetaCryptoPersistentClass  uint32 `json:"metaCryptoPersistentClass"`
	MetaCryptoKeyOSVersion     uint32 `json:"metaCryptoKeyOsVersion"`
	MetaCryptoKeyRevision      uint16 `json:"metaCryptoKeyRevision"`
	RootTreeType               uint32 `json:"rootTreeType"`
	ExtentrefTreeType          uint32 `json:"extentrefTreeType"`
	SnapMetaTreeType           uint32 `json:"snapMetaTreeType"`
	OmapOID                    uint64 `json:"omapOid"`
	RootTreeOID                uint64 `json:"rootTreeOid"`
	RootTreePhysicalAddress    uint64 `json:"rootTreePhysicalAddress"`
	RootTreeHeaderOID          uint64 `json:"rootTreeHeaderOid"`
	RootTreeHeaderXID          uint64 `json:"rootTreeHeaderXid"`
	RootTreeHeaderType         uint32 `json:"rootTreeHeaderType"`
	RootTreeHeaderSubtype      uint32 `json:"rootTreeHeaderSubtype"`
	RootTreeStoredChecksum     uint64 `json:"rootTreeStoredChecksum"`
	RootTreeComputedChecksum   uint64 `json:"rootTreeComputedChecksum"`
	RootTreeChecksumValid      bool   `json:"rootTreeChecksumValid"`
	ExtentrefTreeOID           uint64 `json:"extentrefTreeOid"`
	ExtentrefTree              *apfsTreeSnapshot `json:"extentrefTree,omitempty"`
	SnapMetaTreeOID            uint64 `json:"snapMetaTreeOid"`
	SnapMetaTree               *apfsTreeSnapshot `json:"snapMetaTree,omitempty"`
	RevertToXID                uint64 `json:"revertToXid"`
	RevertToSblockOID          uint64 `json:"revertToSblockOid"`
	NextObjID                  uint64 `json:"nextObjId"`
	NumberOfFiles              uint64 `json:"numberOfFiles"`
	NumberOfDirectories        uint64 `json:"numberOfDirectories"`
	NumberOfSymlinks           uint64 `json:"numberOfSymlinks"`
	NumberOfOtherFSObjects     uint64 `json:"numberOfOtherFsObjects"`
	SnapshotCount              uint64 `json:"snapshotCount"`
	TotalBlocksAllocated       uint64 `json:"totalBlocksAllocated"`
	TotalBlocksFreed           uint64 `json:"totalBlocksFreed"`
	VolumeUUID                 string `json:"volumeUuid"`
	ModificationTime           uint64 `json:"modificationTime"`
	VolumeFlags                uint64 `json:"volumeFlags"`
	Role                       uint16 `json:"role"`
	RootToXID                  uint64 `json:"rootToXid"`
	SnapMetaExtOID             uint64 `json:"snapMetaExtOid"`
	VolumeGroupID              string `json:"volumeGroupId"`
}

type apfsNXSnapshot struct {
	BlockSize uint32 `json:"blockSize"`
	BlockCount uint64 `json:"blockCount"`
	Features uint64 `json:"features"`
	ReadOnlyCompatibleFeatures uint64 `json:"readOnlyCompatibleFeatures"`
	IncompatibleFeatures uint64 `json:"incompatibleFeatures"`
	ContainerUUID string `json:"containerUuid"`
	OID uint64 `json:"oid"`
	XID uint64 `json:"xid"`
	NextOID uint64 `json:"nextOid"`
	NextXID uint64 `json:"nextXid"`
	XpDescBlocks uint32 `json:"xpDescBlocks"`
	XpDataBlocks uint32 `json:"xpDataBlocks"`
	XpDescBase uint64 `json:"xpDescBase"`
	XpDataBase uint64 `json:"xpDataBase"`
	XpDescNext uint32 `json:"xpDescNext"`
	XpDataNext uint32 `json:"xpDataNext"`
	XpDescIndex uint32 `json:"xpDescIndex"`
	XpDescLen uint32 `json:"xpDescLen"`
	XpDataIndex uint32 `json:"xpDataIndex"`
	XpDataLen uint32 `json:"xpDataLen"`
	SpacemanOID uint64 `json:"spacemanOid"`
	OmapOID uint64 `json:"omapOid"`
	ReaperOID uint64 `json:"reaperOid"`
	Flags uint64 `json:"flags"`
	LatestCheckpointXID uint64 `json:"latestCheckpointXid"`
	LatestCheckpointNextXID uint64 `json:"latestCheckpointNextXid"`
	LatestCheckpointBlock uint64 `json:"latestCheckpointBlock"`
	Volume *apfsVolumeSnapshot `json:"volume"`
}

func readSourceNXSnapshot(filename string) (apfsNXSnapshot, error) {
	reader, offset, closer, err := disk.OpenWithOffset(filename)
	if err != nil { return apfsNXSnapshot{}, fmt.Errorf("open decoded APFS source: %w", err) }
	defer closer.Close()
	return readNXSnapshot(reader, offset)
}

func readNXSnapshot(reader io.ReaderAt, containerOffset int64) (apfsNXSnapshot, error) {
	buffer := make([]byte, 0x580)
	if _, err := reader.ReadAt(buffer, containerOffset); err != nil && err != io.EOF { return apfsNXSnapshot{}, fmt.Errorf("read NXSB block: %w", err) }
	if string(buffer[32:36]) != "NXSB" { return apfsNXSnapshot{}, fmt.Errorf("APFS NXSB magic missing at container offset 0x%x", containerOffset) }
	u32 := func(at int) uint32 { return binary.LittleEndian.Uint32(buffer[at:at+4]) }
	u64 := func(at int) uint64 { return binary.LittleEndian.Uint64(buffer[at:at+8]) }
	snapshot := apfsNXSnapshot{BlockSize:u32(36),BlockCount:u64(40),Features:u64(48),ReadOnlyCompatibleFeatures:u64(56),IncompatibleFeatures:u64(64),ContainerUUID:formatUUID(buffer[72:88]),OID:u64(8),XID:u64(16),NextOID:u64(88),NextXID:u64(96),XpDescBlocks:u32(104),XpDataBlocks:u32(108),XpDescBase:u64(112),XpDataBase:u64(120),XpDescNext:u32(128),XpDataNext:u32(132),XpDescIndex:u32(136),XpDescLen:u32(140),XpDataIndex:u32(144),XpDataLen:u32(148),SpacemanOID:u64(152),OmapOID:u64(160),ReaperOID:u64(168),Flags:u64(0x4d8),LatestCheckpointXID:u64(16),LatestCheckpointNextXID:u64(96)}
	if snapshot.BlockSize==0 { return apfsNXSnapshot{}, fmt.Errorf("APFS NXSB has zero block size") }
	for index:=uint64(0); index<uint64(snapshot.XpDescBlocks); index++ { blockNumber:=snapshot.XpDescBase+index; checkpoint:=make([]byte,0x580); if _,err:=reader.ReadAt(checkpoint,containerOffset+int64(blockNumber)*int64(snapshot.BlockSize)); err!=nil&&err!=io.EOF{return apfsNXSnapshot{},fmt.Errorf("read checkpoint descriptor block %d: %w",blockNumber,err)}; if len(checkpoint)<104||string(checkpoint[32:36])!="NXSB"{continue}; xid:=binary.LittleEndian.Uint64(checkpoint[16:24]); if xid>=snapshot.LatestCheckpointXID{snapshot.LatestCheckpointXID=xid;snapshot.LatestCheckpointNextXID=binary.LittleEndian.Uint64(checkpoint[96:104]);snapshot.LatestCheckpointBlock=blockNumber} }
	if volume,err:=readAPFSVolumeSnapshot(reader,containerOffset,snapshot.BlockSize,snapshot.BlockCount);err==nil{snapshot.Volume=volume}
	return snapshot,nil
}

func readAPFSVolumeSnapshot(reader io.ReaderAt, containerOffset int64, blockSize uint32, blockCount uint64) (*apfsVolumeSnapshot,error){
	magic:=make([]byte,4)
	for block:=uint64(0);block<blockCount;block++{offset:=containerOffset+int64(block)*int64(blockSize);if _,err:=reader.ReadAt(magic,offset+32);err!=nil{if err==io.EOF{break};return nil,fmt.Errorf("read APSB magic at block %d: %w",block,err)};if string(magic)!="APSB"{continue};superblock:=apfs.NewVolumeSuperblock();if err:=superblock.ReadFrom(reader,offset,false);err!=nil{continue};return &apfsVolumeSnapshot{FSIndex:superblock.FSIndex,CompatibleFeatures:superblock.CompatibleFeaturesFlags,ReadOnlyCompatibleFeatures:superblock.ReadOnlyCompatibleFeaturesFlags,IncompatibleFeatures:superblock.IncompatibleFeaturesFlags,MetaCryptoMajorVersion:superblock.MetaCryptoMajorVersion,MetaCryptoMinorVersion:superblock.MetaCryptoMinorVersion,MetaCryptoFlags:superblock.MetaCryptoFlags,MetaCryptoPersistentClass:superblock.MetaCryptoPersistentClass,MetaCryptoKeyOSVersion:superblock.MetaCryptoKeyOSVersion,MetaCryptoKeyRevision:superblock.MetaCryptoKeyRevision,RootTreeType:superblock.RootTreeType,ExtentrefTreeType:superblock.ExtentrefTreeType,SnapMetaTreeType:superblock.SnapMetaTreeType,OmapOID:superblock.OmapOID,RootTreeOID:superblock.RootTreeOID,ExtentrefTreeOID:superblock.ExtentrefTreeOID,SnapMetaTreeOID:superblock.SnapMetaTreeOID,RevertToXID:superblock.RevertToXID,RevertToSblockOID:superblock.RevertToSblockOID,NextObjID:superblock.NextObjID,NumberOfFiles:superblock.NumberOfFiles,NumberOfDirectories:superblock.NumberOfDirectories,NumberOfSymlinks:superblock.NumberOfSymlinks,NumberOfOtherFSObjects:superblock.NumberOfOtherFileSystemObjects,SnapshotCount:superblock.SnapshotCount,TotalBlocksAllocated:superblock.TotalBlocksAllocated,TotalBlocksFreed:superblock.TotalBlocksFreed,VolumeUUID:formatUUID(superblock.VolumeUUID[:]),ModificationTime:superblock.ModificationTime,VolumeFlags:superblock.VolumeFlags,Role:superblock.Role,RootToXID:superblock.RootToXID,SnapMetaExtOID:superblock.SnapMetaExtOID,VolumeGroupID:formatUUID(superblock.VolumeGroupID[:])},nil}
	return nil,fmt.Errorf("APFS volume superblock not found")
}

func formatUUID(value []byte) string { encoded:=hex.EncodeToString(value); if len(encoded)!=32{return encoded}; return fmt.Sprintf("%s-%s-%s-%s-%s",encoded[0:8],encoded[8:12],encoded[12:16],encoded[16:20],encoded[20:32]) }
