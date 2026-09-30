package main

import (
    "bytes"
    "compress/zlib"
    "encoding/binary"
    "testing"
)

func TestDecodeZlibResourceForkMultiChunk(t *testing.T) {
    plain := append(bytes.Repeat([]byte{0x41}, 65536), bytes.Repeat([]byte{0x42}, 12345)...)
    chunks := [][]byte{plain[:65536], plain[65536:]}
    compressed := make([][]byte, len(chunks))
    for i, chunk := range chunks {
        var buf bytes.Buffer
        zw := zlib.NewWriter(&buf)
        if _, err := zw.Write(chunk); err != nil { t.Fatal(err) }
        if err := zw.Close(); err != nil { t.Fatal(err) }
        compressed[i] = buf.Bytes()
    }

    const base = 0x104
    const table = 0x108
    tableEnd := table + len(chunks)*8
    fork := make([]byte, tableEnd)
    binary.BigEndian.PutUint32(fork[0:4], 0x100)
    binary.LittleEndian.PutUint32(fork[base:table], uint32(len(chunks)))
    cursor := tableEnd
    for i, chunk := range compressed {
        at := table + i*8
        binary.LittleEndian.PutUint32(fork[at:at+4], uint32(cursor-base))
        binary.LittleEndian.PutUint32(fork[at+4:at+8], uint32(len(chunk)))
        fork = append(fork, chunk...)
        cursor += len(chunk)
    }
    fork = append(fork, make([]byte, 50)...)

    got, err := decodeZlibResourceFork(fork, uint64(len(plain)))
    if err != nil { t.Fatal(err) }
    if !bytes.Equal(got, plain) { t.Fatalf("decoded payload mismatch: got %d bytes", len(got)) }
}

func TestDecodeZlibResourceForkRejectsDeclaredSizeMismatch(t *testing.T) {
    fork := make([]byte, 0x108)
    binary.BigEndian.PutUint32(fork[0:4], 0x100)
    binary.LittleEndian.PutUint32(fork[0x104:0x108], 0)
    if _, err := decodeZlibResourceFork(fork, 1); err == nil { t.Fatal("expected block-count mismatch") }
}
