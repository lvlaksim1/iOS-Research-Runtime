using System.Buffers.Binary;
using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class TrustCacheBuilderTests
{
    [Fact]
    public void Build_MatchesDarwinVmTrustCacheLayout()
    {
        var builder = new TrustCacheBuilder();
        var result = builder.Build(
        [
            "ffeeddccbbaa99887766554433221100ffeeddcc",
            "00112233445566778899aabbccddeeff00112233"
        ]);

        Assert.Equal(24 + (22 * 2), result.Length);
        Assert.Equal(1u, BinaryPrimitives.ReadUInt32LittleEndian(result.AsSpan(0, 4)));
        Assert.Equal(new string('A', 16), System.Text.Encoding.ASCII.GetString(result, 4, 16));
        Assert.Equal(2u, BinaryPrimitives.ReadUInt32LittleEndian(result.AsSpan(20, 4)));

        var firstEntry = result.AsSpan(24, 22);
        Assert.Equal(
            Convert.FromHexString("00112233445566778899aabbccddeeff00112233"),
            firstEntry[..20].ToArray());
        Assert.Equal(2, firstEntry[20]);
        Assert.Equal(0, firstEntry[21]);

        var secondEntry = result.AsSpan(46, 22);
        Assert.Equal(
            Convert.FromHexString("ffeeddccbbaa99887766554433221100ffeeddcc"),
            secondEntry[..20].ToArray());
        Assert.Equal(2, secondEntry[20]);
        Assert.Equal(0, secondEntry[21]);
    }

    [Theory]
    [InlineData("")]
    [InlineData("abcd")]
    [InlineData("zz112233445566778899aabbccddeeff00112233")]
    public void Build_RejectsInvalidCdHash(string hash)
    {
        var builder = new TrustCacheBuilder();

        Assert.Throws<InvalidDataException>(() => builder.Build([hash]));
    }
}
