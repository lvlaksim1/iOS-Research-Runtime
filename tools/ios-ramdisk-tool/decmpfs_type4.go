package main

import (
    "bytes"
    "compress/zlib"
    "encoding/binary"
    "fmt"
    "io"
)

func decodeZlibResourceFork(resourceFork []byte, uncompressedSize uint64) ([]byte, error) {
    const (
        chunkSize = uint64(65536)
        blockCountOffset = uint64(0x104)
        tableOffset = uint64(0x108)
    )
    if uncompressedSize > uint64(^uint(0)>>1) { return nil, fmt.Errorf("decmpfs type 4 is too large: %d", uncompressedSize) }
    if uint64(len(resourceFork)) < tableOffset { return nil, fmt.Errorf("decmpfs type 4 resource fork is too short: %d", len(resourceFork)) }
    dataOffset := uint64(binary.BigEndian.Uint32(resourceFork[0:4]))
    if dataOffset != 0x100 { return nil, fmt.Errorf("decmpfs type 4 data offset 0x%x != expected 0x100", dataOffset) }
    blockCount := uint64(binary.LittleEndian.Uint32(resourceFork[blockCountOffset:tableOffset]))
    expectedBlocks := (uncompressedSize + chunkSize - 1) / chunkSize
    if blockCount != expectedBlocks { return nil, fmt.Errorf("decmpfs type 4 block count %d != expected %d", blockCount, expectedBlocks) }
    tableEnd := tableOffset + blockCount*8
    if tableEnd > uint64(len(resourceFork)) { return nil, fmt.Errorf("decmpfs type 4 block table ends at %d beyond resource fork %d", tableEnd, len(resourceFork)) }

    out := make([]byte, 0, int(uncompressedSize))
    for block := uint64(0); block < blockCount; block++ {
        at := tableOffset + block*8
        relative := uint64(binary.LittleEndian.Uint32(resourceFork[at:at+4]))
        storedSize := uint64(binary.LittleEndian.Uint32(resourceFork[at+4:at+8]))
        start := blockCountOffset + relative
        end := start + storedSize
        if start < tableEnd || end < start || end > uint64(len(resourceFork)) {
            return nil, fmt.Errorf("decmpfs type 4 block %d range [%d,%d) is invalid", block, start, end)
        }
        expected := min(chunkSize, uncompressedSize-uint64(len(out)))
        stored := resourceFork[start:end]
        var chunk []byte
        if len(stored) > 0 && stored[0] == 0xff {
            if uint64(len(stored)-1) != expected { return nil, fmt.Errorf("decmpfs type 4 block %d raw payload %d bytes, expected %d", block, len(stored)-1, expected) }
            chunk = stored[1:]
        } else {
            zr, err := zlib.NewReader(bytes.NewReader(stored))
            if err != nil { return nil, fmt.Errorf("decmpfs type 4 block %d zlib header: %w", block, err) }
            decoded, readErr := io.ReadAll(io.LimitReader(zr, int64(chunkSize)+1))
            closeErr := zr.Close()
            if readErr != nil { return nil, fmt.Errorf("decmpfs type 4 block %d zlib read: %w", block, readErr) }
            if closeErr != nil { return nil, fmt.Errorf("decmpfs type 4 block %d zlib close: %w", block, closeErr) }
            if uint64(len(decoded)) != expected { return nil, fmt.Errorf("decmpfs type 4 block %d decoded %d bytes, expected %d", block, len(decoded), expected) }
            chunk = decoded
        }
        out = append(out, chunk...)
    }
    if uint64(len(out)) != uncompressedSize { return nil, fmt.Errorf("decmpfs type 4 decoded %d bytes, expected %d", len(out), uncompressedSize) }
    return out, nil
}
