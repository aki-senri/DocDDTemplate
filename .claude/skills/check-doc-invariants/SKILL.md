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
| 0 – Project | `docs/00_project/` | External resources and layer 0 only. Every other layer may reference it |
| 1 – Requirements | `docs/01_requirements/` | External resources, layer 0, layer 1 (`constraints.md`), the E2E scenarios |
| 1〜2 – E2E scenarios (a **range**) | `docs/01-02_e2e/` | Layers 0–2, and the other scenarios |
| 2 – Spec | `docs/02_spec/` | Layers 0–2, including the E2E scenarios |
| 2.5 – Exec-plans | `exec-plans/` | Layers 0–2 (US files, E2E scenarios, spec sections) |
| 3 – Design | `docs/03_design/` | Layers 0–3 (including exec-plans and the E2E scenarios) |
| 4 – Implementation | `docs/04_implementation/` | Layers 0–4 |
| 5 – Quality | `docs/05_quality/` | All `docs/` layers |

**Violation examples**: A `docs/01_requirements/` file links to `docs/03_design/api_spec.md`. A
`docs/00_project/decisions.md` ADR links to `docs/02_spec/app_spec.md`. A scenario in
`docs/01-02_e2e/` links to `docs/03_design/ui_flows.md`.

**Layer 0 is the most abstract layer, and references nothing below it.** `docs/00_project/` holds
the material decisions are made *from* — the overview, the glossary, the ADRs in `decisions.md`, the
research notes under `research/`. Every layer may cite it, which is what lets a US point at the ADR
behind a constraint. It may not link back down: material that links to the spec it informed has
started to depend on its own conclusion. When an ADR needs to say where a decision landed, it names
the document in prose — a mention is not a link and is not checked. (Being readable from every layer
does not make it a source for a test: `../create-exec-plan/ac-sources.md`「What counts as a source」
classes it as background.)

**No grace period applies to layer 0.** A project whose `docs/00_project/` already links down — an
`overview.md` ported from a README that links into `docs/`, an ADR linking the design it chose —
gets DOC-INV-001 ❌ the first time this check runs. The fix is mechanical and changes no meaning:
turn each such link into a prose mention of the document (its path or title in backticks, not a
Markdown link). Unlike the E2E move below, nothing else points at these links, so there is no
reason to stage it.

**A range layer spans more than one layer.** A directory whose prefix is a range — `docs/LO-HI_*/`
— holds documents that stand in a **two-way** relationship with every layer from LO to HI, which no
single number can express: given a number, a document sits on the line, above one neighbour and
below the other. The rule for a range is mechanical:

| The range is… | It counts as | So |
|---------------|--------------|----|
| the **target** of a link | its lowest layer, LO | every layer numbered LO or higher may link to it |
| the **source** of a link | its highest layer, HI | it may link to any layer numbered HI or lower |

Between two ranges, compare the source's HI with the target's LO. Today one range exists,
`docs/01-02_e2e/` — the E2E scenarios. Applied to it:

| Link | Counts as | Verdict |
|------|-----------|---------|
| US (1) → `01-02_e2e` | 1 → 1 | ✅ |
| Spec (2) → `01-02_e2e`, and exec-plan (2.5) → `01-02_e2e` | 2 → 1, 2.5 → 1 | ✅ |
| `01-02_e2e` → US (1), → spec (2) | 2 → 1, 2 → 2 | ✅ — the two-way part |
| `01-02_e2e` → `docs/03_design/` (3) | 2 → 3 | ❌ |
| `docs/00_project/` (0) → `01-02_e2e` | 0 → 1 | ❌ |

Why the E2E scenarios get a range rather than a number: a scenario is written from the US goal image
and the spec is written with it, yet working the scenario out is also how gaps in the requirements
and the spec are found, so each of the three may correct the others until a plan freezes the
scenario. Numbering it `02` makes it the spec's peer and the requirements' downstream; renumbering
everything to put it between them makes it the spec's upstream. Either reading is wrong. The range
names the band it spans. **What this invariant governs is only which links may exist.** Which
document may correct which, and when that stops, is the freeze rule in
`../create-spec/e2e-interaction.md`, not this table.

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

For the E2E scenarios — one file each, `docs/01-02_e2e/E2E-NNN_{slug}.md` (see `create-spec`):
- Each file must carry a `# E2E-NNN:` heading whose ID matches its file name, and the lines
  `前提:`, `完了条件:` and `満たす AC:` — the material an `[E2E]` AC is transcribed from. It should
  also carry `由来ジャーニー: US-NNN` and `満たす業務要求: {docs/00_project/ path § section | n/a（理由）}`
  (`create-spec`); missing, those two are warnings, not violations (see「Upward trace」)
- When `docs/02_spec/**/*.md` exists, at least one scenario must exist, in either layout below
- Every AC referenced by the spec should appear in at least one scenario's `満たす AC`, in either
  layout (warn if an AC belongs to no scenario)
- An `E2E-NNN` defined in more than one place — two files, or a file and an old-layout section —
  is a warning: the ID is meant to be unique, and the freeze search
  (`../create-spec/e2e-interaction.md`) can no longer tell which definition a plan froze
- Each scenario's **upward trace** — its `由来ジャーニー:` and `満たす業務要求:` lines — is checked
  as described under「Upward trace」 below, in both layouts
- Each scenario is compared against the requirements and spec beside it — the **symmetric check**
  below. Its findings are advisory and never block

**Upward trace.** `満たす AC` traces a scenario across the ACs; the two lines above it trace it up,
to the journey it realizes and to the business requirement outside the US (`create-spec`). A line
that is **missing** is a ⚠️ — a scenario written before the lines existed is not broken, only
untraced, the same grace the old layout gets. A line that is **present but points nowhere** is a ❌:
it claims a trace that does not exist, which is worse than claiming none.

**Adding a missing line is an edit to the scenario**, not bookkeeping. `由来ジャーニー` widens
comparison set #2 for every plan that froze the scenario (`../create-spec/e2e-interaction.md`), so on
an approved scenario the addition is routed like any other edit (CLAUDE.md「変更のルーティング」) and
the plans that froze it are searched for (`e2e-interaction.md`「The freeze is per plan」). That is
also why whoever runs this check — `gc` included — reports a missing line and never fills it in.

| Line | ⚠️ when | ❌ when |
|------|---------|---------|
| `由来ジャーニー:` | the line is missing | an ID names no `docs/01_requirements/user_stories/US-NNN_*.md`, or names a US that has no `## ゴール像` |
| `満たす業務要求:` | the line is missing | the value is neither `n/a（理由）` nor a path under `docs/00_project/`, or the path names no file |

And in the other direction, the check that makes `由来ジャーニー` traceability rather than a
self-report: when `docs/02_spec/**/*.md` exists, every US with an AC the spec references should be
named under `由来ジャーニー` by at least one scenario, in either layout. A US that none names is a ⚠️:
its journey is realized by no scenario — usually a path the spec dropped, or a scenario that forgot
the line. **Skip a US whose ACs appear only in scenarios that lack the line** — the missing-line ⚠️
on those scenarios already reports the cause, and a legacy project would otherwise get a second ⚠️ for
every US it has. The US is checked again once those scenarios carry the line.

**Symmetric check.** The bullets above look only one way: an AC that belongs to no scenario is
reported, but a scenario step that belongs to no requirement is not, so a scenario that says more than
the US and the spec passes every gate. This check closes that, by comparing each scenario's 前提,
steps and 完了条件 against the comparison set that `../create-spec/e2e-interaction.md` defines —
here without a plan, so its #1 (the plan's row) is n/a, and its #2 (the goal images of the USs under
`由来ジャーニー`) and #3 (the US and spec sections of each AC under `満たす AC`) are the whole set.
While a scenario has no `由来ジャーニー` line (already a ⚠️ above), #2 uses the advisory-site
fallback that file defines (「Where this is applied」 — the goal images of the USs owning its
`満たす AC` entries), and the report says so. A line that is present but names a US that does not
exist or has no goal image gets no fallback: the scenario is not compared, and no 要確認 is added —
the upward-trace ❌ above already names the cause (same section of that file). The
verdicts are that file's; the report sorts them by **what a human has to do**, because a symmetric
check rings about twice as often as a one-way one and the count that matters is the decisions it
asks for:

| Tier | Finding | Who acts, and how |
|------|---------|-------------------|
| ⚠️ **要決定** | A requirements gap (an outcome stated nowhere in the set) or a contradiction | A human: ① promote / ② drop / ③ rework for a gap, or a choice of target and the edit that follows for a contradiction (`e2e-interaction.md`) |
| ⚠️ **要確認** | The set cannot be assembled even with the fallback — a `満たす AC` entry's US or spec section cannot be identified, or no US is found for #2 — so whether a step is stated cannot be decided | A human completes the trace; the comparison runs on the next check |
| ℹ️ | A finding an active plan's Decision Log records under a `deferred:` line with no later `deferred 解除:` line (`e2e-interaction.md`「Deferring a plan, and lifting it」). Once lifted, a finding still on `main` is 要決定 again | Nobody, for now — the decision was made and is waiting on a promotion |

None of these blocks: the check judges meaning, which a reader can get wrong, and the gates that act
on a finding — `create-exec-plan` Q3d before a plan freezes the scenario, `run-exec-plan` Step 0b
after — already exist and are where a halt belongs (`e2e-interaction.md`「Where this is applied」).
**Whoever runs this check edits nothing**: not the scenario, not the US, not the spec. Each of ①–③
and a contradiction's edit is a spec change a human routes (CLAUDE.md「変更のルーティング」). A
refinement — the scenario stating concretely what the set states — is not a finding at all.

**The old layout is still read, during a grace period.** Scenarios used to be a `## E2E シナリオ`
section inside a spec file, with `### E2E-NNN:` headings. A project generated before the move keeps
working: its old-layout scenarios count for both checks above, and the section is reported as a
⚠️ **migration candidate**, not a violation. Moving it is a human's step, because a scenario that an
active plan names in `## Sources` breaks that row the moment the scenario moves:

1. Cut each `### E2E-NNN:` block into its own file `docs/01-02_e2e/E2E-NNN_{slug}.md`, with
   `status:` copied from the spec file and the heading raised to `# E2E-NNN:`. Keep the ID. Do not
   add `由来ジャーニー` / `満たす業務要求` as part of the move: the move keeps the content, and adding
   a line is an edit (「Upward trace」) — do it as a separate, routed change
2. Remove the section (and its summary table) from the spec file.
3. Find the plans that name each moved scenario
   (`grep -rn "E2E-NNN" exec-plans/active/ 2>/dev/null || true` — only hits in a `## Sources` row
   count) and repoint those rows to the new file **in the same commit**, by hand
   (`../create-exec-plan/ac-sources.md`「When a source cannot be opened」). A row left behind is
   only a DOC-INV-012 **⚠️**, not a ❌: the spec file still exists and only its `§ E2E-NNN` section
   is gone, so the PR is not blocked — but the plan's next run halts with (a) at Step 0b, because
   the row can no longer be opened. Treat that ⚠️ as one to fix before merging the move.

Moving a scenario changes where it lives, not what it says, so it is an in-version fix
(CLAUDE.md「変更のルーティング」) and does not move the target of a plan that froze it.

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
| A spec exists but no scenario exists in either layout | ❌ Violation |
| A scenario file without a `# E2E-NNN:` heading matching its file name, or without `前提:` / `完了条件:` / `満たす AC:` | ❌ Violation |
| Spec AC belonging to no `E2E-NNN` scenario | ⚠️ Warning |
| A spec file with an old-layout `## E2E シナリオ` section (migration candidate) | ⚠️ Warning |
| An `E2E-NNN` defined in more than one place | ⚠️ Warning |
| A scenario's `由来ジャーニー:` or `満たす業務要求:` line is missing | ⚠️ Warning |
| `由来ジャーニー:` names no US file, or a US without `## ゴール像` | ❌ Violation |
| `満たす業務要求:` is neither `n/a（理由）` nor an existing file under `docs/00_project/` | ❌ Violation |
| A US with an AC the spec references that no scenario names under `由来ジャーニー` | ⚠️ Warning |
| Symmetric check: a requirements gap or a contradiction (要決定) | ⚠️ Warning — advisory, never repaired by the checker |
| Symmetric check: the comparison set cannot be assembled (要確認) | ⚠️ Warning |
| Symmetric check: a finding an active plan records as `deferred:`, not yet lifted | ℹ️ Informational |
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
| DOC-INV-012 | C6 AC sources resolution | A file an **active** plan's `## Sources` row names that does not exist — every source in a cell is resolved, and `同上 § …` with no file above it to inherit is one too. A section (`§`) that cannot be matched, or a row naming a file with no section, is a ⚠️. The forms are defined in `../create-exec-plan/ac-sources.md`「Rules for the table」 | ❌ Violation (section: ⚠️). For a PR, only the rows the PR is answerable for block — see「Which ❌ blocks which run」 |

DOC-INV-011 is a warning rather than a violation because a snippet may legitimately want the
non-zero exit; the other checks have no such case, so they block. DOC-INV-012 blocks only on what is
unambiguous — a missing file. Section names are matched by heading text, which can drift in wording,
so an unmatched section is a warning: a reader can still tell a reworded heading from a missing one,
and that is the line `../create-exec-plan/ac-sources.md`「When a source cannot be opened」 draws for
the run itself (an unopenable row halts the loop; `n/a` does not).

**Range — wider than DOC-INV-001〜006 in one direction, narrower in another.** DOC-INV-007〜011 also
read `.claude/skills/**/*.md` and the root `*.md`, not only `docs/**` and `exec-plans/**`
(DOC-INV-012 reads only active plans' `## Sources` tables — see below). That is where
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

A DOC-INV-012 finding is **reported, never repaired by whoever runs this check** — `pre-pr`, `gc` or
a driver. Repointing a row, or deciding there is nothing to read after all, is a decision about what
the AC condenses, and it belongs to a human (`../create-exec-plan/ac-sources.md`「When a source cannot
be opened」). The fix hint the script prints says the same.

**Which ❌ blocks which run.** DOC-INV-012 reads every active plan, but a PR is answerable for only
some of them. A row can break through a change that never passes `pre-pr` — a promotion pushed in
`promote-spec` Step 6, a fix made directly on `main` — and if every ❌ blocked every PR, each PR after
it would stop on a plan it never touched. So the run made for a PR (`pre-pr` ③) passes
`--base <the PR's base branch>` (Step 8), and an ❌ blocks that PR only in the first two rows:

| The row | In PR mode | Why |
|---------|-----------|-----|
| is in a plan the branch changed or added since its merge-base with the base — committed, in the working tree, or untracked (a new plan, or a gitignored one) | ❌ blocks | It is the PR's own work: the row is about to be read, or has just been written |
| names a file the branch deleted or renamed away — in **any** plan | ❌ blocks | The PR broke it. Repointing belongs in the same change as the move (`../create-exec-plan/ac-sources.md`, "Moving a source breaks rows elsewhere") |
| anything else | ❌ listed apart, under "In other plans — not blocking this PR"; the exit code ignores it | Another plan's row, broken by a change that is already in the base. It is presented so that plan's owner is told — and, like every DOC-INV-012 finding, not repaired by whoever runs the check |

**When the split cannot be made, nothing is downgraded** — git is unavailable, the base does not
resolve (or looks like an option), `--root` is not the top of the repository, or the working tree
does not differ from the base at all. The report says which, and every ❌ blocks. That is the
direction to err in: misplacing the PR's own row as "someone else's" would let the PR go ahead on a
row nobody can open, which is the path this check exists to close. Paths are compared the way the
file system resolves them — case-folded where it ignores case, and Unicode-normalized — since a row
that names `docs/a.md` opens `docs/A.md` there, and the PR that deletes `docs/A.md` has broken it.

A change with no plan (the spec-override exception) is split like any other: it changes no plan, so
it blocks only on rows naming a file it deleted or renamed. A PR that repoints another plan's row —
as `../create-exec-plan/ac-sources.md` requires ("Moving a source breaks rows elsewhere") — changes
that plan, so it becomes answerable for that plan's other broken rows too; that errs toward
blocking, and the fix is the same repointing.

**Pass an up-to-date base.** The split is only as good as the merge-base. A local `main` that is
behind — in a worktree it usually is — puts changes already on the base into the diff, so another
plan's rows broken by them look like this PR's and block (safely, but for nothing). Fetch first and
pass the remote-tracking branch (`origin/main`); without a remote, the local base branch. A branch
with no commits of its own — `run-exec-plan` does not commit — is fine behind a base that has moved
on: the merge-base is its HEAD and the diff is exactly its working tree. What the script cannot catch
is a base that is not the PR's target at all (one that already holds the branch's commits hides
them from the diff), so pass the branch the PR merges into and nothing else.

A run without `--base` — `gc` ③'s full scan, a standalone run — blocks on every ❌, as it always
has. That is the **backstop**: a row one PR listed under another plan stays an ❌ in every `gc`
report until it is repointed, and it always blocks its own plan's PR (first row above).

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
| `docs/00_project/` | 0 |
| `docs/01_requirements/` | 1 |
| `docs/01-02_e2e/` | 1〜2 (a range — see below) |
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

For a **range** layer (`docs/LO-HI_*/`), use its lowest layer when it is the target and its highest
when it is the source — `docs/01-02_e2e/` is 1 as a target and 2 as a source. That single
substitution is the whole of the range rule; see the examples under DOC-INV-001 above.

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
2. Collect the scenarios from both layouts:
   - each `docs/01-02_e2e/E2E-*.md`: check its `# E2E-NNN:` heading against its file name and its
     `前提:` / `完了条件:` / `満たす AC:` lines
   - each `docs/02_spec/**/*.md` with a `## E2E シナリオ` section: read its `### E2E-NNN:` blocks,
     and report the section as a migration candidate (⚠️)

   If `docs/02_spec/**/*.md` exists and neither layout yielded a scenario → ❌. Report any ID found
   twice (⚠️). Then compare the union of the `満たす AC` lists against the ACs the spec references
3. For each scenario, in either layout, check the upward trace: `由来ジャーニー:` (missing → ⚠️;
   an ID with no US file, or a US without `## ゴール像` → ❌) and `満たす業務要求:` (missing → ⚠️;
   neither `n/a（理由）` nor an existing file under `docs/00_project/` → ❌). If a spec exists,
   collect the USs owning an AC the spec references, and report each one that no scenario names
   under `由来ジャーニー` (⚠️) — skipping a US whose ACs appear only in scenarios lacking the line
4. Run the symmetric check on each scenario: compare its 前提, steps and 完了条件 against
   comparison set #2 and #3 of `../create-spec/e2e-interaction.md` (#1 is n/a — there is no plan
   row; without `由来ジャーニー`, #2 is the fallback `e2e-interaction.md`「Where this is applied」
   defines).
   Report a gap or a contradiction as ⚠️ 要決定, a set that cannot be assembled as
   ⚠️ 要確認, and a finding under an active plan's unlifted `deferred:` line as ℹ️ — and edit
   no document
5. For each `exec-plans/active/*.md`: check for at least one `- [ ] AC-NNN: [E2E]` /
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

- Exit code `1` means at least one ❌ violation: **blocking**. In PR mode (below), DOC-INV-012 ❌s
  listed under "In other plans — not blocking this PR" do not count toward it
- Exit code `0` means no ❌. Any ⚠️ lines present are report-only — DOC-INV-011, DOC-INV-012's
  unmatched sections, and with `--mermaid-parser` a DOC-INV-010 warning when the parser could not run
  (see below). The exit code is what decides blocking; the invariant a ⚠️ is filed under does not
- `--mermaid-parser` additionally runs Mermaid's own parser (needs `node` + `mermaid` + `jsdom`).
  It is opt-in so the checks never require a Node toolchain; when those are unavailable, or the
  parser run itself fails, the finding is a **⚠️ under DOC-INV-010** and the exit code is unchanged
  — a check that could not run is not a passing check, and not a violation either
- `--base <ref>` is **PR mode**, and only `pre-pr` ③ passes it — `<ref>` is the up-to-date branch
  the PR will merge into: after a fetch, `origin/main` (unless the PR targets another branch; see
  "Pass an up-to-date base" above). It changes which DOC-INV-012 ❌s block, and
  nothing else (「Which ❌ blocks which run」 above). `gc` ③ and a standalone run omit it, so every
  ❌ blocks there. Do not pass it to make a run pass: if the split cannot be made the script blocks
  on everything and says why — fix that cause, not the flag
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
  - docs/01-02_e2e/E2E-006_report.md: 由来ジャーニー: US-007 — US-007 has no ## ゴール像
    Fix: Run /create-requirements Q4 on US-007 (the scenario is skipped by the symmetric check until then)
  - docs/01-02_e2e/E2E-002_export.md: 由来ジャーニー: US-009 — no such US file
    Fix: Name the US whose journey this scenario realizes (or add the line's US); do not leave a
         trace that points nowhere
  - docs/01-02_e2e/E2E-003_audit.md: 満たす業務要求: docs/02_spec/app_spec.md is not under docs/00_project/
    Fix: Point at where the business requirement is recorded in docs/00_project/, or write n/a（理由）

⚠️ DOC-INV-006 warnings: {count}
  - docs/02_spec/app_spec.md: AC-004 belongs to no E2E-NNN scenario
  - docs/01-02_e2e/E2E-007_legacy.md: no 由来ジャーニー: line
    Fix: Name the US whose journey it realizes — a routed edit to an approved scenario (「Upward trace」)
  - docs/01-02_e2e/E2E-001_tag-and-filter.md: no 満たす業務要求: line
    Fix: Add the outer anchor (a docs/00_project/ path and section) or n/a（理由）
  - docs/01_requirements/user_stories/US-004_share.md: named under 由来ジャーニー by no scenario
    Fix: Check whether the spec dropped this journey, or a scenario is missing the line
  - 要決定 docs/01-02_e2e/E2E-001_tag-and-filter.md: 完了条件「CSV に書き出せる」is stated nowhere in
    the comparison set (US-003 § ゴール像, AC-001 / AC-003 US and spec sections) — requirements gap
    Decide: ① promote it into the US / spec ② drop it from the scenario ③ rework the US
            (e2e-interaction.md). Nothing was edited by this check
  - 要確認 docs/01-02_e2e/E2E-005_import.md: 満たす AC lists AC-012, which no US defines — comparison
    set #3 cannot be assembled
    Fix: Correct the 満たす AC entry (an edit to the scenario — routed); the check runs on the next pass
  - docs/02_spec/app_spec.md: ## E2E シナリオ (E2E-001, E2E-002) is in the old layout — migration candidate
    Fix: Cut each scenario into docs/01-02_e2e/E2E-NNN_{slug}.md, remove the section, and repoint
         every active plan's ## Sources row that names it, in the same commit (see DOC-INV-006)
  - exec-plans/active/2026-01-feature.md: no [E2E] AC (predates the requirement?)
    Fix: Add an [E2E] AC (see create-exec-plan), or record E2E: n/a if documentation-only
  - exec-plans/active/2026-03-docs.md: records E2E: n/a but defines AC-004 [E2E]
    Fix: Restate AC-004 as an ordinary functional AC — the test gates will hold on it otherwise
  ℹ️ exec-plans/active/2026-02-docs.md: documentation-only, E2E exempt
  ℹ️ docs/01-02_e2e/E2E-004_bulk.md: gap「一括削除」recorded as deferred in
     exec-plans/active/2026-03-bulk.md (until spec/sprint-12) — not re-raised

{the output of .claude/scripts/check_doc_lint.py, verbatim — DOC-INV-007〜012}

---
Overall: ✅ All passed / ❌ {count} violation(s) / ⚠️ {count} warning(s)
         [/ ❌ {count} in other plans (not blocking) — PR mode only, DOC-INV-012]
```

---

## Completion criteria

- [ ] All `docs/**/*.md` and `exec-plans/**/*.md` collected
- [ ] DOC-INV-001 through DOC-INV-006 checked
- [ ] DOC-INV-007 through DOC-INV-011 checked by running `.claude/scripts/check_doc_lint.py`
      (its wider range covers `.claude/skills/**/*.md` and the root `*.md` as well)
- [ ] DOC-INV-012 checked by the same run, over `exec-plans/active/**` `## Sources` tables only —
      with `--base` when the run is `pre-pr` ③'s, and without it otherwise
- [ ] All violations reported with specific file paths, line numbers, and fix instructions
- [ ] Result report output
