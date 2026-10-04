"""Acceptance tests for .claude/scripts/check_doc_lint.py.

Each test names the AC it transcribes (exec-plans/active/2026-09-doc-lint-scripts.dev.md).
Written from the AC lines before the implementation existed (red-first / INV-T02).
"""

import ast
import re
import io
import os
import sys
import sysconfig
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_doc_lint as lint  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")
    return path


def checks_of(findings, check):
    return [f for f in findings if f.check == check]


class TempRepo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


# --------------------------------------------------------------------------- AC-001

class TestAC001DefaultRange(TempRepo):
    """AC-001: 既定の検査範囲は .claude/skills/**/*.md・ルート *.md・docs/**/*.md・
    exec-plans/**/*.md。存在しない範囲は失敗ではなく skip する。"""

    def test_covers_the_four_ranges(self):
        write(self.root, ".claude/skills/demo/SKILL.md", "# skill\n")
        write(self.root, ".claude/skills/demo/extra.md", "# extra\n")
        write(self.root, "CLAUDE.md", "# root\n")
        write(self.root, "docs/02_spec/app_spec.md", "# spec\n")
        write(self.root, "exec-plans/active/2026-09-x.md", "# plan\n")

        found = {p.relative_to(self.root).as_posix() for p in lint.default_paths(self.root)}

        self.assertEqual(
            found,
            {
                ".claude/skills/demo/SKILL.md",
                ".claude/skills/demo/extra.md",
                "CLAUDE.md",
                "docs/02_spec/app_spec.md",
                "exec-plans/active/2026-09-x.md",
            },
        )

    def test_missing_range_is_skipped_not_an_error(self):
        write(self.root, "README.md", "# only a root file\n")

        paths = lint.default_paths(self.root)

        self.assertEqual([p.relative_to(self.root).as_posix() for p in paths], ["README.md"])

    def test_excludes_non_markdown_and_nested_root_files(self):
        write(self.root, "README.md", "# root\n")
        write(self.root, "notes.txt", "not markdown\n")
        write(self.root, "vendor/other.md", "outside the four ranges\n")

        paths = {p.relative_to(self.root).as_posix() for p in lint.default_paths(self.root)}

        self.assertEqual(paths, {"README.md"})

    def test_uses_only_standard_library_imports(self):
        source = (Path(lint.__file__)).read_text(encoding="utf-8")
        stdlib = set(sys.stdlib_module_names)
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported.add(node.module.split(".")[0])

        self.assertEqual(sorted(imported - stdlib), [])
        self.assertNotIn("site-packages", sysconfig.get_paths()["stdlib"])  # sanity


# --------------------------------------------------------------------------- AC-002 (C1)

class TestAC002Links(TempRepo):
    """AC-002: 解決できない相対 Markdown リンクを ❌ で file:line 付き報告。
    fenced code / プレースホルダ / 外部 URL / アンカーのみ / Decision・Progress Log は対象外。"""

    def test_reports_unresolvable_relative_link_with_line_number(self):
        target = write(self.root, "docs/a.md", """\
            # a

            see [gone](./missing.md) for details
            """)

        findings = lint.check_links(target, target.read_text(encoding="utf-8"), self.root)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "C1")
        self.assertEqual(findings[0].level, "error")
        self.assertEqual(findings[0].line, 3)
        self.assertIn("missing.md", findings[0].message)

    def test_resolvable_link_is_not_reported(self):
        write(self.root, "docs/b.md", "# b\n")
        target = write(self.root, "docs/a.md", "see [b](./b.md)\n")

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_link_with_anchor_suffix_resolves_to_the_file(self):
        write(self.root, "docs/b.md", "# b\n")
        target = write(self.root, "docs/a.md", "see [b](b.md#some-heading)\n")

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_links_inside_a_fenced_code_block_are_skipped(self):
        target = write(self.root, "docs/a.md", """\
            # template

            ```markdown
            | AC-001 | [US](docs/01_requirements/user_stories/US-XXX_name.md) |
            [nope](./also-missing.md)
            ```
            """)

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_placeholder_links_are_skipped(self):
        target = write(self.root, "docs/a.md", """\
            see [plan](exec-plans/active/YYYY-MM-{name}.md)
            see [us](docs/01_requirements/user_stories/US-XXX_foo.md)
            see [ac](docs/02_spec/AC-NNN.md)
            """)

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_external_and_anchor_only_links_are_skipped(self):
        target = write(self.root, "docs/a.md", """\
            [ext](https://example.com/x.md)
            [ext2](http://example.com/y.md)
            [mail](mailto:someone@example.com)
            [anchor](#section)
            """)

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_link_escaping_to_a_prefix_sharing_sibling_is_skipped(self):
        """リポジトリ外は検証不能として skip する。文字列の前方一致で判定すると、
        名前の先頭を共有する兄弟ディレクトリ（`repo` と `repo2`）を「内側」と誤判定する
        （PR #40 Copilot 指摘 r4116315395）。"""
        repo = self.root / "repo"
        sibling = self.root / "repo2"
        sibling.mkdir(parents=True, exist_ok=True)
        target = write(repo, "docs/a.md", "see [outside](../../repo2/missing.md)\n")

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), repo), [])

    def test_link_escaping_above_the_repository_is_skipped(self):
        target = write(self.root, "docs/a.md", "see [outside](../../elsewhere/missing.md)\n")

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_plan_files_are_out_of_range(self):
        """plan は作業ノートであり参照文書ではない（AC-002 改訂。理由は Decision Log）。"""
        target = write(self.root, "exec-plans/active/2026-09-x.md", """\
            # plan

            body [gone](./missing-body.md)

            ## Decision Log

            - AC-001 done. 参照: [old spec](./deleted-spec.md)
            """)

        self.assertEqual(lint.check_links(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_a_document_outside_exec_plans_is_still_in_range(self):
        target = write(self.root, "docs/a.md", "body [gone](./missing-body.md)\n")

        self.assertEqual(len(lint.check_links(target, target.read_text(encoding="utf-8"), self.root)), 1)


# --------------------------------------------------------------------------- AC-003 (C2)

class TestAC003Tables(TempRepo):
    """AC-003: header 行と列数の異なる body 行を ❌。`\\|` エスケープと
    インラインコード内の `|` は区切りとして数えない。"""

    def test_reports_row_with_wrong_column_count(self):
        target = write(self.root, "docs/a.md", """\
            | a | b | c |
            |---|---|---|
            | 1 | 2 | 3 |
            | 1 | 2 |
            """)

        findings = lint.check_tables(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "C2")
        self.assertEqual(findings[0].level, "error")
        self.assertEqual(findings[0].line, 4)

    def test_consistent_table_is_not_reported(self):
        target = write(self.root, "docs/a.md", """\
            | a | b |
            |---|---|
            | 1 | 2 |
            """)

        self.assertEqual(lint.check_tables(target, target.read_text(encoding="utf-8")), [])

    def test_escaped_pipe_is_not_a_column_separator(self):
        target = write(self.root, "docs/a.md", """\
            | cmd | why |
            |-----|-----|
            | `grep -rn x .claude/ docs/ 2>/dev/null \\|\\| true` | a no-match grep exits 1 |
            """)

        self.assertEqual(lint.check_tables(target, target.read_text(encoding="utf-8")), [])

    def test_pipe_inside_inline_code_is_not_a_column_separator(self):
        target = write(self.root, "docs/a.md", """\
            | pattern | note |
            |---------|------|
            | `a | b` | alternation inside code |
            """)

        self.assertEqual(lint.check_tables(target, target.read_text(encoding="utf-8")), [])

    def test_tables_inside_fenced_code_blocks_are_skipped(self):
        target = write(self.root, "docs/a.md", """\
            ```markdown
            | a | b | c |
            |---|---|---|
            | 1 |
            ```
            """)

        self.assertEqual(lint.check_tables(target, target.read_text(encoding="utf-8")), [])


# --------------------------------------------------------------------------- AC-004 (C3)

class TestAC004LabelReferences(TempRepo):
    """AC-004: 同一行が対象ファイルを名指しているラベル参照が対象ファイルに実在しなければ ❌。
    対象を特定できない参照は skip。Decision・Progress Log は対象外。"""

    def setUp(self):
        super().setUp()
        write(self.root, ".claude/skills/create-exec-plan/SKILL.md", """\
            # create-exec-plan

            ### Q3d: sources
            2b. collect the sources
            """)

    def test_reports_label_absent_from_the_named_skill(self):
        target = write(self.root, "CLAUDE.md", """\
            | 地点 | タイミング |
            |------|-----------|
            | `create-exec-plan`（Q2b） | プラン確定前 |
            """)

        findings = lint.check_labels(target, target.read_text(encoding="utf-8"), self.root)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "C3")
        self.assertEqual(findings[0].level, "error")
        self.assertEqual(findings[0].line, 3)
        self.assertIn("Q2b", findings[0].message)

    def test_label_present_in_the_named_skill_is_not_reported(self):
        target = write(self.root, "CLAUDE.md", "`create-exec-plan`（Q3d） でプラン確定前に検査する\n")

        self.assertEqual(lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_slash_command_form_names_the_target(self):
        target = write(self.root, "CLAUDE.md", "/create-exec-plan の Q9z を参照\n")

        findings = lint.check_labels(target, target.read_text(encoding="utf-8"), self.root)

        self.assertEqual(len(findings), 1)
        self.assertIn("Q9z", findings[0].message)

    def test_relative_md_link_names_the_target(self):
        write(self.root, ".claude/skills/x/ac-sources.md", "# sources\n\nStep 3 の話\n")
        target = write(self.root, ".claude/skills/x/SKILL.md", "[ac-sources](ac-sources.md) の Step 9 を見る\n")

        findings = lint.check_labels(target, target.read_text(encoding="utf-8"), self.root)

        self.assertEqual(len(findings), 1)
        self.assertIn("Step 9", findings[0].message)

    def test_label_without_a_named_target_is_skipped(self):
        target = write(self.root, "CLAUDE.md", "Step 0b で検査する（対象ファイルの名指しが無い行）\n")

        self.assertEqual(lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_doc_inv_and_inv_t_labels_are_checked_against_the_named_file(self):
        write(self.root, ".claude/skills/check-doc-invariants/SKILL.md", "### DOC-INV-001: reference direction\n")
        target = write(self.root, "CLAUDE.md", "`check-doc-invariants` の DOC-INV-042 が検査する\n")

        findings = lint.check_labels(target, target.read_text(encoding="utf-8"), self.root)

        self.assertEqual(len(findings), 1)
        self.assertIn("DOC-INV-042", findings[0].message)

    def test_plan_files_are_out_of_range(self):
        """未完了・完了・履歴のいずれであっても plan は対象外（AC-004 改訂。理由は Decision Log）。"""
        for name, body in [
            ("pending", "- [ ] AC-001: `create-exec-plan` の Q2b を参照する"),
            ("done", "- [x] AC-001: `create-exec-plan` の Q2b を参照する"),
            ("history", "## Decision Log\n\n- AC-008 の本文を `create-exec-plan` の Q2b から Q3d に修正"),
        ]:
            with self.subTest(name):
                target = write(self.root, f"exec-plans/active/2026-09-{name}.md", body + "\n")

                self.assertEqual(
                    lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), []
                )

    def test_target_named_after_the_label_is_not_used(self):
        """対象が label より後ろにある場合は、その対象に対する参照とは読まない
        （例: "(Step 1b / Step 3a), while at `pre-pr` ⑤c" の Step は pre-pr のものではない）。"""
        write(self.root, ".claude/skills/pre-pr/SKILL.md", "### ⑤c Sources record\n")
        target = write(self.root, "CLAUDE.md", "halts the loop (Step 1b / Step 3a), while at `pre-pr` ⑤c a missing record\n")

        self.assertEqual(lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_bare_circled_numbers_are_not_checked(self):
        """裸の丸数字は同一文書の図の箱番号にも使われ、指示と局所列挙を機械的に区別できない。"""
        target = write(self.root, "ONBOARDING.md", "上図のボックス ①②③ はいずれも人が起動する（③ は `create-exec-plan` の前）\n")

        self.assertEqual(lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), [])

    def test_lettered_circled_label_is_checked(self):
        write(self.root, ".claude/skills/pre-pr/SKILL.md", "### ⑤c Sources record\n")
        present = write(self.root, "CLAUDE.md", "`pre-pr` ⑤c が報告する\n")
        absent = write(self.root, "SKILL_FLOW.md", "`pre-pr` ⑤z が報告する\n")

        self.assertEqual(lint.check_labels(present, present.read_text(encoding="utf-8"), self.root), [])
        findings = lint.check_labels(absent, absent.read_text(encoding="utf-8"), self.root)
        self.assertEqual(len(findings), 1)
        self.assertIn("⑤z", findings[0].message)

    def test_labels_inside_fenced_code_blocks_are_skipped(self):
        target = write(self.root, "CLAUDE.md", """\
            ```markdown
            - AC-NNN: `create-exec-plan`（Q2b）を参照する例
            ```
            """)

        self.assertEqual(lint.check_labels(target, target.read_text(encoding="utf-8"), self.root), [])


# --------------------------------------------------------------------------- AC-005 (C4)

class TestAC005MermaidQuoting(TempRepo):
    """AC-005: mermaid のエッジラベル・ノードラベルで、引用されておらず ()[]{} を含むものを ❌。
    PR #35 以前の SKILL_FLOW.md 64・65 行目の2件が検出され、修正後は検出されない。"""

    def test_detects_the_two_unquoted_edge_labels_from_skill_flow(self):
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                IMPL -.->|optional, manual path\\n(no run-exec-plan)| DCR
                DRIVER ==>|mandatory once every AC is - [x]\\n(Step 4a)| DCR
            ```
            """)

        findings = lint.check_mermaid(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 2)
        self.assertEqual([f.line for f in findings], [3, 4])
        self.assertTrue(all(f.check == "C4" and f.level == "error" for f in findings))

    def test_quoted_edge_labels_are_not_reported(self):
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                IMPL -.->|"optional, manual path\\n(no run-exec-plan)"| DCR
                DRIVER ==>|"mandatory once every AC is - [x]\\n(Step 4a)"| DCR
            ```
            """)

        self.assertEqual(lint.check_mermaid(target, target.read_text(encoding="utf-8")), [])

    def test_detects_unquoted_node_label_with_parentheses(self):
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                A[run-tests (red-first)] --> B
            ```
            """)

        findings = lint.check_mermaid(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 3)

    def test_plain_labels_and_quoted_node_labels_are_not_reported(self):
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                A[plain label] -->|simple edge| B["quoted (paren) label"]
                B --> C{decision}
            ```
            """)

        self.assertEqual(lint.check_mermaid(target, target.read_text(encoding="utf-8")), [])

    def test_composite_shapes_are_syntax_not_label_text(self):
        """`START([Project Start])` はスタジアム型ノードであり、ラベルに括弧を含むのではない。"""
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                START([Project Start]) --> INIT
                DB[(database)] --> APP
                SUB{{choice}} --> END
            ```
            """)

        self.assertEqual(lint.check_mermaid(target, target.read_text(encoding="utf-8")), [])

    def test_risky_text_inside_a_composite_shape_is_still_reported(self):
        target = write(self.root, "SKILL_FLOW.md", """\
            ```mermaid
            flowchart TD
                START([Project Start (phase 1)]) --> INIT
            ```
            """)

        findings = lint.check_mermaid(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 3)

    def test_content_outside_a_mermaid_fence_is_not_inspected(self):
        target = write(self.root, "SKILL_FLOW.md", "prose with |an (unquoted) pipe label| inline\n")

        self.assertEqual(lint.check_mermaid(target, target.read_text(encoding="utf-8")), [])


# --------------------------------------------------------------------------- AC-006

class TestAC006MermaidParserOptIn(TempRepo):
    """AC-006: 実パーサ版は --mermaid-parser で opt-in。既定は静的検査のみ。
    利用できない環境では ⚠️ skip として報告し exit code を変えない。"""

    def test_parser_is_not_probed_by_default(self):
        write(self.root, "SKILL_FLOW.md", "```mermaid\nflowchart TD\n  A --> B\n```\n")
        calls = []
        original = lint.mermaid_parser_available
        lint.mermaid_parser_available = lambda: calls.append(1) or False
        self.addCleanup(setattr, lint, "mermaid_parser_available", original)

        lint.lint_paths(lint.default_paths(self.root), repo_root=self.root)

        self.assertEqual(calls, [])

    def test_unavailable_parser_reports_a_warning_and_keeps_exit_code_zero(self):
        write(self.root, "SKILL_FLOW.md", "```mermaid\nflowchart TD\n  A --> B\n```\n")
        original = lint.mermaid_parser_available
        lint.mermaid_parser_available = lambda: False
        self.addCleanup(setattr, lint, "mermaid_parser_available", original)

        findings = lint.lint_paths(
            lint.default_paths(self.root), repo_root=self.root, mermaid_parser=True
        )

        skips = [f for f in findings if f.level == "warn" and "mermaid" in f.message.lower()]
        self.assertEqual(len(skips), 1)
        self.assertEqual(lint.exit_code(findings), 0)


    def test_skip_note_is_reported_as_a_warning_without_a_fix_hint(self):
        """skip は「直すもの」が無い run 全体の注記なので、violations 扱いも Fix 行も付けない。"""
        write(self.root, "SKILL_FLOW.md", "```mermaid\nflowchart TD\n  A --> B\n```\n")
        original = lint.mermaid_parser_available
        lint.mermaid_parser_available = lambda: False
        self.addCleanup(setattr, lint, "mermaid_parser_available", original)

        findings = lint.lint_paths(
            lint.default_paths(self.root), repo_root=self.root, mermaid_parser=True
        )
        report = lint.format_report(findings, repo_root=self.root, checked=1)
        line = next(l for l in report.splitlines() if "DOC-INV-010" in l)

        self.assertIn("warnings", line)
        self.assertNotIn("violations", line)
        self.assertNotIn("Fix:", report.split("DOC-INV-010")[1].split("DOC-INV-011")[0])


# --------------------------------------------------------------------------- AC-007 (C5)

class TestAC007GrepSnippets(TempRepo):
    """AC-007: fenced bash 内で複数パスを渡す grep -r に 2>/dev/null と || true の
    双方が揃っていないものを ⚠️ 報告のみで出す（exit code に影響しない）。"""

    def test_reports_multi_path_grep_missing_both_guards(self):
        target = write(self.root, "docs/a.md", """\
            ```bash
            grep -rn "pattern" .claude/ exec-plans/active/ docs/ *.md
            ```
            """)

        findings = lint.check_grep_snippets(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "C5")
        self.assertEqual(findings[0].level, "warn")
        self.assertEqual(findings[0].line, 2)

    def test_reports_multi_path_grep_missing_only_the_or_true_guard(self):
        target = write(self.root, "docs/a.md", """\
            ```bash
            grep -rn "pattern" .claude/ docs/ *.md 2>/dev/null
            ```
            """)

        findings = lint.check_grep_snippets(target, target.read_text(encoding="utf-8"))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].level, "warn")

    def test_guarded_grep_is_not_reported(self):
        target = write(self.root, "docs/a.md", """\
            ```bash
            grep -rn "pattern" .claude/ exec-plans/active/ docs/ *.md 2>/dev/null || true
            ```
            """)

        self.assertEqual(lint.check_grep_snippets(target, target.read_text(encoding="utf-8")), [])

    def test_single_path_grep_is_not_reported(self):
        target = write(self.root, "docs/a.md", """\
            ```bash
            grep -n "pattern" CLAUDE.md
            ```
            """)

        self.assertEqual(lint.check_grep_snippets(target, target.read_text(encoding="utf-8")), [])

    def test_grep_outside_a_bash_fence_is_not_inspected(self):
        target = write(self.root, "docs/a.md", "run `grep -rn x .claude/ docs/ *.md` somewhere\n")

        self.assertEqual(lint.check_grep_snippets(target, target.read_text(encoding="utf-8")), [])


# --------------------------------------------------------------------------- AC-008

class TestAC008ExitCode(unittest.TestCase):
    """AC-008: C1〜C4 の違反が1件以上なら 1、⚠️ のみなら 0。"""

    def test_error_finding_yields_one(self):
        findings = [lint.Finding("C1", "error", Path("a.md"), 1, "broken link")]

        self.assertEqual(lint.exit_code(findings), 1)

    def test_warnings_only_yield_zero(self):
        findings = [
            lint.Finding("C5", "warn", Path("a.md"), 1, "unguarded grep"),
            lint.Finding("C4", "warn", Path("b.md"), 1, "mermaid parser unavailable"),
        ]

        self.assertEqual(lint.exit_code(findings), 0)

    def test_no_findings_yield_zero(self):
        self.assertEqual(lint.exit_code([]), 0)


# --------------------------------------------------------------------------- AC-009 / AC-010

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestAC009SkillDefinesTheInvariants(unittest.TestCase):
    """AC-009: check-doc-invariants が C1〜C5 を DOC-INV-007〜011 として定義し、
    Steps でスクリプト実体を呼ぶ。範囲の違いを明記する。"""

    def setUp(self):
        self.text = (REPO_ROOT / ".claude/skills/check-doc-invariants/SKILL.md").read_text(encoding="utf-8")

    def test_defines_doc_inv_007_to_011(self):
        for label in ("DOC-INV-007", "DOC-INV-008", "DOC-INV-009", "DOC-INV-010", "DOC-INV-011"):
            self.assertIn(label, self.text, f"{label} is not defined in check-doc-invariants")

    def test_invokes_the_script_entity(self):
        self.assertIn(".claude/scripts/check_doc_lint.py", self.text)

    def test_states_the_wider_range_including_the_template_itself(self):
        self.assertIn(".claude/skills/", self.text)

    def test_completion_criteria_covers_the_new_invariants(self):
        self.assertIn("DOC-INV-011", self.text.split("## Completion criteria")[-1])


class TestAC010SingleEntityCalledFromExistingSites(unittest.TestCase):
    """AC-010: 単一実体を複数地点から呼ぶ形を崩さず、分岐を作らない。"""

    def test_script_path_appears_in_exactly_one_skill(self):
        naming = []
        for path in sorted((REPO_ROOT / ".claude/skills").rglob("*.md")):
            if "check_doc_lint.py" in path.read_text(encoding="utf-8"):
                naming.append(path.relative_to(REPO_ROOT).as_posix())

        self.assertEqual(naming, [".claude/skills/check-doc-invariants/SKILL.md"])

    def test_pre_pr_and_gc_reach_it_through_the_skill(self):
        for rel in (".claude/skills/pre-pr/SKILL.md", ".claude/skills/gc/SKILL.md"):
            text = (REPO_ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("check-doc-invariants", text, rel)
            self.assertNotIn("check_doc_lint.py", text, rel)


# --------------------------------------------------------------------------- AC-011 [E2E]

class TestAC011EndToEnd(TempRepo):
    """AC-011 [E2E]: 1回の実行で C1〜C4 が ❌・C5 が ⚠️ として file:line 付きで報告され、
    ❌ があれば exit 1 になる。"""

    def test_one_run_reports_every_check_and_exits_one(self):
        write(self.root, "CLAUDE.md", """\
            # project

            broken [link](./nope.md)

            | a | b |
            |---|---|
            | 1 |

            `create-exec-plan`（Q9z）を参照

            ```mermaid
            flowchart TD
                A -->|edge (unquoted)| B
            ```

            ```bash
            grep -rn "x" .claude/ docs/ *.md
            ```
            """)
        write(self.root, ".claude/skills/create-exec-plan/SKILL.md", "### Q3d: sources\n")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(self.root)])
        report = buffer.getvalue()

        self.assertEqual(code, 1)
        for label in ("DOC-INV-007", "DOC-INV-008", "DOC-INV-009", "DOC-INV-010", "DOC-INV-011"):
            self.assertIn(label, report)
        self.assertIn("❌", report)
        self.assertIn("⚠️", report)
        self.assertIn("CLAUDE.md:3", report)

    def test_clean_repository_exits_zero(self):
        write(self.root, "CLAUDE.md", "# clean\n\nNo links, no tables, no diagrams.\n")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(self.root)])

        self.assertEqual(code, 0)
        self.assertIn("✅", buffer.getvalue())

    def test_this_repository_passes_its_own_checks(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(REPO_ROOT)])

        self.assertEqual(code, 0, buffer.getvalue())


# =========================================================================== Issue #41
# AC-IDs below refer to exec-plans/active/2026-10-sources-resolution.dev.md (not the #36 plan).

US_FIXTURE = """\
---
status: active
ac_ids: [AC-001, AC-002]
---

# US-003 tagging

## ゴール像

### 完成時にできること

- タグで絞り込める

### 主要ユーザージャーニー

1. 付ける 2. 絞る

### 非ゴール

- なし

## 受け入れ条件

### AC-001: タグを付ける

- 付けられる

### AC-002: タグで絞る

- 絞れる
"""

SPEC_FIXTURE = """\
---
status: active
---

# app spec

## Features

### タグの付与（satisfies AC-001）

付与できる。

### 一覧の絞り込み

satisfies AC-002

## E2E シナリオ

### E2E-001: 付けて絞る

一連の流れ。
"""

CONSTRAINTS_FIXTURE = """\
# constraints

| ID | 内容 |
|----|------|
| TC-001 | Python 3.11 |
"""

US_PATH = "docs/01_requirements/user_stories/US-003_tagging.md"
SPEC_PATH = "docs/02_spec/app_spec.md"


def sources_plan(rows: str, *, header: str = "## Sources") -> str:
    return (
        "# plan\n\n## Acceptance Criteria\n\n- [ ] AC-001: x\n\n"
        f"{header}\n\n"
        "| AC | US（検証可能な bullet） | spec（振る舞いの節） |\n"
        "|----|------------------------|---------------------|\n"
        f"{rows}\n"
        "\n## Task Breakdown\n\n- [ ] t\n"
    )


def report_line(testcase: unittest.TestCase, report: str, needle: str) -> str:
    """The report line mentioning `needle`; fails as an assertion (not StopIteration) when absent."""
    lines = [l for l in report.splitlines() if needle in l]
    testcase.assertTrue(lines, f"no report line mentions {needle}")
    return lines[0]


class SourcesRepo(TempRepo):
    def setUp(self):
        super().setUp()
        write(self.root, US_PATH, US_FIXTURE)
        write(self.root, SPEC_PATH, SPEC_FIXTURE)
        write(self.root, "docs/01_requirements/constraints.md", CONSTRAINTS_FIXTURE)

    def plan(self, rows: str, rel: str = "exec-plans/active/2026-10-x.md", **kwargs) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sources_plan(rows, **kwargs), encoding="utf-8")
        return path

    def check(self, path: Path):
        return lint.check_sources(path, path.read_text(encoding="utf-8"), self.root)


class TestSourcesAC001FileResolution(SourcesRepo):
    """#41 AC-001: Sources のセルが名指すファイルが存在しなければ ❌（file:line）。1セルの起点はすべて解決する。
    `同上 § X` は同じ列の直前の行のファイルを継承し、継承するファイルが無ければ ❌。素の `同上` は直上の
    セルをそのまま繰り返す（n/a の下では n/a）。n/a と、パスも同上も含まないセルは対象外。"""

    def test_resolving_table_reports_nothing(self):
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001 | `{SPEC_PATH}` §「タグの付与」 |\n"
            f"| AC-002 | 同上 § AC-002 | 同上 § E2E-001 |\n"
            f"| AC-003 [E2E] | 同上 § ゴール像／主要ユーザージャーニー | n/a（spec 未作成 — 起点は US の該当節） |"
        )

        self.assertEqual(self.check(plan), [])

    def test_missing_file_is_an_error_on_its_row(self):
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001 | `docs/02_spec/gone.md` §「タグの付与」 |"
        )

        findings = self.check(plan)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].check, "C6")
        self.assertEqual(findings[0].level, "error")
        self.assertIn("docs/02_spec/gone.md", findings[0].message)
        row_line = plan.read_text(encoding="utf-8").splitlines().index(
            f"| AC-001 | `{US_PATH}` § AC-001 | `docs/02_spec/gone.md` §「タグの付与」 |"
        ) + 1
        self.assertEqual(findings[0].line, row_line)

    def test_ditto_without_anything_above_it_is_an_error(self):
        plan = self.plan("| AC-001 | 同上 § AC-001 | n/a（spec 未作成） |")

        findings = self.check(plan)

        self.assertEqual([(f.check, f.level) for f in findings], [("C6", "error")])

    def test_ditto_below_a_missing_file_is_reported_once_not_twice(self):
        plan = self.plan(
            "| AC-001 | `docs/gone.md` § AC-001 | n/a（x） |\n"
            "| AC-002 | 同上 § AC-002 | n/a（x） |"
        )

        errors = [f for f in self.check(plan) if f.level == "error"]

        self.assertEqual(len(errors), 1)

    def test_na_cells_and_cells_naming_no_path_are_skipped(self):
        plan = self.plan(
            "| AC-001 | n/a（テンプレート自身の改修） | n/a（同上） |\n"
            "| AC-002 | 起点は Issue #41 | 本プランの Goal & Scope |"
        )

        self.assertEqual(self.check(plan), [])

    def test_every_source_in_a_cell_is_resolved(self):
        """1セルに起点が2つ（US と constraints）あるとき、2つ目の不在も ❌（再チェックで発見: 見逃し）。"""
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001、`docs/01_requirements/gone.md` § TC-001 | n/a（x） |"
        )

        errors = [f for f in self.check(plan) if f.level == "error"]

        self.assertEqual(len(errors), 1)
        self.assertIn("docs/01_requirements/gone.md", errors[0].message)

    def test_bare_ditto_under_na_inherits_the_na(self):
        """素の `同上` は直上のセルをそのまま繰り返す。直上が n/a なら n/a（再チェックで発見: 誤ブロック）。"""
        plan = self.plan(
            "| AC-001 | n/a（テンプレート自身の改修） | n/a（同上） |\n"
            "| AC-002 | 同上 | 同上 |"
        )

        self.assertEqual(self.check(plan), [])

    def test_bare_ditto_under_a_file_is_not_reported_a_second_time(self):
        """直上のセルを繰り返すだけなので、直上で出た所見をもう一度出さない。"""
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-009 | n/a（x） |\n"
            "| AC-002 | 同上 | n/a（x） |"
        )

        self.assertEqual([f.line for f in self.check(plan)], [self.check(plan)[0].line])
        self.assertEqual(len(self.check(plan)), 1)

    def test_range_row_with_na_is_skipped(self):
        plan = self.plan("| AC-001〜AC-009 | n/a（理由） | n/a（理由） |")

        self.assertEqual(self.check(plan), [])


class TestSourcesAC002SectionResolution(SourcesRepo):
    """#41 AC-002: ファイルはあるが § の節が見つからない場合と、§ を持たないセルを ⚠️。"""

    def test_named_section_not_found_is_a_warning(self):
        plan = self.plan(f"| AC-001 | `{US_PATH}` § AC-001 | `{SPEC_PATH}` §「存在しない節」 |")

        findings = self.check(plan)

        self.assertEqual([(f.check, f.level) for f in findings], [("C6", "warn")])
        self.assertIn("存在しない節", findings[0].message)

    def test_id_section_not_found_is_a_warning(self):
        plan = self.plan(f"| AC-001 | `{US_PATH}` § AC-009 | n/a（x） |")

        findings = self.check(plan)

        self.assertEqual([f.level for f in findings], ["warn"])
        self.assertIn("AC-009", findings[0].message)

    def test_heading_with_trailing_text_matches_the_name(self):
        plan = self.plan(f"| AC-001 | n/a（x） | `{SPEC_PATH}` §「タグの付与」 |")

        self.assertEqual(self.check(plan), [])

    def test_bare_name_without_brackets_matches_a_heading(self):
        plan = self.plan(f"| AC-001 | `{US_PATH}` § ゴール像 | `{SPEC_PATH}` § 一覧の絞り込み |")

        self.assertEqual(self.check(plan), [])

    def test_nested_path_must_follow_heading_nesting(self):
        good = self.plan(f"| AC-001 | `{US_PATH}` § ゴール像／主要ユーザージャーニー | n/a（x） |", rel="exec-plans/active/a.md")
        ascii_slash = self.plan(f"| AC-001 | `{US_PATH}` § ゴール像/主要ユーザージャーニー | n/a（x） |", rel="exec-plans/active/b.md")
        reversed_path = self.plan(f"| AC-001 | `{US_PATH}` § 主要ユーザージャーニー／ゴール像 | n/a（x） |", rel="exec-plans/active/c.md")

        self.assertEqual(self.check(good), [])
        self.assertEqual(self.check(ascii_slash), [])
        self.assertEqual([f.level for f in self.check(reversed_path)], ["warn"])

    def test_id_defined_as_a_table_first_cell_resolves(self):
        plan = self.plan("| AC-001 | `docs/01_requirements/constraints.md` § TC-001 | n/a（x） |")

        self.assertEqual(self.check(plan), [])

    def test_backticked_section_id_resolves(self):
        plan = self.plan(f"| AC-001 | `{US_PATH}` § `AC-001` | n/a（x） |")

        self.assertEqual(self.check(plan), [])

    def test_cell_naming_a_file_without_a_section_is_a_warning(self):
        plan = self.plan(f"| AC-001 | `{US_PATH}` | n/a（x） |")

        findings = self.check(plan)

        self.assertEqual([(f.check, f.level) for f in findings], [("C6", "warn")])

    def test_two_resolving_sources_in_one_cell_report_nothing(self):
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001、`docs/01_requirements/constraints.md` § TC-001 | n/a（x） |"
        )

        self.assertEqual(self.check(plan), [])

    def test_slash_inside_brackets_is_part_of_the_name(self):
        """「」で括った名前の中の `/` は入れ子の区切りではない（再チェックで発見: 誤 ⚠️）。"""
        write(self.root, SPEC_PATH, SPEC_FIXTURE + "\n## 入出力/形式\n\n本文\n")
        plan = self.plan(f"| AC-001 | n/a（x） | `{SPEC_PATH}` §「入出力/形式」 |")

        self.assertEqual(self.check(plan), [])

    def test_missing_file_is_not_also_reported_as_a_missing_section(self):
        plan = self.plan("| AC-001 | `docs/gone.md` § AC-001 | n/a（x） |")

        self.assertEqual([f.level for f in self.check(plan)], ["error"])



class TestSourcesReviewFindings(SourcesRepo):
    """/docode-review（PR #44）の指摘 #2・#3・#8 の再現。AC-001 / AC-002 の範囲内の欠陥。"""

    # --- #2: a backticked token inside a section name, or a URL, is not a source path
    def test_backticks_inside_a_section_name_are_part_of_the_name(self):
        write(self.root, SPEC_PATH, SPEC_FIXTURE + "\n## 設定（`config.yaml`）\n\n本文\n")
        plan = self.plan(f"| AC-001 | n/a（x） | `{SPEC_PATH}` §「設定（`config.yaml`）」 |")

        self.assertEqual(self.check(plan), [])

    def test_backticked_text_in_a_bare_section_name_matches_the_heading(self):
        write(self.root, SPEC_PATH, SPEC_FIXTURE + "\n## v1.2 の互換\n\n本文\n")
        plan = self.plan(f"| AC-001 | n/a（x） | `{SPEC_PATH}` § `v1.2` の互換 |")

        self.assertEqual(self.check(plan), [])

    def test_a_url_is_not_a_source_path(self):
        plan = self.plan("| AC-001 | `https://github.com/o/r/issues/41` | n/a（x） |")

        self.assertEqual([f for f in self.check(plan) if f.level == "error"], [])

    # --- #3: a source that cannot be read as text is reported, not a crash
    def test_unreadable_source_is_a_warning_not_a_crash(self):
        (self.root / "docs/02_spec/spec.pdf").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
        plan = self.plan("| AC-001 | n/a（x） | `docs/02_spec/spec.pdf` § 3.2 |")

        findings = self.check(plan)

        self.assertEqual([(f.check, f.level) for f in findings], [("C6", "warn")])

    def test_unreadable_source_does_not_stop_the_other_checks(self):
        (self.root / "docs/02_spec/spec.pdf").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
        self.plan("| AC-001 | n/a（x） | `docs/02_spec/spec.pdf` § 3.2 |")
        write(self.root, "docs/a.md", "see [gone](./missing.md)\n")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(self.root)])

        self.assertEqual(code, 1)
        self.assertIn("missing.md", buffer.getvalue())

    # --- #8: paths are resolved from the repository root only (ac-sources.md Rules)
    def test_a_plan_relative_path_is_not_resolved(self):
        write(self.root, "exec-plans/active/neighbour.md", "# AC-001: x\n")
        plan = self.plan("| AC-001 | `neighbour.md` § AC-001 | n/a（x） |")

        self.assertEqual([f.level for f in self.check(plan)], ["error"])

    def test_a_path_outside_the_repository_is_an_error_and_is_not_read(self):
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("# AC-001: x\n", encoding="utf-8")
        self.addCleanup(outside.unlink)
        plan = self.plan(f"| AC-001 | `../{outside.name}` § AC-001 | n/a（x） |")

        findings = self.check(plan)

        self.assertEqual([f.level for f in findings], ["error"])
        self.assertIn("outside the repository", findings[0].message)

    def test_a_directory_is_reported_as_a_directory(self):
        plan = self.plan("| AC-001 | `docs/02_spec` § E2E-001 | n/a（x） |")

        findings = self.check(plan)

        self.assertEqual([f.level for f in findings], ["error"])
        self.assertIn("directory", findings[0].message)



class TestSourcesReviewFinding6(SourcesRepo):
    """/docode-review 指摘 #6: 既存テストが AC を拘束していなかった箇所。挙動は既にあるため
    初回から緑になりうる。拘束していることは、実装を壊したコピーで赤になることで確認する。"""

    def test_id_defined_by_a_line_resolves(self):
        """AC-002: ID は「行頭 `ID:`」でも定義される（見出しでも表でもない形）。"""
        write(self.root, "docs/01_requirements/ids.md", "# ids\n\n- AC-007: リスト項目で定義\n\nAC-008: 行で定義\n")
        plan = self.plan(
            "| AC-007 | `docs/01_requirements/ids.md` § AC-007 | n/a（x） |\n"
            "| AC-008 | 同上 § AC-008 | n/a（x） |"
        )

        self.assertEqual(self.check(plan), [])

    def test_nested_path_does_not_cross_into_a_sibling_section(self):
        """AC-002: `／` は見出しの入れ子。AC-001 は `## 受け入れ条件` の配下で、`## ゴール像` の配下ではない。"""
        plan = self.plan(f"| AC-001 | `{US_PATH}` § ゴール像／AC-001 | n/a（x） |")

        self.assertEqual([f.level for f in self.check(plan)], ["warn"])


class TestSourcesReviewFinding6Documents(unittest.TestCase):
    """/docode-review 指摘 #6（文書側）と #2・#7 の規則。既存の弱い assert は凍結のまま残し、
    規則の中身を述べているかを新しく測る。"""

    def setUp(self):
        self.ac_sources = (REPO_ROOT / ".claude/skills/create-exec-plan/ac-sources.md").read_text(encoding="utf-8")
        self.rules = " ".join(_section(self.ac_sources, "Rules for the table:", ("Referencing ",)).split())

    def test_ac005_branch_says_it_is_not_na(self):
        section = _section(self.ac_sources, "## When a source cannot be opened", ("## ",))
        self.assertIn("That is not `n/a`", section)

    def test_ac006_step_0b_says_there_is_no_fallback(self):
        text = (REPO_ROOT / ".claude/skills/run-exec-plan/SKILL.md").read_text(encoding="utf-8")
        section = " ".join(_section(text, "#### Step 0b", ("#### ", "### ")).split())
        self.assertIn("gets no fallback", section)

    def test_ac007_pre_pr_and_gc_do_not_enumerate_a_range_either(self):
        for rel in (".claude/skills/pre-pr/SKILL.md", ".claude/skills/gc/SKILL.md"):
            with self.subTest(rel):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                section = _section(text, "### ③", ("### ",))
                self.assertIsNone(re.search(r"DOC-INV-0\d\d\s*[〜~-]\s*(DOC-INV-)?0?\d+", section), section)

    def test_ac010_states_the_separator_and_the_nesting_mark(self):
        self.assertIn("separated by `、`", self.rules)
        self.assertIn("joined by `／`", self.rules)
        self.assertIn("Inside 「…」 a `/` is part of the name", self.rules)

    def test_finding2_backticks_after_the_section_mark_are_part_of_the_name(self):
        self.assertIn("A backticked token after the `§` is part of the section name", self.rules)

    def test_finding7_ditto_with_and_without_a_section_are_stated_separately(self):
        self.assertIn("`同上 § X` takes the first file of the row above", self.rules)
        self.assertIn("A bare `同上` repeats the whole cell above", self.rules)
        self.assertIn("under `n/a（理由）` it is `n/a` with the same reason", self.rules)



class TestSourcesReReviewFindings(SourcesRepo):
    """/docode-review 再実行（PR #44）の指摘 #4・#6。"""

    # --- #6: a path is the backticked token at the *start* of a reference (人の決定)
    def test_backticks_in_free_text_are_not_a_path(self):
        for name, cell in [
            ("version", "起点は Issue #41（`v2.0` 互換）"),
            ("directory", "なし（`docs/` が無い）"),
            ("unpaired", "`US` を見る v1.2 `x`"),
        ]:
            with self.subTest(name):
                plan = self.plan(f"| AC-001 | {cell} | n/a（x） |", rel=f"exec-plans/active/{name}.md")
                self.assertEqual(self.check(plan), [])

    def test_bare_ditto_with_nothing_above_is_an_error(self):
        plan = self.plan("| AC-001 | 同上 | n/a（x） |")

        self.assertEqual([(f.check, f.level) for f in self.check(plan)], [("C6", "error")])

    def test_ditto_in_a_later_position_follows_the_same_rule(self):
        first_row = self.plan(f"| AC-001 | `{US_PATH}` § AC-001、同上 § AC-002 | n/a（x） |", rel="exec-plans/active/a.md")
        with_file_above = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001 | n/a（x） |\n"
            f"| AC-002 | `{SPEC_PATH}` § E2E-001、同上 § AC-009 | n/a（x） |",
            rel="exec-plans/active/b.md",
        )

        self.assertEqual([f.level for f in self.check(first_row)], ["error"])
        self.assertEqual([f.level for f in self.check(with_file_above)], ["warn"])

    # --- #4: what the earlier tests left unconstrained (green on first run; verified by mutation)
    def test_ditto_with_a_section_checks_that_section_in_the_inherited_file(self):
        plan = self.plan(
            f"| AC-001 | `{US_PATH}` § AC-001 | n/a（x） |\n"
            "| AC-002 | 同上 § AC-009 | n/a（x） |"
        )

        findings = self.check(plan)

        self.assertEqual([f.level for f in findings], ["warn"])
        self.assertIn("AC-009", findings[0].message)

    def test_ditto_does_not_reach_past_a_row_that_names_no_file(self):
        for name, middle in [("na", "n/a（理由）"), ("free", "起点は Issue #41")]:
            with self.subTest(name):
                plan = self.plan(
                    f"| AC-001 | `{US_PATH}` § AC-001 | n/a（x） |\n"
                    f"| AC-002 | {middle} | n/a（x） |\n"
                    "| AC-003 | 同上 § AC-002 | n/a（x） |",
                    rel=f"exec-plans/active/{name}.md",
                )
                self.assertEqual([f.level for f in self.check(plan)], ["error"])

    def test_an_id_does_not_match_a_longer_id(self):
        write(self.root, "docs/01_requirements/longer.md", "# x\n\n### AC-0011: 別の AC\n")
        plan = self.plan("| AC-001 | `docs/01_requirements/longer.md` § AC-001 | n/a（x） |")

        self.assertEqual([f.level for f in self.check(plan)], ["warn"])


class TestSourcesAC003Range(SourcesRepo):
    """#41 AC-003: exec-plans/active/** の ## Sources 節の表のみ。completed・docs・.claude・fence 内は対象外。"""

    BROKEN = "| AC-001 | `docs/gone.md` § AC-001 | n/a（x） |"

    def test_completed_plans_are_out_of_range(self):
        plan = self.plan(self.BROKEN, rel="exec-plans/completed/2026-09-old.md")

        self.assertEqual(self.check(plan), [])

    def test_documents_outside_exec_plans_are_out_of_range(self):
        for rel in ("docs/02_spec/notes.md", ".claude/skills/demo/SKILL.md", "README.md"):
            with self.subTest(rel):
                self.assertEqual(self.check(self.plan(self.BROKEN, rel=rel)), [])

    def test_a_table_outside_the_sources_section_is_ignored(self):
        plan = self.plan(self.BROKEN, header="## Task Notes")

        self.assertEqual(self.check(plan), [])

    def test_a_fenced_sources_table_is_ignored(self):
        path = self.root / "exec-plans/active/2026-10-fenced.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# plan\n\n```markdown\n" + sources_plan(self.BROKEN) + "```\n", encoding="utf-8")

        self.assertEqual(self.check(path), [])

    def test_pointer_checks_still_skip_exec_plans(self):
        plan = self.plan(self.BROKEN + "\n\nsee [gone](./missing.md)")

        self.assertEqual(lint.check_links(plan, plan.read_text(encoding="utf-8"), self.root), [])


class TestSourcesAC004ExitCodeAndReport(SourcesRepo):
    """#41 AC-004: AC-001 の ❌ で exit 1、AC-002 の ⚠️ のみなら 0。レポートに DOC-INV-012 の行。"""

    def run_main(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(self.root)])
        return code, buffer.getvalue()

    def test_missing_file_exits_one_and_is_reported_under_doc_inv_012(self):
        self.plan("| AC-001 | `docs/gone.md` § AC-001 | n/a（x） |")

        code, report = self.run_main()

        self.assertEqual(code, 1)
        line = report_line(self, report, "DOC-INV-012")
        self.assertIn("❌", line)

    def test_section_mismatch_only_exits_zero_with_a_warning(self):
        self.plan(f"| AC-001 | `{US_PATH}` § AC-009 | n/a（x） |")

        code, report = self.run_main()

        self.assertEqual(code, 0)
        line = report_line(self, report, "DOC-INV-012")
        self.assertIn("⚠️", line)


def _section(text: str, start: str, stop_prefixes: tuple[str, ...]) -> str:
    """The text from the line starting with `start` up to the next line starting with any stop prefix."""
    lines = text.splitlines()
    begin = next((i for i, l in enumerate(lines) if l.startswith(start)), None)
    if begin is None:
        return ""  # absent section: the caller's assertIn fails as an assertion, not StopIteration
    end = next(
        (i for i in range(begin + 1, len(lines)) if lines[i].startswith(stop_prefixes)),
        len(lines),
    )
    return "\n".join(lines[begin:end])


class TestSourcesAC005SingleSourceBranch(unittest.TestCase):
    """#41 AC-005: ac-sources.md に「起点が開けない」分岐が単一ソースとして定義され、
    n/a とは区別され、再アンカー判定表にも同じ行がある。"""

    def setUp(self):
        self.text = (REPO_ROOT / ".claude/skills/create-exec-plan/ac-sources.md").read_text(encoding="utf-8")

    def test_defines_the_branch_as_its_own_section(self):
        self.assertIn("## When a source cannot be opened", self.text)

    def test_branch_halts_the_loop_and_presents_on_the_manual_path(self):
        section = _section(self.text, "## When a source cannot be opened", ("## ",))
        self.assertIn("HALT", section)
        self.assertIn("(a)", section)
        self.assertIn("start-feature", section)

    def test_branch_is_distinguished_from_the_na_fallback(self):
        section = _section(self.text, "## When a source cannot be opened", ("## ",))
        self.assertIn("n/a", section)

    def test_re_anchor_verdict_table_carries_the_same_row(self):
        use2 = _section(self.text, "### Use 2", ("## ",))
        self.assertIn("起点が開けない", use2)



class TestSourcesFormatStatedInTheSingleSource(unittest.TestCase):
    """再チェックで発見（#41 案3）: DOC-INV-012 が施行する書式は ac-sources.md に書かれていなければ
    ならない。スクリプトにしか無い規則は、表を書く人が読めない。"""

    def setUp(self):
        text = (REPO_ROOT / ".claude/skills/create-exec-plan/ac-sources.md").read_text(encoding="utf-8")
        # Compare with whitespace collapsed: Markdown reflows a sentence across lines, and the
        # test is about what the rules say, not where the lines break.
        self.rules = " ".join(_section(text, "Rules for the table:", ("Referencing ",)).split())

    def test_states_the_reference_form_and_section_forms(self):
        self.assertIn("§", self.rules)
        self.assertIn("／", self.rules)
        self.assertIn("「", self.rules)

    def test_states_that_a_cell_may_name_several_sources(self):
        self.assertIn("、", self.rules)

    def test_states_what_a_bare_ditto_means(self):
        self.assertIn("bare `同上`", self.rules)


class TestSourcesAC006ConsumersReferenceTheBranch(unittest.TestCase):
    """#41 AC-006: run-exec-plan Step 0b・1b と start-feature Step 2 が分岐を参照し、
    CLAUDE.md の停止条件 (a) にこの場合が含まれる。"""

    def test_run_exec_plan_step_0b(self):
        text = (REPO_ROOT / ".claude/skills/run-exec-plan/SKILL.md").read_text(encoding="utf-8")
        section = _section(text, "#### Step 0b", ("#### ", "### "))
        self.assertIn("cannot be opened", section)

    def test_run_exec_plan_step_1b(self):
        text = (REPO_ROOT / ".claude/skills/run-exec-plan/SKILL.md").read_text(encoding="utf-8")
        section = _section(text, "### Step 1b", ("### ",))
        self.assertIn("cannot be opened", section)

    def test_start_feature_step_2(self):
        text = (REPO_ROOT / ".claude/skills/start-feature/SKILL.md").read_text(encoding="utf-8")
        section = _section(text, "### Step 2", ("### ",))
        self.assertIn("cannot be opened", section)

    def test_claude_md_stop_condition_a(self):
        text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        row = next(l for l in text.splitlines() if l.startswith("| (a) |"))
        self.assertIn("開けない", row)


class TestSourcesAC007GateDocuments(unittest.TestCase):
    """#41 AC-007: check-doc-invariants が DOC-INV-012 を定義、pre-pr ⑤c は ③ に委ねる、
    pre-pr ③ / gc ③ は DOC-INV の上限番号を書かない。"""

    def test_check_doc_invariants_defines_doc_inv_012(self):
        text = (REPO_ROOT / ".claude/skills/check-doc-invariants/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("DOC-INV-012", text)
        self.assertIn("DOC-INV-012", text.split("## Completion criteria")[-1])

    def test_pre_pr_5c_delegates_resolution_to_doc_inv_012(self):
        text = (REPO_ROOT / ".claude/skills/pre-pr/SKILL.md").read_text(encoding="utf-8")
        section = _section(text, "### ⑤c", ("### ",))
        self.assertIn("DOC-INV-012", section)

    def test_pre_pr_and_gc_do_not_hardcode_an_upper_bound(self):
        for rel, start in ((".claude/skills/pre-pr/SKILL.md", "### ③"), (".claude/skills/gc/SKILL.md", "### ③")):
            with self.subTest(rel):
                text = (REPO_ROOT / rel).read_text(encoding="utf-8")
                section = _section(text, start, ("### ",))
                self.assertNotIn("through DOC-INV-", section)


class TestSourcesAC008EndToEnd(SourcesRepo):
    """#41 AC-008 [E2E]: 1回の実行で active の不在パスが ❌ / exit 1、節不一致のみなら ⚠️ / exit 0、
    completed は報告されない。"""

    def test_one_run_over_active_and_completed_plans(self):
        self.plan("| AC-001 | `docs/gone.md` § AC-001 | n/a（x） |", rel="exec-plans/active/2026-10-live.md")
        self.plan("| AC-001 | `docs/also-gone.md` § AC-001 | n/a（x） |", rel="exec-plans/completed/2026-09-old.md")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = lint.main(["--root", str(self.root)])
        report = buffer.getvalue()

        self.assertEqual(code, 1)
        self.assertIn("exec-plans/active/2026-10-live.md:", report)
        self.assertIn("docs/gone.md", report)
        self.assertNotIn("also-gone.md", report)


if __name__ == "__main__":
    unittest.main()
