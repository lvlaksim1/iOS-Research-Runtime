package main

import (
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

func writeNXEvidenceFile(outputPath, sourcePath string, rebuilt io.ReaderAt) error {
	source, err := readSourceNXSnapshot(sourcePath)
	if err != nil {
		return fmt.Errorf("read source APFS NX evidence: %w", err)
	}
	rebuiltSnapshot, err := readNXSnapshot(rebuilt, 0)
	if err != nil {
		return fmt.Errorf("read rebuilt APFS NX evidence: %w", err)
	}
	if source.Volume == nil {
		return fmt.Errorf("read source APFS APSB evidence: volume superblock not found")
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
