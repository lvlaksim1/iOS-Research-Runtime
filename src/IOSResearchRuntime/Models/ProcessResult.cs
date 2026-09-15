namespace IOSResearchRuntime.Models;

public sealed record ProcessResult(
    int ExitCode,
    string StandardOutput,
    string StandardError)
{
    public void EnsureSuccess(string operation)
    {
        if (ExitCode == 0)
        {
            return;
        }

        var details = string.IsNullOrWhiteSpace(StandardError)
            ? StandardOutput
            : StandardError;

        throw new InvalidOperationException(
            $"{operation} завершилась с кодом {ExitCode}.{Environment.NewLine}{details}");
    }
}
