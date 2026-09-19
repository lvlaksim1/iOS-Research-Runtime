package main

import (
	"encoding/json"
	"fmt"
	"io"
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
