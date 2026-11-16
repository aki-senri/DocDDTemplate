#!/usr/bin/env python3
"""check_completion_boundary.py — the mechanical part of the completion boundary (`pre-pr` ⑦).

The rules live in `.claude/skills/complete-exec-plan/completion-boundary.md`; this script reads git
and the plan files and reports where the branch stands. `pre-pr` ⑦ and the CI workflow both run it,
so the judgement is written once.

| Finding                                                                  | Level | Blocks |
|--------------------------------------------------------------------------|-------|--------|
| A plan this branch completed, with an implementation change after its    | ❌    | yes    |
| complete commit (committed by the branch, or uncommitted) or inside it   |       |        |
| A plan this branch completed, with an unchecked AC line                  | ❌    | yes    |
| The branch's state cannot be read (no git, unknown base)                 | ❌    | yes    |
| A plan this branch completed, a `## Sources` file changed since then     | ⚠️    | no     |
| A plan in active/ with ACs left (an intermediate state)                  | ⚠️    | no     |
| Code changed, no plan found, no `Spec-Override:` trailer                 | ⚠️    | no     |
| A plan in active/ with every AC done, not completed yet                  | ℹ️    | no     |
| A move into completed/ not committed yet                                 | ℹ️    | no     |
| A plan this branch has not started; a plan-less change                   | ➖    | no     |

Exit code 1 when anything blocks, 0 otherwise. Only the ❌ rows block: they are read from git and the
plan files, not judged from prose. What is a reading — whether a changed section still says what the
human confirmed — is reported for the human.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

#: What "implementation" excludes: the plans' own records and the CONTEXT.md update the complete
#: commit carries (completion-boundary.md「After the boundary」).
NOT_IMPLEMENTATION = (":(exclude)exec-plans/", ":(exclude)docs/07_ai_context/CONTEXT.md")
#: What a branch may change and still not have started a plan, or be plan-less without a trailer.
DOCS_ONLY = (":(exclude)exec-plans/", ":(exclude)docs/")

AC_LINE = re.compile(r"^- \[( |x|X)\] (AC-\d{3}):", re.M)
SOURCES_PATH = re.compile(r"`([^`\s]+\.md)`")
DOC_ONLY_MARK = "E2E: n/a (documentation-only)"


class Undetermined(Exception):
    """The branch's state cannot be read; every check blocks."""


@dataclass
class Report:
    blocking: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)
    none: list[str] = field(default_factory=list)


class Repo:
    def __init__(self, root: Path, base: str):
        self.root = root
        self.base = base

    def git(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.root), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError as error:
            raise Undetermined("git is not available") from error
        if result.returncode != 0:
            detail = (result.stderr or "").strip().splitlines()
            raise Undetermined(f"git {args[0]} failed{': ' + detail[0] if detail else ''}")
        return result.stdout

    def lines(self, *args: str) -> list[str]:
        return [line for line in self.git(*args).splitlines() if line.strip()]


def is_plan(path: Path) -> bool:
    try:
        return "## Acceptance Criteria" in path.read_text(encoding="utf-8")
    except OSError:
        return False


def sources_paths(text: str) -> set[str]:
    """The files a plan's `## Sources` table names (the whole section, cell by cell)."""
    match = re.search(r"^## Sources\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return set()
    return {path for path in SOURCES_PATH.findall(match.group(1)) if "/" in path}


def check(root: Path, base: str) -> Report:
    if base.startswith("-"):
        raise Undetermined(f"{base!r} is not a branch name")
    repo = Repo(root, base)
    toplevel = Path(repo.git("rev-parse", "--show-toplevel").strip()).resolve()
    if toplevel != root.resolve():
        raise Undetermined(f"{root} is not the top of its git repository ({toplevel})")
    repo.git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    merge_base = repo.git("merge-base", base, "HEAD").strip()
    report = Report()

    # -- the plans of this branch (completion-boundary.md「Finding the plan of this branch」) -------
    active = set(repo.lines("diff", "--name-only", "--diff-filter=AM", merge_base, "--", "exec-plans/active/"))
    active |= set(repo.lines("ls-files", "--others", "--", "exec-plans/active/"))
    completed = {
        path
        for path in repo.lines("diff", "--name-only", "-M", "--diff-filter=AR", f"{base}...HEAD", "--", "exec-plans/")
        if path.startswith("exec-plans/completed/")
    }
    pending_moves = set()
    for line in repo.lines("status", "--porcelain", "-uall", "--", "exec-plans/"):
        target = line[3:].split(" -> ")[-1].strip().strip('"')
        if target.startswith("exec-plans/completed/") and (line[0] in "AR?" or line[:2] == "??"):
            pending_moves.add(target)
    pending_moves -= completed
    active = {p for p in active if p.endswith(".md") and is_plan(root / p)}
    completed = {p for p in completed if p.endswith(".md") and is_plan(root / p)}
    pending_moves = {p for p in pending_moves if p.endswith(".md") and is_plan(root / p)}

    for plan in sorted(completed):
        check_completed(repo, root, plan, report)
    for plan in sorted(pending_moves):
        report.info.append(
            f"{Path(plan).name} → completed/ への移動が未コミット（complete-exec-plan の中断。再開してコミットする）"
        )
    for plan in sorted(active):
        check_active(repo, root, merge_base, plan, report)

    if not (active or completed or pending_moves):
        check_plan_less(repo, merge_base, report)
    return report


def check_completed(repo: Repo, root: Path, plan: str, report: Report) -> None:
    name = Path(plan).name
    boundary = repo.git("log", "-1", "--diff-filter=AR", "--format=%H", f"{repo.base}..HEAD", "--", plan).strip()
    if not boundary:
        report.blocking.append(f"{name} → complete コミット（completed/ へ移したコミット）が見つからない")
        return
    short = boundary[:7]
    after = set(
        repo.lines(
            "log", "--no-merges", "--format=", "--name-only", f"{boundary}..HEAD", f"^{repo.base}",
            "--", ".", *NOT_IMPLEMENTATION,
        )
    )
    after |= {line[3:].split(" -> ")[-1].strip().strip('"')
              for line in repo.lines("status", "--porcelain", "--", ".", *NOT_IMPLEMENTATION)}
    inside = set(repo.lines("show", "--format=", "--name-only", boundary, "--", ".", *NOT_IMPLEMENTATION))
    blocked = False
    if after:
        blocked = True
        report.blocking.append(
            f"{name} → complete {short} の後に実装変更: {', '.join(sorted(after))}（再オープンして確認をやり直す）"
        )
    if inside:
        blocked = True
        report.blocking.append(
            f"{name} → complete コミット {short} 自体に実装変更: {', '.join(sorted(inside))}（再オープンして確認をやり直す）"
        )
    text = (root / plan).read_text(encoding="utf-8")
    unchecked = [ac for mark, ac in AC_LINE.findall(text) if mark == " "]
    if unchecked:
        blocked = True
        report.blocking.append(
            f"{name} → completed のプランに未チェックの {', '.join(unchecked)}（再オープンする）"
        )
    changed = set(repo.lines("diff", "--name-only", "--no-renames", boundary, "HEAD"))
    moved_sources = sorted(sources_paths(text) & changed)
    if moved_sources:
        report.warnings.append(
            f"{name} → complete {short} の後に ## Sources のファイルが変更: {', '.join(moved_sources)}"
            "（確認がなお有効か、再オープンするかを人が判断）"
        )
    if not blocked:
        report.passed.append(f"{name} → complete {short} 以降の実装変更なし")


def check_active(repo: Repo, root: Path, merge_base: str, plan: str, report: Report) -> None:
    name = Path(plan).name
    text = (root / plan).read_text(encoding="utf-8")
    marks = AC_LINE.findall(text)
    unchecked = [ac for mark, ac in marks if mark == " "]
    if marks and not unchecked:
        report.info.append(f"{name} → 全 AC 完了・未 complete（マージ前に人の確認 → /complete-exec-plan）")
        return
    tracked = bool(repo.lines("ls-files", "--", plan))
    if tracked:
        ticked = any(
            line.startswith("+") and re.match(r"^\+- \[(x|X)\] AC-\d{3}:", line)
            for line in repo.git("diff", merge_base, "--", plan).splitlines()
        )
    else:
        ticked = any(mark != " " for mark, _ in marks)
    outside = repo.lines("diff", "--name-only", merge_base, "--", ".", *DOCS_ONLY)
    outside += repo.lines("ls-files", "--others", "--exclude-standard", "--", ".", *DOCS_ONLY)
    docs_changed = repo.lines("diff", "--name-only", merge_base, "--", "docs/")
    docs_changed += repo.lines("ls-files", "--others", "--exclude-standard", "--", "docs/")
    documentation_only = DOC_ONLY_MARK in text
    if not ticked and not outside and not (documentation_only and docs_changed):
        report.none.append(f"{name} → 確認対象なし（プランの追加・AC の再オープンのみ）")
        return
    report.warnings.append(f"{name} → {', '.join(unchecked)} が未完了（途中状態ではマージしない）")


def check_plan_less(repo: Repo, merge_base: str, report: Report) -> None:
    outside = repo.lines("diff", "--name-only", merge_base, "--", ".", *DOCS_ONLY)
    outside += repo.lines("ls-files", "--others", "--exclude-standard", "--", ".", *DOCS_ONLY)
    if not outside:
        report.none.append("確認対象なし（プランを持たない文書の変更）")
        return
    messages = repo.git("log", "--format=%B", f"{repo.base}..HEAD")
    if re.search(r"^Spec-Override:", messages, re.M):
        report.none.append("n/a（プラン無しの変更 — Spec-Override の記録あり）")
        return
    report.warnings.append(
        "プランが特定できない — コードを変えているが、このブランチのプランも Spec-Override の記録も無い"
        "（どのプランの実装かを人に確認する）"
    )


def format_report(report: Report, base: str) -> str:
    out = ["=== Completion boundary (pre-pr ⑦) ===", f"Base: {base}", ""]
    for mark, items in (("❌", report.blocking), ("⚠️", report.warnings), ("ℹ️", report.info),
                        ("✅", report.passed), ("➖", report.none)):
        out.extend(f"{mark} {item}" for item in items)
    if not any((report.blocking, report.warnings, report.info, report.passed, report.none)):
        out.append("➖ 確認対象なし")
    out.append("---")
    out.append(f"Overall: ❌ {len(report.blocking)} blocking" if report.blocking else "Overall: ✅ nothing blocks")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="The mechanical completion-boundary check (pre-pr ⑦, CI): blocks an implementation "
        "change after a plan's complete commit and an unchecked AC inside a completed plan.",
    )
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    parser.add_argument(
        "--base", required=True, metavar="REF",
        help="the branch the PR merges into, current (e.g. origin/main after git fetch)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        report = check(root, args.base)
    except Undetermined as error:
        print("=== Completion boundary (pre-pr ⑦) ===")
        print(f"❌ could not determine the branch's state: {error} — every check blocks until this is fixed")
        print("---\nOverall: ❌ undetermined")
        return 1
    print(format_report(report, args.base))
    return 1 if report.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
