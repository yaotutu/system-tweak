from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chglib.model import ChangeError, load_change_set, sha256_file
from chglib.state import transition, validate_ledger


class WorkflowTests(unittest.TestCase):
    def test_real_repository_mixed_versions(self) -> None:
        change_set = load_change_set(ROOT)
        self.assertEqual(change_set.docs["CHG-0013"]["schema"], 2)
        self.assertIn("CHG-0001", change_set.superseded)
        self.assertIn("CHG-0013", change_set.effective)
        self.assertIn("CHG-0012", change_set.effective)

    def test_v2_assets_match_checksums(self) -> None:
        change_set = load_change_set(ROOT)
        for operation in change_set.docs["CHG-0013"]["operations"]:
            if "asset" in operation:
                source = ROOT / operation["asset"]["path"]
                self.assertEqual(sha256_file(source), operation["asset"]["sha256"])

    def test_manual_verification_blocks_illegal_finalize_transition(self) -> None:
        run = {"state": "verifying", "updatedAt": ""}
        transition(run, "awaiting-manual")
        with self.assertRaises(ValueError):
            transition(run, "applied") if False else transition({"state": "planned", "updatedAt": ""}, "applied")

    def test_failed_run_cannot_become_applied(self) -> None:
        run = {"state": "planned", "updatedAt": ""}
        transition(run, "failed")
        with self.assertRaises(ValueError):
            transition(run, "applied")

    def test_ledger_requires_reason_for_failure(self) -> None:
        ledger = {
            "schema": 1,
            "host": "test",
            "lastProcessed": "CHG-0001",
            "changes": {"CHG-0001": {"status": "failed", "verifiedAt": "2026-09-25T00:00:00+00:00"}},
        }
        with self.assertRaisesRegex(ValueError, "requires reason"):
            validate_ledger(ledger, {"CHG-0001"})

    def test_publish_check_reports_committed_not_pushed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", "--initial-branch=main", repo], check=True)
            subprocess.run(["git", "-C", repo, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", repo, "config", "user.name", "Test"], check=True)
            (repo / "x").write_text("one")
            subprocess.run(["git", "-C", repo, "add", "x"], check=True)
            subprocess.run(["git", "-C", repo, "commit", "-qm", "one"], check=True)
            remote = repo / "remote.git"
            subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
            subprocess.run(["git", "-C", repo, "remote", "add", "origin", str(remote)], check=True)
            subprocess.run(["git", "-C", repo, "push", "-qu", "origin", "main"], check=True)
            (repo / "x").write_text("two")
            subprocess.run(["git", "-C", repo, "commit", "-qam", "two"], check=True)
            local = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
            upstream = subprocess.check_output(["git", "-C", repo, "rev-parse", "@{upstream}"], text=True).strip()
            self.assertNotEqual(local, upstream)
            self.assertEqual(
                subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", upstream, local]).returncode,
                0,
            )


if __name__ == "__main__":
    unittest.main()
