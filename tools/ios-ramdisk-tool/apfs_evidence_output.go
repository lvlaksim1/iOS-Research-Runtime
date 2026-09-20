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
	if source.Volume == nil {
		return fmt.Errorf("read source APFS APSB evidence: volume superblock not found")
	}
	if err := preserveMetaCryptoKeyOSVersion(rebuilt, source.Volume.MetaCryptoKeyOSVersion); err != nil {
		return fmt.Errorf("preserve APFS MetaCryptoKeyOSVersion: %w", err)
	}
	rebuiltSnapshot, err := readNXSnapshot(rebuilt, 0)
	if err != nil {
		return fmt.Errorf("read rebuilt APFS NX evidence: %w", err)
	}
	if rebuiltSnapshot.Volume == nil {
		return fmt.Errorf("read rebuilt APFS APSB evidence: volume superblock not found")
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
