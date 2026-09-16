package main

import "testing"

func TestPrimaryCodeDirectoryPatternMatchesRcodesignOutput(t *testing.T) {
	const output = `
SuperBlob {
  blobs:
    - slot: CodeDirectory (0)
      magic: CSMAGIC_CODEDIRECTORY
      sha256: ba46def193e2d7dd2c223207644cf5a48f7e6950fa041c5f6ffdc983a29f753a
    - slot: 'CodeDirectory Alternate #0 (4096)'
      sha256: 3e028109062df8c628e70d67584a97b9a64f71ad94708bc5c1d4617eb72ded28
}
`

	match := primaryCodeDirectoryPattern.FindStringSubmatch(output)
	if len(match) != 2 {
		t.Fatalf("primary CodeDirectory SHA-256 not matched")
	}

	const want = "ba46def193e2d7dd2c223207644cf5a48f7e6950fa041c5f6ffdc983a29f753a"
	if match[1] != want {
		t.Fatalf("sha256 = %q, want %q", match[1], want)
	}
}
