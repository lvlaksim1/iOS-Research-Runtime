package main

import (
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/deploymenttheory/go-apfs-v2/pkg/apfs"
)

type apfsNXEvidence struct {
	Source  apfsNXSnapshot `json:"source"`
	Rebuilt apfsNXSnapshot `json:"rebuilt"`
}

func writeNXEvidence(writer io.Writer, source, rebuilt apfsNXSnapshot) error {
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(apfsNXEvidence{Source: source, Rebuilt: rebuilt}); err != nil {
		return fmt.Errorf("encode APFS NX evidence: %w", err)
	}
	return nil
}

func writeNXEvidenceFile(outputPath, sourcePath string, rebuilt *os.File) error {
	source, err := readSourceNXSnapshot(sourcePath)
	if err != nil {
		return fmt.Errorf("read source APFS NX evidence: %w", err)
	}
	source.Volume, err = readMappedAPFSVolumeSnapshot(sourcePath)
	if err != nil {
		return fmt.Errorf("resolve source APFS live-volume evidence: %w", err)
	}
	if err := preserveMetaCryptoKeyOSVersion(rebuilt, source.Volume.MetaCryptoKeyOSVersion); err != nil {
		return fmt.Errorf("preserve APFS MetaCryptoKeyOSVersion: %w", err)
	}
	rebuiltSnapshot, err := readNXSnapshot(rebuilt, 0)
	if err != nil {
		return fmt.Errorf("read rebuilt APFS NX evidence: %w", err)
	}
	rebuiltSnapshot.Volume, err = readMappedAPFSVolumeSnapshot(rebuilt.Name())
	if err != nil {
		return fmt.Errorf("resolve rebuilt APFS live-volume evidence: %w", err)
	}
	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("create APFS NX evidence output: %w", err)
	}
	defer file.Close()
	if err := writeNXEvidence(file, source, rebuiltSnapshot); err != nil {
		return err
	}
	return nil
}

func readMappedAPFSVolumeSnapshot(filename string) (*apfsVolumeSnapshot, error) {
	container, closer, err := apfs.OpenImage(filename, nil)
	if err != nil {
		return nil, fmt.Errorf("open APFS container: %w", err)
	}
	defer closer.Close()

	volume, err := container.VolumeBySelector("0")
	if err != nil {
		return nil, fmt.Errorf("resolve active APFS volume: %w", err)
	}
	if volume.Superblock == nil {
		return nil, fmt.Errorf("resolved APFS volume has no superblock")
	}
	if volume.ObjectMapBTree == nil {
		return nil, fmt.Errorf("resolved APFS volume has no object map")
	}
	superblock := volume.Superblock
	rootDescriptor, err := volume.ObjectMapBTree.DescriptorByObjectIdentifier(container.Reader, superblock.RootTreeOID, superblock.XID)
	if err != nil {
		return nil, fmt.Errorf("resolve live-volume root-tree oid %d: %w", superblock.RootTreeOID, err)
	}
	if rootDescriptor == nil || rootDescriptor.Value.ObjectPhysicalAddress == 0 {
		return nil, fmt.Errorf("resolve live-volume root-tree oid %d: mapping missing", superblock.RootTreeOID)
	}
	rootPaddr := rootDescriptor.Value.ObjectPhysicalAddress
	blockSize := int(container.Superblock.BlockSize)
	if blockSize < 32 {
		return nil, fmt.Errorf("invalid APFS block size %d", blockSize)
	}
	rootBlock := make([]byte, blockSize)
	if _, err := container.Reader.ReadAt(rootBlock, int64(rootPaddr)*int64(blockSize)); err != nil && err != io.EOF {
		return nil, fmt.Errorf("read live-volume root-tree block %d: %w", rootPaddr, err)
	}
	computedChecksum, err := apfs.CalculateFletcher64(rootBlock[8:], 0)
	if err != nil {
		return nil, fmt.Errorf("calculate live-volume root-tree checksum at block %d: %w", rootPaddr, err)
	}
	storedChecksum := binary.LittleEndian.Uint64(rootBlock[0:8])

	return &apfsVolumeSnapshot{
		FSIndex: superblock.FSIndex,
		CompatibleFeatures: superblock.CompatibleFeaturesFlags,
		ReadOnlyCompatibleFeatures: superblock.ReadOnlyCompatibleFeaturesFlags,
		IncompatibleFeatures: superblock.IncompatibleFeaturesFlags,
		MetaCryptoMajorVersion: superblock.MetaCryptoMajorVersion,
		MetaCryptoMinorVersion: superblock.MetaCryptoMinorVersion,
		MetaCryptoFlags: superblock.MetaCryptoFlags,
		MetaCryptoPersistentClass: superblock.MetaCryptoPersistentClass,
		MetaCryptoKeyOSVersion: superblock.MetaCryptoKeyOSVersion,
		MetaCryptoKeyRevision: superblock.MetaCryptoKeyRevision,
		RootTreeType: superblock.RootTreeType,
		ExtentrefTreeType: superblock.ExtentrefTreeType,
		SnapMetaTreeType: superblock.SnapMetaTreeType,
		OmapOID: superblock.OmapOID,
		RootTreeOID: superblock.RootTreeOID,
		RootTreePhysicalAddress: rootPaddr,
		RootTreeHeaderOID: binary.LittleEndian.Uint64(rootBlock[8:16]),
		RootTreeHeaderXID: binary.LittleEndian.Uint64(rootBlock[16:24]),
		RootTreeHeaderType: binary.LittleEndian.Uint32(rootBlock[24:28]),
		RootTreeHeaderSubtype: binary.LittleEndian.Uint32(rootBlock[28:32]),
		RootTreeStoredChecksum: storedChecksum,
		RootTreeComputedChecksum: computedChecksum,
		RootTreeChecksumValid: storedChecksum == computedChecksum,
		ExtentrefTreeOID: superblock.ExtentrefTreeOID,
		SnapMetaTreeOID: superblock.SnapMetaTreeOID,
		RevertToXID: superblock.RevertToXID,
		RevertToSblockOID: superblock.RevertToSblockOID,
		NextObjID: superblock.NextObjID,
		NumberOfFiles: superblock.NumberOfFiles,
		NumberOfDirectories: superblock.NumberOfDirectories,
		NumberOfSymlinks: superblock.NumberOfSymlinks,
		NumberOfOtherFSObjects: superblock.NumberOfOtherFileSystemObjects,
		SnapshotCount: superblock.SnapshotCount,
		TotalBlocksAllocated: superblock.TotalBlocksAllocated,
		TotalBlocksFreed: superblock.TotalBlocksFreed,
		VolumeUUID: formatUUID(superblock.VolumeUUID[:]),
		ModificationTime: superblock.ModificationTime,
		VolumeFlags: superblock.VolumeFlags,
		Role: superblock.Role,
		RootToXID: superblock.RootToXID,
		SnapMetaExtOID: superblock.SnapMetaExtOID,
		VolumeGroupID: formatUUID(superblock.VolumeGroupID[:]),
	}, nil
}

func preserveMetaCryptoKeyOSVersion(file *os.File, keyOSVersion uint32) error {
	container, closer, err := apfs.OpenImage(file.Name(), nil)
	if err != nil {
		return fmt.Errorf("open rebuilt APFS container: %w", err)
	}
	defer closer.Close()

	volumeIDs, err := container.VolumeObjectIdentifiers()
	if err != nil {
		return fmt.Errorf("resolve rebuilt APFS volume object id: %w", err)
	}
	if len(volumeIDs) == 0 {
		return fmt.Errorf("rebuilt APFS container has no volumes")
	}
	volumeOID := volumeIDs[0]

	paddr, err := container.CheckpointMap.PhysicalAddressByObjectIdentifier(volumeOID)
	if err != nil || paddr == 0 {
		descriptor, lookupErr := container.ObjectMapBTree.DescriptorByObjectIdentifier(container.Reader, volumeOID, container.Superblock.XID)
		if lookupErr != nil {
			return fmt.Errorf("resolve rebuilt APFS volume paddr: %w", lookupErr)
		}
		if descriptor == nil || descriptor.Value.ObjectPhysicalAddress == 0 {
			return fmt.Errorf("resolve rebuilt APFS volume paddr: mapping missing for object %d", volumeOID)
		}
		paddr = descriptor.Value.ObjectPhysicalAddress
	}

	blockSize := int(container.Superblock.BlockSize)
	if blockSize < 112 {
		return fmt.Errorf("invalid APFS block size %d", blockSize)
	}
	block := make([]byte, blockSize)
	offset := int64(paddr) * int64(blockSize)
	if _, err := file.ReadAt(block, offset); err != nil && err != io.EOF {
		return fmt.Errorf("read APSB block %d: %w", paddr, err)
	}
	if string(block[32:36]) != "APSB" {
		return fmt.Errorf("resolved APFS volume block %d is not APSB", paddr)
	}

	binary.LittleEndian.PutUint32(block[108:112], keyOSVersion)
	checksum, err := apfs.CalculateFletcher64(block[8:], 0)
	if err != nil {
		return fmt.Errorf("calculate APSB checksum at block %d: %w", paddr, err)
	}
	binary.LittleEndian.PutUint64(block[:8], checksum)
	validated, err := apfs.CalculateFletcher64(block[8:], 0)
	if err != nil {
		return fmt.Errorf("validate APSB checksum at block %d: %w", paddr, err)
	}
	if validated != binary.LittleEndian.Uint64(block[:8]) {
		return fmt.Errorf("APSB checksum validation failed at block %d", paddr)
	}
	if _, err := file.WriteAt(block, offset); err != nil {
		return fmt.Errorf("write APSB block %d: %w", paddr, err)
	}
	return file.Sync()
}
