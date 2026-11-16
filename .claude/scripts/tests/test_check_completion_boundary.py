"""Tests for .claude/scripts/check_completion_boundary.py.

Transcribed from the completion-boundary rules (`.claude/skills/complete-exec-plan/completion-boundary.md`
「Finding the plan of this branch」「After the boundary」 and `pre-pr` ⑦) before the script existed
(red-first / INV-T02). Each test builds a small git repository: `main` holds a plan, and a branch
works on it.
"""

import io
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_completion_boundary as boundary  # noqa: E402

GIT = shutil.which("git") is not None

PLAN = """\
---
status: active
created: 2026-11-01
completed:
---

# login

## Goal & Scope
x

## Acceptance Criteria
- [{a1}] AC-001: logging in works
- [{a2}] AC-002: [E2E] the login flow works end to end

## Sources

| AC | US（検証可能な bullet） | spec（振る舞いの節） |
|----|------------------------|---------------------|
| AC-001 | `docs/01_requirements/user_stories/US-001_login.md` § AC-001 | `docs/02_spec/app_spec.md` §「Login」 |
| AC-002 [E2E] | n/a（x） | n/a（x） |

## Decision Log
{log}
"""


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")
    return path


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


@unittest.skipUnless(GIT, "git is not available")
class BoundaryRepo(unittest.TestCase):
    """`main` has the plan `exec-plans/active/2026-11-login.md` (nothing checked) and its sources;
    the test then works on branch `feature`."""

    PLAN_ACTIVE = "exec-plans/active/2026-11-login.md"
    PLAN_DONE = "exec-plans/completed/2026-11-login.md"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        git(self.root, "config", "core.autocrlf", "false")
        write(self.root, "docs/01_requirements/user_stories/US-001_login.md", "# US-001\n\n### AC-001\n- x\n")
        write(self.root, "docs/02_spec/app_spec.md", "# spec\n\n## Login\n\nx\n")
        write(self.root, "src/app.py", "print('v0')\n")
        write(self.root, "src/other.py", "print('o0')\n")
        self.write_plan(self.PLAN_ACTIVE, " ", " ")
        self.commit("base")
        git(self.root, "checkout", "-q", "-b", "feature")

    # -- helpers -----------------------------------------------------------------------------

    def write_plan(self, rel, a1, a2, log="- Plan created", status="active"):
        text = PLAN.format(a1=a1, a2=a2, log=log).replace("status: active", f"status: {status}")
        write(self.root, rel, text)

    def commit(self, message, *, allow_empty=False):
        git(self.root, "add", "-A")
        args = ["commit", "-q", "-m", message]
        if allow_empty:
            args.append("--allow-empty")
        git(self.root, *args)
        return git(self.root, "rev-parse", "HEAD").strip()

    def implement(self):
        """The branch implements the plan and ticks every box."""
        write(self.root, "src/app.py", "print('v1')\n")
        self.write_plan(self.PLAN_ACTIVE, "x", "x")
        self.commit("feat: AC-001, AC-002")

    def complete(self, *, extra=None):
        """The complete commit: move the plan to completed/ (optionally carrying another change)."""
        (self.root / self.PLAN_DONE).parent.mkdir(parents=True, exist_ok=True)
        git(self.root, "mv", self.PLAN_ACTIVE, self.PLAN_DONE)
        self.write_plan(self.PLAN_DONE, "x", "x", log="- 人の確認: 全 AC — t, 2026-11-17, x。根拠: 本人記入", status="completed")
        if extra:
            write(self.root, extra, "print('folded in')\n")
        return self.commit("complete: 2026-11-login")

    def on_main(self, rel, text, message="main: change"):
        git(self.root, "checkout", "-q", "main")
        write(self.root, rel, text)
        self.commit(message)
        git(self.root, "checkout", "-q", "feature")
        git(self.root, "merge", "-q", "--no-edit", "main")

    def run_check(self, base="main"):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = boundary.main(["--root", str(self.root), f"--base={base}"])
        return code, buffer.getvalue()


# --------------------------------------------------------------------------- blocking: ❌

class TestImplementationChangeAfterTheBoundaryBlocks(BoundaryRepo):
    """An implementation change the branch made after the complete commit is ❌ (exit 1)."""

    def test_a_commit_after_the_boundary_blocks(self):
        self.implement()
        self.complete()
        write(self.root, "src/app.py", "print('v2')\n")
        self.commit("fix after confirmation")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("src/app.py", out)
        self.assertIn("2026-11-login", out)

    def test_an_uncommitted_change_after_the_boundary_blocks(self):
        self.implement()
        self.complete()
        write(self.root, "src/app.py", "print('v2')\n")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("src/app.py", out)

    def test_an_implementation_change_inside_the_complete_commit_blocks(self):
        self.implement()
        self.complete(extra="src/other.py")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("src/other.py", out)

    def test_a_clean_boundary_passes(self):
        self.implement()
        self.complete()
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("✅", out)

    def test_records_added_to_the_completed_plan_and_context_do_not_count(self):
        self.implement()
        self.complete()
        self.write_plan(self.PLAN_DONE, "x", "x", log="- 人の確認: … 根拠: 本人記入\n- note", status="completed")
        write(self.root, "docs/07_ai_context/CONTEXT.md", "# context\n")
        self.commit("docs: note")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_a_change_that_came_in_by_merging_main_is_not_the_branchs_own(self):
        self.implement()
        self.complete()
        self.on_main("src/other.py", "print('o1')\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)


class TestUncheckedAcInsideTheCompletedPlanBlocks(BoundaryRepo):
    """A completed plan of this branch with an unchecked AC line is ❌ (exit 1)."""

    def test_an_unchecked_ac_in_the_completed_plan_blocks(self):
        self.implement()
        self.complete()
        text = (self.root / self.PLAN_DONE).read_text(encoding="utf-8")
        (self.root / self.PLAN_DONE).write_text(
            text.replace("## Sources", "- [ ] AC-003: re-opened from main\n\n## Sources"), encoding="utf-8"
        )
        self.commit("merge-carried reopen")
        code, out = self.run_check()
        self.assertEqual(code, 1, out)
        self.assertIn("AC-003", out)


# --------------------------------------------------------------------------- not blocking

class TestNonBlockingStates(BoundaryRepo):
    """Every other state is reported and does not set the exit code."""

    def test_a_branch_that_only_adds_a_plan_is_not_held(self):
        write(self.root, "exec-plans/active/2026-11-next.md", PLAN.format(a1=" ", a2=" ", log="- created"))
        self.commit("plan: next")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("➖", out)

    def test_a_plan_less_change_with_a_spec_override_trailer_is_not_held(self):
        write(self.root, "src/app.py", "print('override')\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "chore: x\n\nSpec-Override: tooling")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("➖", out)

    def test_a_code_change_with_no_plan_and_no_trailer_is_reported_not_blocked(self):
        write(self.root, "src/app.py", "print('who?')\n")
        self.commit("chore: x")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("⚠️", out)
        self.assertIn("プランが特定できない", out)

    def test_a_plan_with_every_ac_done_but_not_completed_is_information(self):
        self.implement()
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("ℹ️", out)

    def test_a_plan_with_acs_left_is_an_intermediate_state(self):
        write(self.root, "src/app.py", "print('v1')\n")
        self.write_plan(self.PLAN_ACTIVE, "x", " ")
        self.commit("feat: AC-001")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("⚠️", out)
        self.assertIn("AC-002", out)

    def test_a_sources_file_changed_by_main_after_the_boundary_is_a_warning(self):
        self.implement()
        self.complete()
        self.on_main("docs/02_spec/app_spec.md", "# spec\n\n## Login\n\nchanged\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("⚠️", out)
        self.assertIn("docs/02_spec/app_spec.md", out)


class TestUndetermined(BoundaryRepo):
    """When the branch's state cannot be read, the check blocks and says why."""

    def test_an_unknown_base_blocks_and_says_so(self):
        self.implement()
        code, out = self.run_check(base="no-such-branch")
        self.assertEqual(code, 1, out)
        self.assertIn("could not", out.lower())

    def test_an_option_like_base_is_refused(self):
        code, out = self.run_check(base="--output=x")
        self.assertEqual(code, 1, out)


if __name__ == "__main__":
    unittest.main()
