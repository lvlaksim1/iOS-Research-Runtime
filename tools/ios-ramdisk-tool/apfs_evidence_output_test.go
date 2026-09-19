package main

import (
	"bytes"
	"encoding/json"
	"testing"
)

func TestWriteNXEvidenceProducesStablePair(t *testing.T) {
	source := apfsNXSnapshot{BlockSize: 4096, BlockCount: 10, ContainerUUID: "source", XID: 7}
	rebuilt := apfsNXSnapshot{BlockSize: 4096, BlockCount: 11, ContainerUUID: "rebuilt", XID: 8}
	var buffer bytes.Buffer
	if err := writeNXEvidence(&buffer, source, rebuilt); err != nil {
		t.Fatalf("writeNXEvidence: %v", err)
	}
	var got apfsNXEvidence
	if err := json.Unmarshal(buffer.Bytes(), &got); err != nil {
		t.Fatalf("decode evidence: %v", err)
	}
	if got.Source != source {
		t.Fatalf("source mismatch: %#v", got.Source)
	}
	if got.Rebuilt != rebuilt {
		t.Fatalf("rebuilt mismatch: %#v", got.Rebuilt)
	}
}
