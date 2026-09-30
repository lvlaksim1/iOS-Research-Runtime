package main

import "fmt"

func formatPostMergeBashDiagnostic(data []byte, primaryCDHash string, hasPrimaryCDHash bool, injectedHashes map[string]struct{}) string {
	_, trusted := injectedHashes[primaryCDHash]
	return fmt.Sprintf("post-merge-bash path=/bin/bash macho=%t size=%d primary_cdhash=%s primary_cdhash_ok=%t injected_trust_member=%t",
		isMachO(data), len(data), primaryCDHash, hasPrimaryCDHash, hasPrimaryCDHash && trusted)
}
