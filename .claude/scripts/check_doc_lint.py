#!/usr/bin/env python3
"""check_doc_lint.py — mechanical checks for DocDD convention documents.

Implements DOC-INV-007 through DOC-INV-012 (see
`.claude/skills/check-doc-invariants/SKILL.md`, which is the only skill that invokes this file):

| Check | Invariant    | What it detects                                       | Level |
|-------|--------------|-------------------------------------------------------|-------|
| C1    | DOC-INV-007  | A relative Markdown link that resolves to nothing     | ❌    |
| C2    | DOC-INV-008  | A table row whose column count differs from its header| ❌    |
| C3    | DOC-INV-009  | A label reference (`Q3d`, `Step 0b`, `§2c`, `⑤c`,     | ❌    |
|       |              | `DOC-INV-NNN`, `INV-TNN`) absent from the file the    |       |
|       |              | same line names                                       |       |
| C4    | DOC-INV-010  | An unquoted Mermaid label containing `()[]{}`         | ❌    |
| C5    | DOC-INV-011  | A multi-path `grep` in a `bash` fence without both    | ⚠️    |
|       |              | `2>/dev/null` and `\\|\\| true`                         |       |
| C6    | DOC-INV-012  | A file an active plan's `## Sources` row names that   | ❌    |
|       |              | does not exist (⚠️ when only the § section is missing) |       |

What it deliberately does not check is listed in the skill: pointers inside `exec-plans/**` (a plan
is a working note, and an archived one is not a reference document) — except an active plan's
`## Sources` table, which DOC-INV-012 checks because it is read while the work is in flight —
whether a consumer has the
material it needs at the point it decides (process-walkthrough lap 7 step 3), and sites that
*should* consume a rule but never name it. Those stay with the human or the driver.

Standard library only, so it runs wherever `python3` does.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------- model

INVARIANTS = {
    "C1": ("DOC-INV-007", "relative link resolution"),
    "C2": ("DOC-INV-008", "table column consistency"),
    "C3": ("DOC-INV-009", "label reference existence"),
    "C4": ("DOC-INV-010", "Mermaid label quoting"),
    "C5": ("DOC-INV-011", "grep robustness in shell snippets"),
    "C6": ("DOC-INV-012", "AC sources resolution"),
}

FIX_HINTS = {
    "C1": "Point the link at a file that exists, or drop it. A placeholder belongs in a fenced block.",
    "C2": "Restore the row to the header's column count — a split table renders as prose.",
    "C3": "Update the label to the one the target file actually defines (it was probably renumbered).",
    "C4": 'Wrap the label in double quotes: |"a (b)"| — an unquoted bracket breaks the whole diagram.',
    "C5": "Append 2>/dev/null || true — a missing path or a no-match exits non-zero under set -e.",
    "C6": "Present the row to a human — repairing it is theirs, not an agent's: repointing it, or "
    "deciding there is nothing to read, is a decision about what the AC condenses "
    "(ac-sources.md「When a source cannot be opened」). Do not guess the moved file or write n/a.",
}

# DOC-INV-007 (links) and DOC-INV-009 (label references) are the *pointer* checks: they ask whether
# a reference resolves right now. They skip `exec-plans/**` entirely.
#
# A plan is a working note, not a reference document. CLAUDE.md already treats it that way — a
# completed plan is archived and "参照されない", which is why reconcile records go to the active plan
# instead — so a stale pointer inside one has almost no downstream consumer. Against that, a ❌ on a
# plan would block the PR of the very work the plan describes, and it would fire hardest at the
# start: an unchecked AC names what it is *about to* create, so it can only point at something that
# does not exist yet. Letting archived material drift is the cheaper trade; drift inside a plan is
# left to the readers who can judge it — process-walkthrough lap 7, `/doc-review`, `/docode-review`.
#
# The structural checks still cover plans, because they are not about pointers: a split `## Sources`
# table (DOC-INV-008) silently breaks "a row for every AC", and a broken diagram (DOC-INV-010) or an
# unguarded snippet (DOC-INV-011) is broken in every state, not only against today's tree.
POINTER_CHECK_EXCLUDED_DIRS = ("exec-plans",)


def pointer_checks_apply(path) -> bool:
    """Whether the pointer checks (DOC-INV-007 / 009) judge this file at all."""
    return not any(part in POINTER_CHECK_EXCLUDED_DIRS for part in Path(path).parts)


@dataclass
class Finding:
    check: str
    level: str  # "error" (blocks) or "warn" (report only)
    path: Path
    line: int
    message: str


# --------------------------------------------------------------------------- line structure


@dataclass
class Line:
    number: int
    text: str
    fence: str | None  # the fence's language when inside one, else None


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)")


def scan_lines(text: str) -> list[Line]:
    """Annotate every line with the fence it sits in, if any."""
    lines: list[Line] = []
    marker: str | None = None  # the opening fence's run of backticks/tildes
    lang = ""
    for number, raw in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(raw)
        if marker is None:
            if match:
                marker, lang = match.group(1), match.group(2).lower()
                lines.append(Line(number, raw, lang))
                continue
            lines.append(Line(number, raw, None))
        else:
            inside = lang
            # A closing fence uses the same character, at least as many times, and nothing else.
            if match and match.group(1)[0] == marker[0] and len(match.group(1)) >= len(marker) and not match.group(2):
                marker, lang = None, ""
            lines.append(Line(number, raw, inside))
    return lines


def body_lines(lines: list[Line]) -> list[Line]:
    """Lines outside fenced blocks — a fence holds templates and examples, not live markup."""
    return [line for line in lines if line.fence is None]


def fenced_lines(lines: list[Line], languages: tuple[str, ...]) -> list[Line]:
    """Lines inside a fence whose language matches, excluding the fence markers themselves."""
    return [
        line
        for line in lines
        if line.fence in languages and not FENCE_RE.match(line.text)
    ]


def strip_inline_code(text: str) -> str:
    """Blank out `code spans` so their contents are not mistaken for live markup."""
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), text)


# --------------------------------------------------------------------------- C1: links

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^()\s]+?)\s*(?:\s+\"[^\"]*\")?\)")
PLACEHOLDER_MARKERS = ("{", "}", "<", ">", "XXX", "NNN", "YYYY", "MM-", "$")
SKIP_SCHEMES = ("http://", "https://", "mailto:", "ftp://", "tel:")


def check_links(path: Path, text: str, repo_root: Path) -> list[Finding]:
    """C1 / DOC-INV-007 — every relative Markdown link resolves to a file in the tree.

    Plans are out of range (see `pointer_checks_apply`).
    """
    if not pointer_checks_apply(path):
        return []
    findings: list[Finding] = []
    repo_root = Path(repo_root)
    for line in body_lines(scan_lines(text)):
        for target in LINK_RE.findall(strip_inline_code(line.text)):
            if target.startswith("#") or target.lower().startswith(SKIP_SCHEMES):
                continue
            if any(marker in target for marker in PLACEHOLDER_MARKERS):
                continue
            bare = target.split("#", 1)[0]
            if not bare:
                continue
            candidates = [
                (Path(path).parent / bare),
                (repo_root / bare.lstrip("/")),
            ]
            if any(candidate.exists() for candidate in candidates):
                continue
            # A link that points outside the repository cannot be verified from here. Compare
            # resolved paths rather than string prefixes: "/tmp/repo2/x" starts with "/tmp/repo"
            # without being inside it, which would turn an unverifiable link into a violation.
            resolved = (Path(path).parent / bare).resolve()
            if not resolved.is_relative_to(Path(repo_root).resolve()):
                continue
            findings.append(
                Finding("C1", "error", Path(path), line.number, f"link target does not exist: {target}")
            )
    return findings


# --------------------------------------------------------------------------- C2: tables


def split_cells(row: str) -> int:
    """Count a table row's cells, treating `\\|` and pipes inside `code spans` as literal text."""
    stripped = row.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        stripped = stripped[:-1]
    cells, in_code, index = 1, False, 0
    while index < len(stripped):
        char = stripped[index]
        if char == "\\" and index + 1 < len(stripped):
            index += 2
            continue
        if char == "`":
            in_code = not in_code
        elif char == "|" and not in_code:
            cells += 1
        index += 1
    return cells


DELIMITER_RE = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")


def check_tables(path: Path, text: str) -> list[Finding]:
    """C2 / DOC-INV-008 — a table's rows all carry the header's column count."""
    findings: list[Finding] = []
    lines = body_lines(scan_lines(text))
    index = 0
    while index < len(lines):
        header = lines[index]
        following = lines[index + 1] if index + 1 < len(lines) else None
        is_table = (
            header.text.strip().startswith("|")
            and following is not None
            and following.number == header.number + 1
            and DELIMITER_RE.match(following.text)
        )
        if not is_table:
            index += 1
            continue
        expected = split_cells(header.text)
        index += 1  # the delimiter row
        while index < len(lines) and lines[index].text.strip().startswith("|"):
            row = lines[index]
            actual = split_cells(row.text)
            if actual != expected:
                findings.append(
                    Finding(
                        "C2",
                        "error",
                        Path(path),
                        row.number,
                        f"table row has {actual} column(s), header has {expected}",
                    )
                )
            index += 1
    return findings


# --------------------------------------------------------------------------- C3: label references

LABEL_RES = (
    re.compile(r"(?<![A-Za-z0-9])(Q\d+[a-z]?)(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])(Step\s\d+[a-z]?)(?![A-Za-z0-9])"),
    re.compile(r"(§\d+[a-z]?)"),
    re.compile(r"([①-⑳][a-z])"),  # ⑤c only: a bare ③ is as often a local enumeration
    re.compile(r"(DOC-INV-\d{3})"),
    re.compile(r"(INV-[A-Z]+\d+)"),
)
SKILL_NAME_RE = re.compile(r"[`/]([a-z][a-z0-9-]{2,})`?")
DOC_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.md)`|\]\(([^()\s]+\.md)\)")
#: How far *after* a named file a label may sit and still be read as pointing into it. A whole line
#: is too wide in both directions: a line that links one file while listing unrelated question
#: numbers would flag every one of them, and a label whose own file is named later in the sentence
#: ("(Step 1b / Step 3a), while at `pre-pr` ⑤c …") would be judged against the wrong file.
PROXIMITY = 32


def _targets(path: Path, line_text: str, repo_root: Path) -> list[tuple[int, Path]]:
    """Files this line names, each with the column it was named at."""
    found: list[tuple[int, Path]] = []
    for match in SKILL_NAME_RE.finditer(line_text):
        candidate = Path(repo_root) / ".claude/skills" / match.group(1) / "SKILL.md"
        if candidate.exists():
            found.append((match.start(1), candidate))
    for match in DOC_PATH_RE.finditer(line_text):
        rel = match.group(1) or match.group(2)
        for candidate in ((Path(path).parent / rel), (Path(repo_root) / rel.lstrip("/"))):
            if candidate.exists() and candidate.is_file():
                found.append((match.start(), candidate))
                break
    return found


def _label_variants(label: str) -> list[str]:
    """`§2c` is written `2c` where it is defined; everything else is written as referenced."""
    variants = [label]
    if label.startswith("§"):
        variants.append(label[1:])
    return variants


def check_labels(path: Path, text: str, repo_root: Path) -> list[Finding]:
    """C3 / DOC-INV-009 — a label reference exists in the file named just before it.

    Plans are out of range (see `pointer_checks_apply`).
    """
    if not pointer_checks_apply(path):
        return []
    findings: list[Finding] = []
    cache: dict[Path, str] = {}
    for line in body_lines(scan_lines(text)):
        targets = _targets(Path(path), line.text, Path(repo_root))
        if not targets:
            continue
        for pattern in LABEL_RES:
            for match in pattern.finditer(line.text):
                label = match.group(1)
                near = [
                    target
                    for column, target in targets
                    if 0 <= match.start(1) - column <= PROXIMITY
                ]
                if not near:
                    continue
                variants = _label_variants(label)
                for target in near:
                    if target not in cache:
                        cache[target] = target.read_text(encoding="utf-8")
                    if any(variant in cache[target] for variant in variants):
                        break
                else:
                    names = ", ".join(sorted({t.name for t in near}))
                    findings.append(
                        Finding(
                            "C3",
                            "error",
                            Path(path),
                            line.number,
                            f"label {label} is not defined in {names}",
                        )
                    )
    return findings


# --------------------------------------------------------------------------- C4: mermaid

EDGE_LABEL_RE = re.compile(r"\|([^|]+)\|")
BRACKET_PAIRS = {"[": "]", "(": ")", "{": "}"}
NEEDS_QUOTING = set("()[]{}")


def _matching_close(text: str, start: int) -> int | None:
    """Index of the bracket closing the one at `start`, ignoring brackets inside quotes."""
    depth, index, quote = 0, start, None
    while index < len(text):
        char = text[index]
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in BRACKET_PAIRS:
            depth += 1
        elif char in BRACKET_PAIRS.values():
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _node_labels(text: str):
    """Yield each node's label text: what sits inside `ID[…]`, `ID([…])`, `ID{{…}}`, …"""
    index = 0
    while index < len(text):
        char = text[index]
        previous = text[index - 1] if index else ""
        if char in BRACKET_PAIRS and (previous.isalnum() or previous == "_"):
            end = _matching_close(text, index)
            if end is None:
                index += 1
                continue
            yield text[index + 1 : end]
            index = end + 1
            continue
        index += 1


def _strip_shape_layers(label: str) -> str:
    """Remove the paired brackets that express a *shape* rather than label text.

    `([Project Start])` is a stadium node, not a label containing brackets — mermaid parses those
    delimiters itself, so only what remains inside them has to be quoted.
    """
    stripped = label.strip()
    while len(stripped) >= 2 and stripped[0] in BRACKET_PAIRS and BRACKET_PAIRS[stripped[0]] == stripped[-1]:
        stripped = stripped[1:-1].strip()
    return stripped


def _unquoted_and_risky(label: str) -> bool:
    stripped = _strip_shape_layers(label)
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) >= 2:
        return False
    return any(char in NEEDS_QUOTING for char in stripped)


def check_mermaid(path: Path, text: str) -> list[Finding]:
    """C4 / DOC-INV-010 — a Mermaid label carrying brackets or parentheses is quoted.

    One unquoted label stops the parser, and the renderer reports only the first one — which is why
    this runs statically over every block instead of relying on a round trip through a renderer.
    """
    findings: list[Finding] = []
    for line in fenced_lines(scan_lines(text), ("mermaid",)):
        seen: set[str] = set()
        for match in EDGE_LABEL_RE.finditer(line.text):
            label = match.group(1)
            if _unquoted_and_risky(label) and label not in seen:
                seen.add(label)
                findings.append(
                    Finding("C4", "error", Path(path), line.number, f"unquoted edge label: |{label}|")
                )
        if seen:
            continue  # the whole line is already reported; a node label inside it adds no signal
        for label in _node_labels(line.text):
            if _unquoted_and_risky(label) and label not in seen:
                seen.add(label)
                findings.append(
                    Finding("C4", "error", Path(path), line.number, f"unquoted node label: {label}")
                )
    return findings


# --------------------------------------------------------------------------- C4 opt-in: real parser

MERMAID_PROBE = "require.resolve('mermaid'); require.resolve('jsdom');"


def mermaid_parser_available() -> bool:
    """Whether node, mermaid and jsdom are all present for the opt-in parser run."""
    try:
        return (
            subprocess.run(
                ["node", "-e", MERMAID_PROBE],
                capture_output=True,
                timeout=30,
                check=False,
            ).returncode
            == 0
        )
    except (OSError, subprocess.SubprocessError):
        return False


def mermaid_blocks(text: str) -> list[tuple[int, str]]:
    """Every Mermaid block as (first content line number, source)."""
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    start = 0
    for line in scan_lines(text):
        if line.fence == "mermaid" and not FENCE_RE.match(line.text):
            if not current:
                start = line.number
            current.append(line.text)
        elif current:
            blocks.append((start, "\n".join(current)))
            current = []
    if current:
        blocks.append((start, "\n".join(current)))
    return blocks


PARSER_SCRIPT = r"""
const fs = require('fs');
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><body></body>', { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
// mermaid 11 ships as ESM; require() hands back the namespace, whose API sits on .default.
const mermaidModule = require('mermaid');
const mermaid = mermaidModule.default || mermaidModule;
if (typeof mermaid.parse !== 'function') {
  process.stderr.write('mermaid.parse unavailable (incompatible mermaid build)');
  process.exit(2);
}
mermaid.initialize({ startOnLoad: false });
const blocks = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
(async () => {
  const results = [];
  for (const block of blocks) {
    try {
      await mermaid.parse(block.source);
    } catch (error) {
      results.push({ path: block.path, line: block.line, message: String(error && error.message || error).split('\n')[0] });
    }
  }
  process.stdout.write(JSON.stringify(results));
})();
"""


def parse_mermaid_with_renderer(blocks: list[dict]) -> list[dict]:
    """Run mermaid's own parser over the blocks; returns one entry per block that failed."""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parse.js"
        payload = Path(tmp) / "blocks.json"
        script.write_text(PARSER_SCRIPT, encoding="utf-8")
        payload.write_text(json.dumps(blocks), encoding="utf-8")
        completed = subprocess.run(
            ["node", str(script), str(payload)],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise RuntimeError(completed.stderr.strip() or "mermaid parser produced no output")
    return json.loads(completed.stdout)


# --------------------------------------------------------------------------- C5: grep snippets

GREP_RE = re.compile(r"\bgrep\b")
PATHISH_RE = re.compile(r"^[\w./*@-]+$")


def _path_argument_count(command: str) -> int:
    after_pattern = re.sub(r"\"[^\"]*\"|'[^']*'", " ", command)
    tokens = after_pattern.split()
    return sum(
        1
        for token in tokens[1:]
        if PATHISH_RE.match(token)
        and not token.startswith("-")
        and ("/" in token or "*" in token or token.endswith(".md"))
    )


def check_grep_snippets(path: Path, text: str) -> list[Finding]:
    """C5 / DOC-INV-011 — a multi-path `grep` in a shell snippet survives set -e (report only).

    Report only: a snippet may deliberately want the non-zero exit (#36 論点2), so this states the
    risk and leaves the judgement to the reader.
    """
    findings: list[Finding] = []
    for line in fenced_lines(scan_lines(text), ("bash", "sh", "shell", "zsh")):
        command = line.text.strip()
        if command.startswith("#") or not GREP_RE.search(command):
            continue
        if _path_argument_count(command) < 2:
            continue
        missing = []
        if "2>/dev/null" not in command:
            missing.append("2>/dev/null")
        if "|| true" not in command.replace("\\|\\|", "||"):
            missing.append("|| true")
        if missing:
            findings.append(
                Finding(
                    "C5",
                    "warn",
                    Path(path),
                    line.number,
                    f"multi-path grep without {' and '.join(missing)}",
                )
            )
    return findings


# --------------------------------------------------------------------------- C6: AC sources

# The one *pointer* check that reads plans. DOC-INV-007 / 009 skip `exec-plans/**` because a plan is a
# working note whose pointers nobody follows once it is archived. A `## Sources` table is the
# deliberate exception: it is read *while the work is in flight* (run-exec-plan Step 0b / 1b / 3a,
# start-feature Step 2), so a row that does not resolve stalls red-first now rather than misleading
# some later reader of the archive. Completed plans stay out of range — their drift is accepted.
#
# Levels follow what can be decided mechanically. A missing file is unambiguous: ❌. A section is
# matched by heading text, which can drift in wording ("タグの付与" vs "タグ付与"), so a section that
# cannot be found is ⚠️ — a human or the driver reading the file can still tell whether it is there.

SOURCES_HEADING_RE = re.compile(r"^##\s+Sources\s*$")
H2_RE = re.compile(r"^##\s")
#: A backticked token is a *path* when it has a directory separator or a file extension. Only a
#: token *before* a reference's `§` is considered: one after it is part of the section name
#: (`§「設定（\`config.yaml\`）」`), and a URL is a link, not a file in this repository.
PATH_TOKEN_RE = re.compile(r"`([^`]*?(?:/|\.[A-Za-z0-9]+)[^`]*?)`")
REFERENCE_SEPARATORS = "、，,;；"
_UNREADABLE = object()  # a source file that exists but cannot be read as text
SECTION_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")
HEADING_LINE_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NAME_SEPARATORS = (" ", "　", ":", "：", "（", "(")
DITTO = "同上"
_UNRESOLVED = object()  # a file above was already reported as missing; do not report it again


def _in_sources_range(path: Path, repo_root: Path) -> bool:
    try:
        rel = Path(path).resolve().relative_to(Path(repo_root).resolve())
    except ValueError:
        return False
    return rel.parts[:2] == ("exec-plans", "active")


def _cells(row: str) -> list[str]:
    """A table row's cells, honouring `\\|` escapes and pipes inside `code spans`."""
    stripped = row.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        stripped = stripped[:-1]
    cells, current, in_code, index = [], [], False, 0
    while index < len(stripped):
        char = stripped[index]
        if char == "\\" and index + 1 < len(stripped):
            current.append(stripped[index : index + 2])
            index += 2
            continue
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def _sources_rows(lines: list[Line]) -> list[Line]:
    """Body rows of the first table under `## Sources`, outside fences, before the next `## `."""
    body = body_lines(lines)
    start = next((i for i, line in enumerate(body) if SOURCES_HEADING_RE.match(line.text)), None)
    if start is None:
        return []
    section: list[Line] = []
    for line in body[start + 1 :]:
        if H2_RE.match(line.text):
            break
        section.append(line)
    for index, line in enumerate(section[:-1]):
        following = section[index + 1]
        if (
            line.text.strip().startswith("|")
            and following.number == line.number + 1
            and DELIMITER_RE.match(following.text)
        ):
            rows = []
            for row in section[index + 2 :]:
                if not row.text.strip().startswith("|"):
                    break
                rows.append(row)
            return rows
    return []


def _headings(text: str) -> list[tuple[int, str]]:
    found = []
    for line in body_lines(scan_lines(text)):
        match = HEADING_LINE_RE.match(line.text)
        if match:
            found.append((len(match.group(1)), _plain(match.group(2))))
    return found


def _plain(text: str) -> str:
    """Heading text without inline-code backticks: `## \`v1.2\` の互換` is the section `v1.2 の互換`."""
    return text.replace("`", "").strip()


def _names_match(heading: str, name: str) -> bool:
    """`タグの付与（satisfies AC-001）` is the section `タグの付与`; `AC-0011` is not `AC-001`."""
    if heading == name:
        return True
    return heading.startswith(name) and heading[len(name)] in NAME_SEPARATORS


def _id_defined(text: str, identifier: str) -> bool:
    """An ID is defined by a heading, a table row's first cell (constraints), or a line `ID:`."""
    for level, heading in _headings(text):
        if _names_match(heading, identifier):
            return True
    for line in body_lines(scan_lines(text)):
        stripped = line.text.strip()
        if stripped.startswith("|") and _cells(stripped)[0] == identifier:
            return True
        bare = re.sub(r"^[-*]\s+(\[[ xX]\]\s+)?", "", stripped)
        if bare.startswith((identifier + ":", identifier + "：")):
            return True
    return False


def _section_segments(section: str) -> list[str]:
    """`ゴール像／主要ユーザージャーニー` → two nested names; `「入出力/形式」` → one name.

    `／` (or `/`) separates nesting levels only outside 「…」 and outside inline code: inside them it
    is part of the heading text.
    """
    parts, current, bracketed, code = [], [], False, False
    for char in section:
        if char == "`":
            code = not code
        elif not code and char == "「":
            bracketed = True
        elif not code and char == "」":
            bracketed = False
        if char in "／/" and not bracketed and not code:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    segments = []
    for part in parts:
        part = part.strip()
        if part.startswith("「") and part.endswith("」"):
            part = part[1:-1]
        part = _plain(part)
        if part:
            segments.append(part)
    return segments


def _section_exists(text: str, section: str) -> bool:
    segments = _section_segments(section)
    if not segments:
        return False
    if len(segments) == 1 and SECTION_ID_RE.match(segments[0]):
        return _id_defined(text, segments[0])

    headings = _headings(text)

    def descend(start: int, depth: int, parent_level: int) -> bool:
        for index in range(start, len(headings)):
            level, heading = headings[index]
            if level <= parent_level:
                return False
            if _names_match(heading, segments[depth]):
                if depth == len(segments) - 1 or descend(index + 1, depth + 1, level):
                    return True
        return False

    return descend(0, 0, 0)


def _split_references(cell: str) -> list[str]:
    """A cell's references, split at `、` (or `,` / `;`) outside 「…」 and inline code."""
    parts, current, bracketed, code = [], [], False, False
    for char in cell:
        if char == "`":
            code = not code
        elif not code and char == "「":
            bracketed = True
        elif not code and char == "」":
            bracketed = False
        if char in REFERENCE_SEPARATORS and not bracketed and not code:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return [part for part in parts if part.strip()]


def _source_refs(cell: str) -> list[tuple[str, str, str | None]]:
    """The sources one cell names, in order — ("ditto", "同上", §) and/or ("path", path, §).

    A cell may name more than one source (the US bullets and a `constraints.md` row, say), and each
    is resolved on its own: checking only the first would let a missing second file through. The
    path of a reference is a backticked token *before* its `§`; anything after the `§` is the
    section name, backticks included. A section of None means the reference names no `§`.
    """
    refs: list[tuple[str, str, str | None]] = []
    for index, reference in enumerate(_split_references(cell)):
        head, marker, section = reference.partition("§")
        section_or_none = section.strip() if marker else None
        match = PATH_TOKEN_RE.search(head)
        if match and "://" not in match.group(1):
            refs.append(("path", match.group(1).strip(), section_or_none))
        elif index == 0 and head.strip().startswith(DITTO):
            refs.append(("ditto", DITTO, section_or_none))
    return refs


def check_sources(path: Path, text: str, repo_root: Path) -> list[Finding]:
    """C6 / DOC-INV-012 — what an active plan's `## Sources` table names can be opened.

    ❌ a file a cell names does not exist (or `同上 § …` has no file above it to inherit);
    ⚠️ the file exists but the `§` section cannot be found, or the cell names a file and no section.
    Cells reading `n/a（理由）`, and cells naming neither a path nor `同上`, are not this check's to
    judge: whether every AC has a well-formed row is `pre-pr` ⑤c.

    `同上` follows the column. `同上 § X` means "the file above, section X". A bare `同上` repeats
    the cell above as it stands — under `n/a` it is `n/a` (the reason carries down), and under a file
    it adds nothing new to check, so whatever the row above found is not reported a second time.
    When a cell names several sources, the first is the one a later `同上` inherits.
    """
    if not _in_sources_range(path, repo_root):
        return []
    findings: list[Finding] = []
    previous: dict[int, object] = {}  # column → Path | _UNRESOLVED | None
    cache: dict[Path, object] = {}  # Path → text | _UNREADABLE
    root = Path(repo_root).resolve()

    def check_section(row: Line, target: Path, written: str, section: str | None) -> None:
        if section is None or not section:
            findings.append(
                Finding("C6", "warn", Path(path), row.number, f"{written} names a file but no § section")
            )
            return
        if target not in cache:
            try:
                cache[target] = target.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                cache[target] = _UNREADABLE
        if cache[target] is _UNREADABLE:
            findings.append(
                Finding(
                    "C6",
                    "warn",
                    Path(path),
                    row.number,
                    f"{written} cannot be read as text — § {section} not checked",
                )
            )
            return
        if not _section_exists(cache[target], section):
            findings.append(Finding("C6", "warn", Path(path), row.number, f"§ {section} not found in {written}"))

    for row in _sources_rows(scan_lines(text)):
        for column, cell in enumerate(_cells(row.text)[1:], start=1):
            if cell.strip("` ").lower().startswith("n/a"):
                previous[column] = None
                continue
            refs = _source_refs(cell)
            if not refs:
                previous[column] = None  # free text: nothing to resolve, and nothing to inherit
                continue
            inherited = previous.get(column)
            primary: object = None
            for position, (kind, written, section) in enumerate(refs):
                if kind == "ditto" and section is None:
                    resolved = inherited  # a bare 同上: the cell above, as it stands
                elif kind == "ditto":
                    if inherited is _UNRESOLVED:
                        resolved = _UNRESOLVED  # the file above is already reported
                    elif inherited is None:
                        findings.append(
                            Finding(
                                "C6",
                                "error",
                                Path(path),
                                row.number,
                                f"{DITTO} § {section} has no source file above it to inherit",
                            )
                        )
                        resolved = _UNRESOLVED
                    else:
                        resolved = inherited
                        check_section(row, Path(inherited), f"{DITTO}（{Path(inherited).name}）", section)
                else:
                    # From the repository root only, as ac-sources.md「Rules for the table」 says —
                    # a reader opening the row resolves it that way, so the check must too.
                    target = (root / written.lstrip("/")).resolve()
                    problem = None
                    if not target.is_relative_to(root):
                        problem = f"source path points outside the repository: {written}"
                    elif target.is_dir():
                        problem = f"source names a directory, not a file: {written}"
                    elif not target.is_file():
                        problem = f"source file does not exist: {written}"
                    if problem:
                        findings.append(Finding("C6", "error", Path(path), row.number, problem))
                        resolved = _UNRESOLVED
                    else:
                        resolved = target
                        check_section(row, target, written, section)
                if position == 0:
                    primary = resolved
            previous[column] = primary
    return findings


# --------------------------------------------------------------------------- driver

RANGES = (".claude/skills/**/*.md", "docs/**/*.md", "exec-plans/**/*.md", "*.md")
CHECKS = {
    "C1": lambda path, text, root: check_links(path, text, root),
    "C2": lambda path, text, root: check_tables(path, text),
    "C3": lambda path, text, root: check_labels(path, text, root),
    "C4": lambda path, text, root: check_mermaid(path, text),
    "C5": lambda path, text, root: check_grep_snippets(path, text),
    "C6": lambda path, text, root: check_sources(path, text, root),
}


def default_paths(repo_root: Path) -> list[Path]:
    """The four ranges. A range that does not exist in this repository is skipped, not an error."""
    root = Path(repo_root)
    found: set[Path] = set()
    for pattern in RANGES:
        found.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(found)


def lint_paths(
    paths, *, repo_root: Path, mermaid_parser: bool = False, only: tuple[str, ...] = ()
) -> list[Finding]:
    selected = tuple(only) or tuple(CHECKS)
    findings: list[Finding] = []
    blocks: list[dict] = []
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            findings.append(Finding("C1", "error", Path(path), 0, f"cannot read file: {error}"))
            continue
        for check in selected:
            findings.extend(CHECKS[check](Path(path), text, Path(repo_root)))
        if mermaid_parser and "C4" in selected:
            blocks.extend(
                {"path": str(path), "line": line, "source": source}
                for line, source in mermaid_blocks(text)
            )

    if mermaid_parser and "C4" in selected:
        if not mermaid_parser_available():
            findings.append(
                Finding(
                    "C4",
                    "warn",
                    Path(repo_root),
                    0,
                    "mermaid parser (node + mermaid + jsdom) unavailable — real-parser pass skipped",
                )
            )
        elif blocks:
            try:
                for failure in parse_mermaid_with_renderer(blocks):
                    findings.append(
                        Finding(
                            "C4",
                            "error",
                            Path(failure["path"]),
                            failure["line"],
                            f"mermaid parse error: {failure['message']}",
                        )
                    )
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
                findings.append(
                    Finding("C4", "warn", Path(repo_root), 0, f"mermaid parser run failed: {error}")
                )
    return sorted(findings, key=lambda f: (f.check, str(f.path), f.line))


def exit_code(findings) -> int:
    return 1 if any(finding.level == "error" for finding in findings) else 0


def format_report(findings, *, repo_root: Path, checked: int) -> str:
    root = Path(repo_root)

    def location(finding: Finding) -> str:
        try:
            rel = Path(finding.path).relative_to(root)
        except ValueError:
            rel = Path(finding.path)
        if not finding.line:
            # A run-wide note (the opt-in parser being unavailable) belongs to no file.
            return "" if rel.as_posix() in (".", "") else rel.as_posix()
        return f"{rel.as_posix()}:{finding.line}"

    out = ["=== Document lint results (DOC-INV-007〜012) ===", "", f"Files checked: {checked}", ""]
    for check, (invariant, title) in INVARIANTS.items():
        rows = [f for f in findings if f.check == check]
        errors = [f for f in rows if f.level == "error"]
        warnings = [f for f in rows if f.level == "warn"]
        mark = "❌" if errors else ("⚠️" if warnings else "✅")
        label = "warnings" if warnings and not errors else "violations"
        out.append(f"{mark} {invariant} {label} ({title}): {len(rows)}")
        for finding in rows:
            prefix = "  - " if finding.level == "error" else "  ⚠️ "
            where = location(finding)
            out.append(f"{prefix}{where}: {finding.message}" if where else f"{prefix}{finding.message}")
        # The hint tells a reader how to clear a violation; a run-wide note has nothing to clear.
        if errors or any(f.line for f in warnings):
            out.append(f"    Fix: {FIX_HINTS[check]}")
        out.append("")

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warn"]
    if errors:
        summary = f"❌ {len(errors)} violation(s)" + (f" / ⚠️ {len(warnings)} warning(s)" if warnings else "")
    elif warnings:
        summary = f"✅ No violations / ⚠️ {len(warnings)} warning(s)"
    else:
        summary = "✅ All passed"
    out.extend(["---", f"Overall: {summary}"])
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Mechanical checks for DocDD convention documents (DOC-INV-007〜012).",
    )
    parser.add_argument("paths", nargs="*", help="files to check (default: the four ranges)")
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    parser.add_argument(
        "--only",
        default="",
        help="comma-separated subset of checks, e.g. C1,C6 (default: all)",
    )
    parser.add_argument(
        "--mermaid-parser",
        action="store_true",
        help="additionally run mermaid's own parser (needs node + mermaid + jsdom; "
        "skipped with a warning when unavailable)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.root).resolve()
    only = tuple(part.strip().upper() for part in args.only.split(",") if part.strip())
    unknown = [check for check in only if check not in CHECKS]
    if unknown:
        parser.error(f"unknown check(s): {', '.join(unknown)}")

    paths = [Path(p) for p in args.paths] if args.paths else default_paths(repo_root)
    findings = lint_paths(
        paths, repo_root=repo_root, mermaid_parser=args.mermaid_parser, only=only
    )
    print(format_report(findings, repo_root=repo_root, checked=len(paths)))
    return exit_code(findings)


if __name__ == "__main__":
    sys.exit(main())
