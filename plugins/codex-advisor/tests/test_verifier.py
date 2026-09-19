from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
VERIFIER = Path("plugins/codex-advisor/scripts/verify.py")


class VerifierRegressionTests(unittest.TestCase):
    def copied_repo(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        shutil.copytree(REPO, Path(temporary.name) / "repo", dirs_exist_ok=True)
        return temporary

    def run_verifier(self, repo: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(repo / VERIFIER)],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_rejects_non_object_marketplace_entry(self) -> None:
        with self.copied_repo() as temporary:
            repo = Path(temporary) / "repo"
            marketplace = repo / ".agents" / "plugins" / "marketplace.json"
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            data["plugins"] = [42]
            marketplace.write_text(json.dumps(data), encoding="utf-8")

            result = self.run_verifier(repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("marketplace plugin entry must be an object", result.stdout)

    def test_rejects_invalid_ui_yaml(self) -> None:
        with self.copied_repo() as temporary:
            repo = Path(temporary) / "repo"
            ui = repo / "plugins" / "codex-advisor" / "skills" / "orchestration" / "agents" / "openai.yaml"
            ui.write_text("interface: [unterminated\n", encoding="utf-8")

            result = self.run_verifier(repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid YAML in skill UI metadata", result.stdout)


if __name__ == "__main__":
    unittest.main()
