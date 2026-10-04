---
name: check-doc-invariants
description: |
  Checks structural invariants of documents in docs/**/*.md and exec-plans/, and runs the
  mechanical checks (DOC-INV-007 onward) over those plus the convention documents themselves
  (.claude/skills/**/*.md and the root *.md) and active plans' ## Sources tables.
  Verifies reference directions, frontmatter completeness, lifecycle consistency,
  AC traceability, goal image / E2E traceability, link resolution, table integrity,
  label references, Mermaid quoting, shell-snippet robustness and AC sources resolution.
  Called from pre-pr and gc, or run standalone.
disable-model-invocation: true
---

# Skill: Document Invariant Check

> **When to run**:
> - Before creating a PR (called from `pre-pr`)
> - During weekly GC (called from `gc`)
> - After writing or updating documents
>
> **Purpose**: Detect structural violations in documentation — broken reference directions,
> incomplete frontmatter, lifecycle inconsistencies, and AC traceability gaps — before they
> accumulate into hard-to-trace drift.
>
> **Prerequisites**: `docs/` directory must exist (Phase 1 must be complete)

---

## What this skill does

1. Collect all `docs/**/*.md` and `exec-plans/**/*.md`
2. Parse frontmatter and extract cross-links from each file
3. Check each document against DOC-INV-001〜006 below (read by a reader, not a script)
4. Run `.claude/scripts/check_doc_lint.py` for DOC-INV-007〜012 — the mechanical checks, over a
   **wider range** that includes the convention documents themselves
5. Report violations with fix instructions

---

## Built-in invariants

### DOC-INV-001: Reference direction

Documents must not reference documents at a more concrete abstraction layer.

| Layer | Path | May reference |
|-------|------|---------------|
| 1 – Requirements | `docs/01_requirements/` | External resources, `constraints.md` within layer 1 |
| 2 – Spec | `docs/02_spec/` | Layer 1 and below |
| 2.5 – Exec-plans | `exec-plans/` | Layers 1–2 (US files and spec sections) |
| 3 – Design | `docs/03_design/` | Layers 1–2 and below |
| 4 – Implementation | `docs/04_implementation/` | Layers 1–3 and below |
| 5 – Quality | `docs/05_quality/` | All `docs/` layers |

**Violation example**: A `docs/01_requirements/` file links to `docs/03_design/api_spec.md`.

**Why exec-plans sit at 2.5 and not 1.5.** A plan is written *from* an approved spec — that is the
`create-requirements → create-spec → create-exec-plan` order — so the spec is upstream of the plan,
not downstream of it. The earlier 1.5 placement predates `docs/02_spec/` being a required layer, and
it made the `## Sources` table an exec-plan must carry
(`../create-exec-plan/ac-sources.md`) into a violation of this very invariant: the plan is required
to name the spec section each AC condenses, and `run-exec-plan` re-anchors to it before checking the
box. Exec-plans still may not reference design or implementation docs (layers 3+) — a plan describes
*what must become true*, not how the code is arranged.

**Note**: Links going upward in abstraction (e.g., implementation doc referencing a requirement)
are valid forward references — only downward references (requirements referencing implementation) are violations.

---

### DOC-INV-002: Frontmatter completeness

Every `docs/**/*.md` must have:
- `status:` — one of `draft`, `active`, `deprecated`

Documents in `docs/03_design/` and `docs/04_implementation/` that correspond to code must have:
- `tracks:` — glob pattern(s) pointing to the tracked source files

Every `docs/01_requirements/user_stories/US-*.md` must also have:
- `ac_ids:` — non-empty list of AC identifiers defined in the document body

---

### DOC-INV-003: Lifecycle consistency

- `active` documents must not link to `deprecated` documents
- If a link target has `status: deprecated`, flag it as a violation and suggest updating to the successor document (if known)

---

### DOC-INV-004: AC traceability

For each `exec-plans/active/*.md`:
- Every `AC-NNN` line must correspond to a US file whose `ac_ids:` contains that identifier

For each `docs/01_requirements/user_stories/US-*.md`:
- Every AC-ID in `ac_ids:` should appear in at least one exec-plan (warn if none found — it may simply not have been planned yet)

---

### DOC-INV-005: Diagram rules (CLAUDE.md compliance)

- ASCII art blocks (lines containing `┌`, `│`, `└`, `├`, `┤`, `┬`, `┴`, `┼`, or `+--+` patterns)
  must be followed within 3 lines by a non-empty plain-text explanation paragraph
- Flow / sequence / class diagrams expressed as ASCII art are a violation when they could be
  expressed as Mermaid (warn level — use context to judge)

*Violation level*: Warning (non-blocking)

---

### DOC-INV-006: Goal image / E2E traceability

The goal-image layer is required but, unlike frontmatter, lives in section bodies — so it is
checked structurally here rather than being left to reviewer attention.

For each `docs/01_requirements/user_stories/US-*.md`:
- A `## ゴール像` section must exist, containing the subsections `完成時にできること`,
  `主要ユーザージャーニー`, and `非ゴール` (see `create-requirements`)

For each `docs/02_spec/**/*.md`:
- A `## E2E シナリオ` section must exist with at least one `### E2E-NNN:` heading
- Every AC referenced by the spec should appear in at least one scenario's `満たす AC`
  (warn if an AC belongs to no scenario)

For each `exec-plans/active/*.md`:
- At least one AC should be an E2E criterion (`- [ ] AC-NNN: [E2E] ...`)
- A plan with none is a **warning, not a violation** — it has legitimate causes: the plan predates
  the E2E requirement, or it is documentation-only. This matches how `run-tests` / `pre-pr` /
  `complete-exec-plan` treat the same situation (⚠️ report-only, does not block); keeping the doc
  gate stricter than the test gates would block on something the test gates deliberately let pass
- **Exemption**: a plan whose Decision Log records `E2E: n/a (documentation-only)` is not even a
  warning — report it as informational, since the criterion was considered and ruled out
- **The converse**: a plan that records `E2E: n/a (documentation-only)` **and** still defines an
  `[E2E]` AC is a ⚠️ warning. Such a plan cannot be completed — `run-tests` / `pre-pr` /
  `complete-exec-plan` hold on an `[E2E]` AC with no passing test, and `create-exec-plan` therefore
  forbids the combination. It stays a warning rather than a violation for the same reason as above:
  the document gate must not be stricter than the test gates that already block it

*Violation levels*:

| Item | Level |
|------|-------|
| US missing `## ゴール像` (or one of its three subsections) | ❌ Violation |
| Spec missing `## E2E シナリオ` (or it has no `E2E-NNN`) | ❌ Violation |
| Spec AC belonging to no `E2E-NNN` scenario | ⚠️ Warning |
| Active plan with no `[E2E]` AC | ⚠️ Warning |
| Active plan with `E2E: n/a (documentation-only)` recorded | ℹ️ Informational |
| Active plan recording `E2E: n/a (documentation-only)` that nonetheless has an `[E2E]` AC | ⚠️ Warning |

---

### DOC-INV-007〜012: Mechanical checks (script-backed)

These defect types are decidable without judgement. The first five each escaped every prose gate
in this repository at least once — an unquoted Mermaid label reached `main` and broke a diagram
completely, and nobody knew until a reader opened it in a browser. They are implemented once, in
[`../../scripts/check_doc_lint.py`](../../scripts/check_doc_lint.py), and this skill is the only
site that invokes it: `pre-pr` and `gc` reach it by running this skill, so there is no second copy
to drift.

| ID | Check | Detects | Level |
|----|-------|---------|-------|
| DOC-INV-007 | C1 relative link resolution | A relative Markdown link that resolves to no file | ❌ Violation |
| DOC-INV-008 | C2 table column consistency | A row whose column count differs from its header (a table split in half renders as prose) | ❌ Violation |
| DOC-INV-009 | C3 label reference existence | A label reference (`Q3d`, `Step 0b`, `§2c`, `⑤c`, `DOC-INV-NNN`, `INV-TNN`) absent from the file named just before it | ❌ Violation |
| DOC-INV-010 | C4 Mermaid label quoting | An unquoted Mermaid label containing `(`, `)`, `[`, `]`, `{` or `}` — one is enough to stop the parser, and the renderer reports only the first | ❌ Violation |
| DOC-INV-011 | C5 shell-snippet robustness | A multi-path `grep` in a `bash` fence without both `2>/dev/null` and `\|\| true`, which dies under `set -e` on a missing path or a no-match | ⚠️ Warning |
| DOC-INV-012 | C6 AC sources resolution | A file an **active** plan's `## Sources` row names that does not exist — every source in a cell is resolved, and `同上 § …` with no file above it to inherit is one too. A section (`§`) that cannot be matched, or a row naming a file with no section, is a ⚠️. The forms are defined in `../create-exec-plan/ac-sources.md`「Rules for the table」 | ❌ Violation (section: ⚠️) |

DOC-INV-011 is a warning rather than a violation because a snippet may legitimately want the
non-zero exit; the other checks have no such case, so they block. DOC-INV-012 blocks only on what is
unambiguous — a missing file. Section names are matched by heading text, which can drift in wording,
so an unmatched section is a warning: a reader can still tell a reworded heading from a missing one,
and that is the line `../create-exec-plan/ac-sources.md`「When a source cannot be opened」 draws for
the run itself (an unopenable row halts the loop; `n/a` does not).

**Range — wider than DOC-INV-001〜006 in one direction, narrower in another.** These five also read
`.claude/skills/**/*.md` and the root `*.md`, not only `docs/**` and `exec-plans/**`. That is where
the escapes happened: the convention documents are the ones carrying the cross-references, tables
and diagrams, and nothing was checking them. A range that does not exist in a given repository (no
`docs/`, no `exec-plans/active/`) is skipped rather than failing.

In the other direction, the two **pointer** checks — DOC-INV-007 (links) and DOC-INV-009 (label
references), which ask whether a reference resolves *right now* — skip `exec-plans/**`:

| Check | `docs/**` | `.claude/**`, root `*.md` | `exec-plans/**` |
|-------|:---------:|:-------------------------:|:---------------:|
| DOC-INV-007 · DOC-INV-009 (pointers) | ✅ | ✅ | — |
| DOC-INV-008 · DOC-INV-010 · DOC-INV-011 (structure) | ✅ | ✅ | ✅ |
| DOC-INV-012 (the one pointer check that reads plans) | — | — | `active/**`, `## Sources` table only |

A plan is a working note, not a reference document. This repository's own convention already says so:
a completed plan is archived and *not referenced* — which is why a reconcile record goes to the
**active** plan rather than the completed one (CLAUDE.md「現バージョン修正による stale の扱い」). A
stale pointer inside a plan therefore has almost no downstream consumer. Against that, a ❌ there
would block the PR of the very work the plan describes, and it would fire hardest at the start,
because an unchecked AC names what it is *about to* create and can only point at something that does
not exist yet. **Letting archived material drift is the cheaper trade: what is worth managing
mechanically is the material still in use.** Pointer drift inside a plan is left to the readers who
can judge it — process-walkthrough lap 7, `/doc-review`, `/docode-review`.

The structural three still cover plans, because they are not about pointers: a split `## Sources`
table breaks "a row for every AC" silently, and a broken diagram or an unguarded snippet is broken in
every state rather than only against today's tree.

**DOC-INV-012 is the deliberate exception**, and the reason is the same principle read the other
way. A `## Sources` table is not archive material: it is read *while the work is in flight* —
`run-exec-plan` Step 0b / 1b / 3a and `start-feature` Step 2 open what it names — so a row that does
not resolve stalls red-first now. It is therefore checked in `exec-plans/active/**` only. Completed
plans stay out: their drift is accepted, like every other pointer in a plan.

**What these checks deliberately do not decide.** Each exclusion exists because the check would
otherwise report something that is not a defect:

| Not checked | Why |
|-------------|-----|
| Anything under `exec-plans/**`, for DOC-INV-007 / 009 only | See the range note above — a plan is a working note, and its pointers are judged by the advisory readers rather than a blocking gate |
| A bare circled number (`③` without a letter) | Used as often for a local figure's boxes as for another skill's step; the two are indistinguishable mechanically. `⑤c` (with a letter) is only ever a pointer, so it is checked |
| A label whose file is named *after* it on the line | `(Step 1b / Step 3a), while at ` + "`pre-pr` ⑤c" + ` …` — the Steps belong to the skill named earlier, not to `pre-pr` |
| Links and labels inside fenced code blocks, and placeholders (`{name}`, `US-XXX`, `AC-NNN`) | Templates and examples, not live references |
| Whether a consumer has the material it needs at the point it decides | That is process-walkthrough lap 7 step 3 — it requires reading each skill from the top. The script makes step 2 (enumeration) cheap; it does not replace step 3 |
| A site that *should* consume a rule and never names it | A grep returns referrers only. The call-site table in each single source is what covers this |

---

## Steps

### Step 1: Collect all documents

```bash
find docs -name "*.md" 2>/dev/null | sort
find exec-plans -name "*.md" 2>/dev/null | sort
```

For each file:
- Parse the YAML frontmatter (content between the first pair of `---` delimiters)
- Extract all Markdown links: `[text](path)` patterns
- Note the file's layer number based on its path prefix

### Step 2: Check DOC-INV-001 (Reference direction)

Assign layer numbers:

| Prefix | Layer |
|--------|-------|
| `docs/01_requirements/` | 1 |
| `docs/02_spec/` | 2 |
| `exec-plans/` | 2.5 |
| `docs/03_design/` | 3 |
| `docs/04_implementation/` | 4 |
| `docs/04_implementation/invariants.md` | 4 |
| `docs/05_quality/` | 5 |
| `docs/06_*/` and `docs/07_*/` | 6+ |

For each link `[text](target)` in a document at layer N:
- Resolve `target` relative to the repository root
- Determine target layer M
- If M > N → violation (higher-layer document referencing a lower-layer document)

Skip external URLs (starting with `http://` or `https://`).

### Step 3: Check DOC-INV-002 (Frontmatter completeness)

For each `docs/**/*.md`:
1. Check `status:` exists and is `draft`, `active`, or `deprecated`
2. For `docs/03_design/` and `docs/04_implementation/` files: check `tracks:` key exists
3. For `docs/01_requirements/user_stories/US-*.md`: check `ac_ids:` exists and is a non-empty list

### Step 4: Check DOC-INV-003 (Lifecycle consistency)

1. Build a map: file path → `status:` value
2. For each `active` document, scan its links
3. For each linked path, look up its status in the map
4. Flag any link from an `active` document to a `deprecated` target

### Step 5: Check DOC-INV-004 (AC traceability)

1. Collect exec-plan AC-IDs: scan `exec-plans/active/*.md` for lines matching
   `- \[[ x]\] AC-\d+:` and extract the identifiers
2. Collect US AC mappings: from each `docs/01_requirements/user_stories/US-*.md`,
   read `ac_ids:` frontmatter
3. Cross-check:
   - For each exec-plan AC-ID: is it present in any US's `ac_ids:`? If not → violation
   - For each US `ac_ids:` entry: is it present in any exec-plan? If not → warning

### Step 6: Check DOC-INV-005 (Diagram rules)

For each `docs/**/*.md` and `exec-plans/**/*.md`:
1. Find ASCII art blocks: consecutive lines starting with box-drawing characters or `+--`
2. Check that within 3 lines after the block ends, a non-empty paragraph exists
3. If not → warning

### Step 7: Check DOC-INV-006 (Goal image / E2E traceability)

1. For each `docs/01_requirements/user_stories/US-*.md`: check for a `## ゴール像` heading and its
   three required subsections
2. For each `docs/02_spec/**/*.md`: check for a `## E2E シナリオ` heading and at least one
   `### E2E-NNN:`; collect the `満たす AC` lists and compare against the ACs the spec references
3. For each `exec-plans/active/*.md`: check for at least one `- [ ] AC-NNN: [E2E]` /
   `- [x] AC-NNN: [E2E]` line, and for `E2E: n/a` in the `## Decision Log`

   | `[E2E]` AC | `E2E: n/a` recorded | Report |
   |:----------:|:-------------------:|--------|
   | present | absent | ✅ (nothing to report) |
   | absent | present | ℹ️ informational — documentation-only, criterion ruled out |
   | absent | absent | ⚠️ warning (not a violation), matching how `run-tests` / `pre-pr` / `complete-exec-plan` treat a plan with no `[E2E]` AC |
   | present | present | ⚠️ warning — contradictory: the plan calls itself documentation-only yet carries a criterion the test gates will hold on |

---

### Step 8: Check DOC-INV-007〜012 (mechanical checks)

Run the single script entity once, from the repository root:

```bash
python3 .claude/scripts/check_doc_lint.py
```

- Exit code `1` means at least one ❌ violation: **blocking**
- Exit code `0` means no ❌. Any ⚠️ lines present are report-only — DOC-INV-011, DOC-INV-012's
  unmatched sections, and with `--mermaid-parser` a DOC-INV-010 warning when the parser could not run
  (see below). The exit code is what decides blocking; the invariant a ⚠️ is filed under does not
- `--mermaid-parser` additionally runs Mermaid's own parser (needs `node` + `mermaid` + `jsdom`).
  It is opt-in so the checks never require a Node toolchain; when those are unavailable, or the
  parser run itself fails, the finding is a **⚠️ under DOC-INV-010** and the exit code is unchanged
  — a check that could not run is not a passing check, and not a violation either
- `--only C1,C4` restricts the run; `--root <path>` checks another checkout

Do not restate the checks inline anywhere else, and do not add a second call site: the reason this
is one script called from one skill is that a duplicated list is what went stale before
(`pre-pr` ③ and `gc` ③ both enumerated DOC-INV-001〜006 by hand).

---

## Result report format

```
=== Document invariant check results ===

Documents checked : {count}
Exec-plans checked: {count}

❌ DOC-INV-001 violations (reference direction): {count}
  - docs/01_requirements/user_stories/US-001_foo.md → docs/03_design/api_spec.md (line 12)
    Fix: Remove or replace the forward reference with a plain description

❌ DOC-INV-002 violations (frontmatter): {count}
  - docs/03_design/data_model.md: missing tracks:
    Fix: Add tracks: field pointing to relevant source files

❌ DOC-INV-003 violations (lifecycle): {count}
  - docs/03_design/api_spec.md (active) → docs/03_design/old_api.md (deprecated) at line 34
    Fix: Update the link to the successor document, or remove the reference

❌ DOC-INV-004 violations (AC traceability): {count}
  - AC-003 in exec-plans/active/2026-01-feature.md has no matching US ac_ids:
    Fix: Add AC-003 to the corresponding US file's ac_ids: frontmatter

⚠️ DOC-INV-005 warnings (diagram rules): {count}
  - docs/03_design/screen_layout.md: ASCII art at line 42 has no following description
    Fix: Add a plain-text explanation paragraph immediately after the diagram

❌ DOC-INV-006 violations (goal image / E2E): {count}
  - docs/01_requirements/user_stories/US-001_foo.md: no ## ゴール像 section
    Fix: Run /create-requirements Q4, or add 完成時にできること / 主要ユーザージャーニー / 非ゴール

⚠️ DOC-INV-006 warnings: {count}
  - docs/02_spec/app_spec.md: AC-004 belongs to no E2E-NNN scenario
  - exec-plans/active/2026-01-feature.md: no [E2E] AC (predates the requirement?)
    Fix: Add an [E2E] AC (see create-exec-plan), or record E2E: n/a if documentation-only
  - exec-plans/active/2026-03-docs.md: records E2E: n/a but defines AC-004 [E2E]
    Fix: Restate AC-004 as an ordinary functional AC — the test gates will hold on it otherwise
  ℹ️ exec-plans/active/2026-02-docs.md: documentation-only, E2E exempt

{the output of .claude/scripts/check_doc_lint.py, verbatim — DOC-INV-007〜012}

---
Overall: ✅ All passed / ❌ {count} violation(s) / ⚠️ {count} warning(s)
```

---

## Completion criteria

- [ ] All `docs/**/*.md` and `exec-plans/**/*.md` collected
- [ ] DOC-INV-001 through DOC-INV-006 checked
- [ ] DOC-INV-007 through DOC-INV-011 checked by running `.claude/scripts/check_doc_lint.py`
      (its wider range covers `.claude/skills/**/*.md` and the root `*.md` as well)
- [ ] DOC-INV-012 checked by the same run, over `exec-plans/active/**` `## Sources` tables only
- [ ] All violations reported with specific file paths, line numbers, and fix instructions
- [ ] Result report output
