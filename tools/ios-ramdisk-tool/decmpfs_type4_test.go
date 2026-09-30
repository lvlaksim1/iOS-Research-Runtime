package main

import (
    "bytes"
    "compress/zlib"
    "encoding/binary"
    "testing"
)

func buildType4Fork(t *testing.T, plain []byte, raw map[int]bool) []byte {
    t.Helper()
    chunks := make([][]byte, 0, (len(plain)+65535)/65536)
    for start := 0; start < len(plain); start += 65536 {
        end := min(start+65536, len(plain))
        chunk := plain[start:end]
        if raw[len(chunks)] {
            chunks = append(chunks, append([]byte{0xff}, chunk...))
            continue
        }
        var buf bytes.Buffer
        zw := zlib.NewWriter(&buf)
        if _, err := zw.Write(chunk); err != nil { t.Fatal(err) }
        if err := zw.Close(); err != nil { t.Fatal(err) }
        chunks = append(chunks, buf.Bytes())
    }
    const base = 0x104
    const table = 0x108
    tableEnd := table + len(chunks)*8
    fork := make([]byte, tableEnd)
    binary.BigEndian.PutUint32(fork[0:4], 0x100)
    binary.LittleEndian.PutUint32(fork[base:table], uint32(len(chunks)))
    cursor := tableEnd
    for i, chunk := range chunks {
        at := table + i*8
        binary.LittleEndian.PutUint32(fork[at:at+4], uint32(cursor-base))
        binary.LittleEndian.PutUint32(fork[at+4:at+8], uint32(len(chunk)))
        fork = append(fork, chunk...)
        cursor += len(chunk)
    }
    return append(fork, make([]byte, 50)...)
}

func TestDecodeZlibResourceForkMultiChunk(t *testing.T) {
    plain := append(bytes.Repeat([]byte{0x41}, 65536), bytes.Repeat([]byte{0x42}, 12345)...)
    got, err := decodeZlibResourceFork(buildType4Fork(t, plain, nil), uint64(len(plain)))
    if err != nil { t.Fatal(err) }
    if !bytes.Equal(got, plain) { t.Fatalf("decoded payload mismatch: got %d bytes", len(got)) }
}

func TestDecodeZlibResourceForkMixedRawAndZlibChunks(t *testing.T) {
    plain := append(bytes.Repeat([]byte{0x31}, 65536), bytes.Repeat([]byte{0x32}, 4097)...)
    got, err := decodeZlibResourceFork(buildType4Fork(t, plain, map[int]bool{0:true}), uint64(len(plain)))
    if err != nil { t.Fatal(err) }
    if !bytes.Equal(got, plain) { t.Fatalf("decoded mixed payload mismatch: got %d bytes", len(got)) }
}

func TestDecodeZlibResourceForkRejectsRawSizeMismatch(t *testing.T) {
    plain := bytes.Repeat([]byte{0x55}, 10)
    fork := buildType4Fork(t, plain, map[int]bool{0:true})
    binary.LittleEndian.PutUint32(fork[0x10c:0x110], 10)
    if _, err := decodeZlibResourceFork(fork, uint64(len(plain))); err == nil { t.Fatal("expected raw-size mismatch") }
}

func TestDecodeZlibResourceForkRejectsDeclaredSizeMismatch(t *testing.T) {
    fork := make([]byte, 0x108)
    binary.BigEndian.PutUint32(fork[0:4], 0x100)
    binary.LittleEndian.PutUint32(fork[0x104:0x108], 0)
    if _, err := decodeZlibResourceFork(fork, 1); err == nil { t.Fatal("expected block-count mismatch") }
}
