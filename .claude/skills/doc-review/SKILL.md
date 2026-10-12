---
name: doc-review
description: |
  Launches an independent agent (with no authoring context) to review a requirement
  or design document from a DocDD perspective.
  Checks AC testability (using the shared AC readiness criteria), completeness, ambiguity,
  cross-reference integrity, and whether the document's decisions have a recorded basis.
  Optional skill — run after writing docs, before /create-exec-plan.
# disable-model-invocation is intentionally false: this skill's core function is to spawn
# an independent subagent via the Agent tool, which requires model invocation.
disable-model-invocation: false
---

# Skill: Independent Document Review

> **When to run**: After writing or updating a requirements or design document,
> before running `/create-exec-plan`
>
> **Purpose**: Get an objective review from an agent that has no knowledge of the authoring
> decisions. This catches DocDD-specific quality issues — vague ACs, untraceable references,
> broken lifecycle state — that automated structural checks cannot detect.
>
> **Prerequisites**:
> - The target document must exist and be saved
> - `docs/` directory structure must be in place (Phase 1 complete)

---

## Background: the `Agent` tool

This skill spawns a **fresh subagent** via the `Agent` tool in an isolated context.
The subagent has no memory of the current session and reviews the document from scratch,
providing the same independence guarantee as `/code-review`.

---

## What this skill does

1. Identify the target document and its type
2. Load the document content and related context files
3. Spawn an independent agent with a structured DocDD-aware review prompt
4. Present the findings and recommend the next step

---

## Steps

### Step 1: Identify target

If the user has not specified a document path, ask:

> "Which document do you want to review? Please provide the path
> (e.g., `docs/01_requirements/user_stories/US-001_foo.md`)"

Then determine the document type from its path:

| Path pattern | Document type |
|-------------|---------------|
| `docs/01_requirements/user_stories/US-*.md` | User Story |
| `docs/01-02_e2e/E2E-*.md` | E2E scenario |
| `docs/02_spec/**/*.md` | Application spec |
| `docs/03_design/**/*.md` | Design document |
| `docs/04_implementation/**/*.md` | Implementation document |
| `exec-plans/**/*.md` | Exec-plan |
| `docs/00_project/decisions.md` | Decision record (ADR) |
| `docs/00_project/research/*.md` | Research note |
| Other `docs/**/*.md` | General document |

### Step 2: Load context

Collect content for the review prompt using the appropriate commands below.

```bash
# Target document (always)
cat {target document path}

# For User Story review: load constraints and any related exec-plan
cat docs/01_requirements/constraints.md 2>/dev/null || echo "not found"
grep -l "AC-" exec-plans/active/*.md 2>/dev/null | head -3 | xargs cat 2>/dev/null || echo "no active exec-plans"

# For exec-plan review: load every section the plan's ## Sources table names.
# R2 is judged against the AC line AND its sources (ac-readiness.md), so a reviewer
# given only the one-liners would return a stricter verdict than the other gates.
# A row naming background material — anything ac-sources.md「What counts as a source」
# does not class as a source (research note, ADR, another plan's Decision Log, design
# document) — is not a source: pass it as such, not as its text (ac-sources.md「When a
# row names background material」).
sed -n '/^## Sources/,/^## /p' {target exec-plan} 2>/dev/null || echo "no ## Sources table"
cat docs/01_requirements/user_stories/{referenced-US}.md 2>/dev/null || echo "not found"
cat docs/02_spec/{referenced-spec}.md 2>/dev/null || echo "not found"
cat docs/01-02_e2e/{referenced-scenario}.md 2>/dev/null || echo "not found"

# For a spec or scenario review: the scenarios are separate files (one per E2E-NNN), so the
# AC coverage check below needs all of them, not only the spec file.
cat docs/01-02_e2e/E2E-*.md 2>/dev/null || echo "no scenario files (old layout, or no spec yet)"

# For a spec or scenario review: the symmetric comparison in §2b reads each scenario against
# its comparison set — the US files its 由来ジャーニー names (their ## ゴール像) and the US and
# spec sections of every AC under 満たす AC — and takes the verdicts from e2e-interaction.md.
cat .claude/skills/create-spec/e2e-interaction.md
cat docs/01_requirements/user_stories/US-NNN_*.md 2>/dev/null || echo "not found"   # each US under 由来ジャーニー (or, without the line, owning a 満たす AC entry)

# Decision basis — for a User Story, spec, scenario, ADR or research note (§6 judges whether the
# document's decisions have a recorded basis). The reviewer needs what the document cites as its
# basis, the ADRs, and the format they are judged against — not only the document.
sed -n '/^## 関連/,/^## /p' {target document path} 2>/dev/null || true
cat docs/00_project/decisions.md 2>/dev/null || echo "no decisions.md"
cat {each in-repo file the target's ## 関連 names, e.g. docs/00_project/research/{topic}.md} 2>/dev/null || echo "not found"
# For decisions.md as the target: the in-repo files its ADRs name under 根拠資料.
# For a scenario: the document its 満たす業務要求 names (its recorded outer anchor).
cat {each such in-repo file} 2>/dev/null || echo "not found"
cat .claude/skills/init-project/adr-format.md
cat .claude/skills/init-project/research-note-format.md   # for a research note, or a ## 関連 that names one

# Project documentation rules
cat CLAUDE.md

# AC readiness criteria — the shared testability checks (always, when the document has ACs)
cat .claude/skills/create-exec-plan/ac-readiness.md

# Process walkthrough laps — when the document describes a process (a loop, a resumable
# run, a stop condition, a gate, an exemption) OR states a rule other documents consume.
# Keep this condition identical to §2c's: a rule document has no loop of its own, and
# collecting on the narrower condition would leave §2c telling the reviewer to apply a
# single source it was never handed.
cat .claude/skills/create-exec-plan/process-walkthrough.md

# Referrers — only when the document states a rule other documents consume.
# §2c's dependency-backflow lap judges whether each consuming site has what the rule now
# requires, so the reviewer needs the consumers themselves, not just this document.
# Start from the document's own call-site table, then widen by grep on BOTH the file name
# and the rule's IDs — a site can name the rule (R2, INV-T02, DOC-INV-001) without ever
# naming the file, and that site is the one the table is most likely to have missed.
# 2>/dev/null || true so a missing range path and a no-match result both yield
# "nothing found" rather than a non-zero exit under set -e.
grep -rln "{basename without .md}\|{rule or step IDs it defines}" \
  .claude/ exec-plans/active/ docs/ *.md 2>/dev/null || true
# then cat each hit that is not this document itself

# Diff, if the document was just changed — it scopes the lap to what actually changed.
# Omit for a document being reviewed before any edit; §2c says what to do in that case.
git diff main...HEAD -- {target document path} 2>/dev/null
```

**If related files are not found**, proceed with what is available and note the absence in the review prompt.

### Step 3: Launch independent agent

Use the `Agent` tool to spawn a **subagent with no session context**.

Construct the prompt as follows (substitute `{…}` placeholders with actual content):

```
You are a document reviewer with no prior context about this document's authoring.
Review the following document from a DocDD (Document-Driven Development) perspective.

## Document type
{User Story / E2E scenario / Application spec / Design document / Exec-plan / Implementation document / Decision record (ADR) / Research note / General document}

## Document to review
{full content of target document}

## Related context
### AC readiness criteria (single source — apply these verbatim in §2)
{full content of .claude/skills/create-exec-plan/ac-readiness.md, or "not available"}

### Process walkthrough laps (single source — apply these in §2c; include only for a process document)
{full content of .claude/skills/create-exec-plan/process-walkthrough.md, or "not applicable"}

### Referrers — the sites that consume this document's rule (needed for §2c dependency backflow)
{the annotated path list: for each hit, its path and whether it appears in the document's own
 call-site table. Paste full content for any the reviewer would otherwise be unable to open.
 Or "none — nothing outside this document names it" / "not applicable — this document states no
 rule others consume".
 That lap cannot be performed on the document alone: judging whether a consuming site has what the
 rule requires means reading that site from the top of its own skill.}

### Diff (if this document was just changed)
{output of: git diff main...HEAD -- {target}, or "none — reviewing the document as it stands"}

### constraints.md (if applicable)
{content, or "not available"}

### Recorded basis (needed for §6 — for a US, spec, scenario, ADR or research note)
{the ADR format (.claude/skills/init-project/adr-format.md); the research-note format
 (.claude/skills/init-project/research-note-format.md); docs/00_project/decisions.md; and each
 in-repo file the document's ## 関連 names, with its content — or "{path}: not found".
 Or "not applicable — {document type}"}

### Related User Story or exec-plan (if applicable)
{content, or "not available"}

### AC sources (the US bullets / spec sections the plan's ## Sources names — needed to apply R2)
{for each row: the AC-ID, the section path, and the section text.
 Or "the plan has no ## Sources table — judge R2 on the AC lines alone and say so"
 / "{AC-ID}: cannot be opened — {path § section as written}: report it; R2 for this AC is NOT READY,
 not judged on the line alone"
 / "{AC-ID}: names background material, not a source — {path § section as written}: report it; R2
 for this AC is NOT READY, not judged on the line alone or on the background text" }

### Project documentation rules (CLAUDE.md excerpt)
{relevant sections covering doc rules, diagram rules, etc.}

## Review criteria

### 1. DocDD structural compliance
- Does the frontmatter include the required fields (`status:`, `tracks:`, `ac_ids:` as applicable)?
- Is `status:` appropriate for the document's actual state?
- For US files: is `ac_ids:` present and consistent with the ACs defined in the document body?
- Are there any forward references — links against DOC-INV-001's layer table in
  `check-doc-invariants` (a requirements doc linking to design/implementation; a `docs/00_project/`
  doc linking to any lower layer; an E2E scenario linking beyond the spec)?
- For a research note: are `collected:`, `references:` and `recheck_by:` (a date, or `n/a（理由）`)
  present (`.claude/skills/init-project/research-note-format.md`「Frontmatter」)? A missing
  `recheck_by` is a suggestion, not a defect — the `gc` backstop still finds the note.

### 2. Acceptance criteria quality (for User Stories and exec-plans)

Judge each AC with the **five readiness checks supplied above** (R1 単一の観測可能な結果 / R2
given-when-then / R3 成功指標が具体 / R4 E2E ステップへのアンカー / R5 what であって how でない),
including the verdict rule (NOT READY when R1 / R2 / R5 fails). Use those checks as written —
do not substitute your own notion of a "good" AC, and name the failing check by ID in your findings.

`create-exec-plan`, `start-feature` and `run-exec-plan` apply the same file at their own gates, so a
verdict here should match theirs. For that to hold, judge **R2 against the AC line together with the
sources supplied above** — the other three gates do, and judging a one-liner in isolation would
manufacture NOT READY verdicts they will never reproduce. If the sources were not available, say so
in the finding rather than failing R2 for detail you were not shown. That is not the same as a row
marked **cannot be opened** above: "not available" means the caller did not hand you the material;
"cannot be opened" means the row itself is a broken pointer — that AC is NOT READY. A row marked
**names background material** is NOT READY for the same reason: the material may explain the AC, but
a test may not be drafted from it (`ac-sources.md`「What counts as a source」).
This review is **advisory**: report the verdict, change nothing.

Then, beyond readiness:
- Are happy-path, error-case, and boundary conditions covered across the AC set?
- Are any ACs overlapping or contradictory with each other?

### 2b. Goal image and E2E coverage

Requirements state obligations; they do not state what the finished thing is. Check that the layer
which does is present and sharp — a document can pass every criterion above and still describe
something nobody wanted.

**For User Stories** — the `## ゴール像` section:
- Is it present at all? (required — see `create-requirements`)
- 完成時にできること: does it say what the *user can do*, or does it just restate the feature name?
- 主要ユーザージャーニー: is it a through-flow (Mermaid), or a list of disconnected capabilities?
- 非ゴール: is it stated, and does it actually exclude something a reader might otherwise assume?

**For application specs and E2E scenarios** — the scenarios in `docs/01-02_e2e/` (one file per
`E2E-NNN`; a project not yet migrated has them as the spec's `## E2E シナリオ` section — report that
as a migration candidate, see DOC-INV-006 in `check-doc-invariants`):
- Is there at least one scenario, each carrying a `# E2E-NNN:` heading, 前提 / 完了条件 / 満たす AC?
- Is each 完了条件 an observable end state, not a restatement of the steps?
- Do the scenarios' `満たす AC` lines together cover every AC? Flag any AC belonging to no scenario
  — it means either the goal image is missing a path or the AC is not needed for the finished thing.
- Does each scenario carry `由来ジャーニー` (the US whose journey it realizes) and `満たす業務要求`
  (its outer anchor in `docs/00_project/`, or `n/a（理由）`), and do they point at something that
  exists? Is every US the spec covers named by some scenario's `由来ジャーニー`? (DOC-INV-006
  「Upward trace」)
- **The other direction — does any scenario say more than the requirements?** Compare each
  scenario's 前提, steps and 完了条件 against its comparison set
  (`.claude/skills/create-spec/e2e-interaction.md` — with no plan, its #2 and #3, and for a scenario
  with no `由来ジャーニー` the advisory-site fallback that file defines in「Where this is applied」;
  a set that still cannot be assembled is reported as such, not compared on what is left). Report an outcome
  stated nowhere in the set as a **requirements gap** and a disagreement as a **contradiction**, each
  for the human to decide (① promote / ② drop / ③ rework, or which side is right). This is an
  advisory site (「Where this is applied」): report it, do not edit the scenario or the US to agree,
  and do not treat a refinement as a finding.

**For exec-plans** — the `[E2E]` acceptance criterion:
- Does the plan have one, and is it traced to an `E2E-NNN` (or to the US goal image)?
- If the plan is a refactoring plan, does the E2E AC state *behavior preservation* rather than new
  behavior?
- If the plan has none, is it genuinely documentation-only? (`create-exec-plan` exempts only that
  case, and asks for `E2E: n/a (documentation-only)` in the Decision Log.)
- The converse is also a finding: a **documentation-only plan that carries an `[E2E]` AC**. Such a
  plan cannot be completed — `run-tests` / `pre-pr` / `complete-exec-plan` all hold on an `[E2E]` AC
  with no passing test, and a documentation change has no test to give them. Flag it and suggest
  restating the criterion as an ordinary functional AC with an observable result.

### 2c. Process documents: does it survive its laps?

Applies when the document under review **describes a process** — a loop, a resumable run, a stop
condition, a gate, an exemption, **or a rule that other documents consume** (a single source with
call sites, including a step or ID that others point at). The last clause matters: a rule document
has no loop of its own, and skipping this section for it would skip the dependency-backflow lap
exactly where it applies. Scope table in
`.claude/skills/create-exec-plan/process-walkthrough.md`. For ordinary requirement or spec
documents, skip this section.

Do not check only that the steps read consistently. Walk the process and name the state after each
step, at least for these laps:

- **second iteration** — the state the first pass leaves behind is the next pass's input;
- **resume** — a fresh session starting from the files alone, mid-process;
- **exemption** — the `n/a` path, and whether every downstream gate knows about it;
- **dependency backflow** — if this document states a rule other documents consume, walk the sites
  that consume it, using the referrer list supplied above. For each, ask whether the material this
  document now requires is in hand *at the point that site runs* — not whether the site's wording
  still matches. A site can be textually correct and still be judging with what it does not have.
  Report a referrer that the list contains but the document's own call-site table omits.

  **Scope note.** Unlike `docode-review`, this review may run with no diff — a document reviewed
  before anything changed. When a diff was supplied, scope the lap to what it altered. When none
  was, you cannot know which requirement is *new*, so ask the question in its standing form: does
  each consumer have what this document requires of it today? Say which of the two you performed.

Report a finding when a state is unreachable or inescapable, when two rules answer the same state
differently, when a gate fires on the state that means success, when the process's own output
violates its own entry condition, or when a consumer decides without the material it now needs.
Advisory, like the rest of this review.

### 3. Clarity and completeness
- For User Stories: is the "As a / I want / So that" structure clear?
  Is the "So that" (the why) meaningful and not circular?
- Are there ambiguous terms that different readers could interpret differently?
- Is there missing information that an implementer would need to proceed?

### 4. Cross-reference integrity
- Do all Markdown links point to files that exist (based on path plausibility)?
- Are constraint IDs (TC-001 etc.) referenced correctly and consistently with constraints.md?
- Are AC-IDs consistent between the US body, `ac_ids:` frontmatter, and any exec-plan?

### 5. Diagram rules compliance (CLAUDE.md)
- Are flow / sequence / class diagrams written in Mermaid?
- Does each ASCII art figure have a plain-text explanation immediately following it?

### 6. Decision basis — a conclusion with no recorded basis

Applies to User Stories, application specs, E2E scenarios, ADRs and research notes. Skip it for
exec-plans (their Decision Log is the record of their own decisions) and for design and implementation
documents.

A document can state a decision clearly and still leave a later reader unable to tell why — and so
unable to tell whether a fix is a correction of the current target or the next thing to build
(CLAUDE.md「変更のルーティング」), or whether an option being proposed was already rejected. Judge
with the ADR format and the recorded basis supplied above:

- **US / spec / scenario.** Find the statements that are *decisions* rather than restatements — the
  ADR format's「When a decision is an ADR candidate」 condition 1: a choice where another option was
  evident, a narrowing (a non-goal, a constraint, a removed behavior), a threshold value. For each, is
  its basis recorded anywhere — the document's `## 関連`, an ADR in `decisions.md`, a research note?
  Report one with none as **結論はあるが根拠が無い**, and suggest the entry that fits: `## 関連` (for a
  US, `create-requirements` Q6; for a spec, `create-spec` Step 2b) or an ADR (the ADR format). A
  scenario has no `## 関連`: its `満たす業務要求` is its recorded basis, and for a decision beyond it
  suggest an ADR or the spec's `## 関連`. Do not ask for a basis for every sentence — a restatement of
  a requirement needs none.
- **ADR.** Does each ADR carry what the ADR format requires — above all 検討した代替案と却下理由 (a
  table, or `なし（理由）`) and a 根拠資料 that is not blank? An ADR with no 種別 or no 却下理由 section is
  reported as a suggestion to fill when it is next touched, not as a defect.
- **Research note.** If it was the material for a choice, does it record the options and the one
  rejected, with why? Has it been changed beyond what `research-note-format.md`「Rechecking」 lists as
  the permitted changes — an observation edited in place rather than a new note written?
- **A `## 関連` pointing at a `status: deprecated` research note** with no `- 影響` line on that note
  recording this document as `維持` or `変更` (the same condition as `research-note-format.md`「The
  `gc` backstop」 step 6) — the document may rest on an observation that no longer holds. Report it so
  the human can check the premise; it is not a defect in the document by itself. Once the human has
  recorded the outcome, it is not a finding.
- **A basis that points at nothing** — a `## 関連` or 根拠資料 entry naming a file that does not exist,
  or a ヒアリング with no date or person — is a finding: a basis nobody can find is not recorded.

The basis is background, never a source: do not suggest naming it in a plan's `## Sources`, and do not
fail an AC's readiness (§2) for a missing rationale. Severity here is 🟡 Medium at most, so this section
alone never produces ❌ — it is advisory, like the rest of this review.

## Output format

=== Document Review Results ===

Reviewed by: Independent Agent (no authoring context)
Document: {path}
Type: {document type}

### Structural compliance
{For each frontmatter check: ✅ Present / ❌ Missing / N/A}

### AC quality (if applicable) — readiness verdicts
| AC | Verdict | Failing checks | Notes |
|----|---------|----------------|-------|
| AC-001 | READY | — | — |
| AC-002 | ⚠️ | R3 | Vague threshold: "performs well" — specify a measurable value |
| AC-003 | NOT READY | R2, R5 | 期待結果が「適切に」しか書かれていない／実装手段を指定している |

### Goal image / E2E coverage
{For US: ゴール像 present? 完成時にできること / 主要ユーザージャーニー / 非ゴール each ✅ / ⚠️ / ❌}
{For spec / scenario: scenarios present (and in docs/01-02_e2e/, or ⚠️ old layout)? Any AC belonging to no E2E-NNN?}
{For spec / scenario: 由来ジャーニー / 満たす業務要求 present and resolvable? Any US realized by no scenario?}
{For spec / scenario: symmetric comparison — 要件の穴 / 矛盾 per scenario, each for the human to decide; or "none"}
{For exec-plan: [E2E] AC present and traced? / ⚠️ documentation-only, exempt}

### Decision basis (US / spec / scenario / ADR / research note — omit otherwise)
{結論はあるが根拠が無い: <statement> (<section>) — suggested entry: ## 関連 / ADR; or "none"}
{For an ADR: required sections per the ADR format ✅ / ⚠️ <ADR-NNN: missing 検討した代替案と却下理由>}
{Basis entries that point at nothing: <entry>; or "none"}

### Process walkthrough (process documents only — omit otherwise)
{Second iteration: ✅ / ❌ <state where it breaks>}
{Resume from files alone: ✅ / ❌ <entry check that rejects the left-behind state>}
{Exemption path: ✅ / ❌ <downstream gate unaware of the exemption>}
{Dependency backflow: referrers examined <list them> — ✅ / ❌ <site that judges without the
 material the rule now requires> / N/A <this document states no rule others consume>}

### Findings

| # | Severity | Section / Line | Issue | Suggestion |
|---|----------|---------------|-------|------------|
| 1 | 🔴 Critical | ... | ... | ... |
| 2 | 🟠 High    | ... | ... | ... |
| 3 | 🟡 Medium  | ... | ... | ... |
| 4 | 🔵 Low     | ... | ... | ... |

### Summary
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

### Verdict
✅ Approved — document is ready for the next step
⚠️ Approved with suggestions — address medium/low items at your discretion
❌ Revision needed — fix critical/high issues before proceeding

Report the review result only. Do not modify any files.
```

**Important**: The spawned agent must NOT make any edits or commits. It only reports findings.

### Step 4: Present findings

After the independent agent returns its report, present it verbatim and guide next steps:

| Verdict | Recommended action |
|---------|--------------------|
| ✅ Approved | For US: proceed to `/create-spec`. For a spec: approve it, then `/create-exec-plan`. For exec-plan: proceed to `/start-feature` |
| ⚠️ Approved with suggestions | Discuss items with user, then proceed |
| ❌ Revision needed | Fix critical/high issues, then re-run `/doc-review` |

---

## Result report format

```
=== Document Review — Independent Agent ===

{full report from the spawned agent}

---
Next step:
  ✅ Approved         → /create-exec-plan (for US) or /start-feature (for exec-plan)
  ⚠️ With suggestions → Discuss findings above, then proceed
  ❌ Revision needed  → Fix issues above, then re-run /doc-review
```

---

## Completion criteria

- [ ] Target document identified
- [ ] Related context collected (or absence noted)
- [ ] Independent agent spawned via `Agent` tool
- [ ] Agent report presented to the user verbatim
- [ ] Next step communicated based on the verdict
