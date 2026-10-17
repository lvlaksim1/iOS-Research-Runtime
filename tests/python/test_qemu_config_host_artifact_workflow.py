"""Static checks for the Windows QEMU Meson-header evidence artifact.

This test checks workflow structure only. It does not claim a successful CI
upload, generated header contents, guest execution, or iOS system boot.
"""

from pathlib import Path
import re
import unittest


WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/qemu-sptm-windows.yml"
STEP_NAME = "Upload generated QEMU Meson configuration header"


def _step_block(text: str, name: str) -> str:
    pattern = rf"(?m)^      - name: {re.escape(name)}\s*$"
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one step {name!r}, got {len(matches)}")
    start = matches[0].start()
    following = re.search(r"(?m)^      - name: ", text[matches[0].end():])
    end = matches[0].end() + following.start() if following else len(text)
    return text[start:end]


class ConfigHostArtifactWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.step = _step_block(cls.workflow, STEP_NAME)

    def test_upload_is_unconditional_on_previous_gate(self):
        self.assertRegex(self.step, r"(?m)^        if: always\(\)$")

    def test_upload_uses_supported_artifact_action(self):
        self.assertRegex(self.step, r"(?m)^        uses: actions/upload-artifact@v4$")

    def test_only_exact_generated_header_is_uploaded(self):
        self.assertRegex(self.step, r"(?m)^          path: qemu-sptm/build/config-host\.h$")
        self.assertNotIn("**", self.step)
        self.assertNotIn("secrets.", self.step)

    def test_missing_header_is_not_silently_claimed_present(self):
        self.assertRegex(self.step, r"(?m)^          if-no-files-found: warn$")

    def test_artifact_name_and_retention(self):
        self.assertRegex(self.step, r"(?m)^          name: qemu-sptm-config-host-header$")
        self.assertRegex(self.step, r"(?m)^          retention-days: 14$")

    def test_upload_occurs_after_trace_checker_before_cache_save(self):
        names = [
            "Build qemu-sptm",
            "Verify compiled QEMU NVMe IRQ trace capability",
            STEP_NAME,
            "Save QEMU build cache",
        ]
        positions = [self.workflow.index(f"      - name: {name}\n") for name in names]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
