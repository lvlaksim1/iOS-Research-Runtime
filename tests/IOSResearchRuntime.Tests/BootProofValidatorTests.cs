using IOSResearchRuntime.Services;

namespace IOSResearchRuntime.Tests;

public sealed class BootProofValidatorTests
{
    [Fact]
    public void Validate_AcceptsDarwinRootProof()
    {
        var validator = new BootProofValidator();

        var result = validator.Validate(
        [
            "Darwin Kernel Version 27.0.0: root:xnu-13432.1.9~3/RELEASE_ARM64_T8142",
            "root",
            "System bin dev etc"
        ]);

        Assert.True(result.IsValid);
    }

    [Fact]
    public void Validate_RejectsMissingDarwinKernel()
    {
        var validator = new BootProofValidator();

        var result = validator.Validate(["root"]);

        Assert.False(result.IsValid);
        Assert.Contains("Darwin Kernel Version", result.Message);
    }

    [Fact]
    public void Validate_RejectsNonRootIdentity()
    {
        var validator = new BootProofValidator();

        var result = validator.Validate(
        [
            "Darwin Kernel Version 27.0.0",
            "mobile"
        ]);

        Assert.False(result.IsValid);
        Assert.Contains("whoami=root", result.Message);
    }
}
