package main

import (
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"
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
	nx, err := readNXSnapshot(file, 0)
	if err != nil {
		return err
	}
	blockSize := int(nx.BlockSize)
	if blockSize < 112 {
		return fmt.Errorf("invalid APFS block size %d", blockSize)
	}
	block := make([]byte, blockSize)
	for paddr := uint64(0); paddr < nx.BlockCount; paddr++ {
		offset := int64(paddr) * int64(blockSize)
		if _, err := file.ReadAt(block, offset); err != nil && err != io.EOF {
			return fmt.Errorf("read APFS block %d: %w", paddr, err)
		}
		if string(block[32:36]) != "APSB" {
			continue
		}
		binary.LittleEndian.PutUint32(block[108:112], keyOSVersion)
		binary.LittleEndian.PutUint64(block[:8], apfsFletcher64(block[8:]))
		if apfsFletcher64(block[8:]) != binary.LittleEndian.Uint64(block[:8]) {
			return fmt.Errorf("APSB checksum validation failed at block %d", paddr)
		}
		if _, err := file.WriteAt(block, offset); err != nil {
			return fmt.Errorf("write APSB block %d: %w", paddr, err)
		}
		return file.Sync()
	}
	return fmt.Errorf("APFS APSB volume superblock not found")
}

func apfsFletcher64(data []byte) uint64 {
	const modulus uint64 = 0xffffffff
	var sum1 uint64
	var sum2 uint64
	for offset := 0; offset+4 <= len(data); offset += 4 {
		sum1 = (sum1 + uint64(binary.LittleEndian.Uint32(data[offset:offset+4]))) % modulus
		sum2 = (sum2 + sum1) % modulus
	}
	check1 := modulus - ((sum1 + sum2) % modulus)
	check2 := modulus - ((sum1 + check1) % modulus)
	return (check2 << 32) | check1
}
