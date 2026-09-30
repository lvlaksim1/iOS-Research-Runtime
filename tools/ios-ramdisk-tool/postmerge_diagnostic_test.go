package main

import "testing"

func TestFormatPostMergeBashDiagnostic(t *testing.T) {
	data := []byte{0xcf, 0xfa, 0xed, 0xfe, 1, 2, 3}
	hash := "0123456789abcdef0123456789abcdef01234567"
	got := formatPostMergeBashDiagnostic(data, hash, true, map[string]struct{}{hash: {}})
	want := "post-merge-bash path=/bin/bash macho=true size=7 primary_cdhash=0123456789abcdef0123456789abcdef01234567 primary_cdhash_ok=true injected_trust_member=true"
	if got != want {
		t.Fatalf("diagnostic = %q, want %q", got, want)
	}
}
