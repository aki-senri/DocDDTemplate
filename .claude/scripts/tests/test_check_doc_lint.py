"""Acceptance tests for .claude/scripts/check_doc_lint.py.

Each test names the AC it transcribes (exec-plans/active/2026-09-doc-lint-scripts.dev.md).
Written from the AC lines before the implementation existed (red-first / INV-T02).
"""

import ast
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


if __name__ == "__main__":
    unittest.main()
