---
name: doc-review
description: |
  Launches an independent agent (with no authoring context) to review a requirement
  or design document from a DocDD perspective.
  Checks AC testability (using the shared AC readiness criteria), completeness, ambiguity,
  and cross-reference integrity.
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
| `docs/02_spec/**/*.md` | Application spec |
| `docs/03_design/**/*.md` | Design document |
| `docs/04_implementation/**/*.md` | Implementation document |
| `exec-plans/**/*.md` | Exec-plan |
| Other `docs/**/*.md` | General document |

### Step 2: Load context

Collect content for the review prompt using the appropriate commands below.

```bash
# Target document (always)
cat {target document path}

# For User Story review: load constraints and any related exec-plan
cat docs/01_requirements/constraints.md 2>/dev/null || echo "not found"
grep -l "AC-" exec-plans/active/*.md 2>/dev/null | head -3 | xargs cat 2>/dev/null || echo "no active exec-plans"

# For exec-plan review: load the referenced US file(s)
# Extract US references from exec-plan frontmatter or body, then:
cat docs/01_requirements/user_stories/{referenced-US}.md 2>/dev/null || echo "not found"

# Project documentation rules
cat CLAUDE.md

# AC readiness criteria — the shared testability checks (always, when the document has ACs)
cat .claude/skills/create-exec-plan/ac-readiness.md

# Process walkthrough laps — only when the document describes a process
# (a loop, a resumable run, a stop condition, a gate, an exemption)
cat .claude/skills/create-exec-plan/process-walkthrough.md
```

**If related files are not found**, proceed with what is available and note the absence in the review prompt.

### Step 3: Launch independent agent

Use the `Agent` tool to spawn a **subagent with no session context**.

Construct the prompt as follows (substitute `{…}` placeholders with actual content):

```
You are a document reviewer with no prior context about this document's authoring.
Review the following document from a DocDD (Document-Driven Development) perspective.

## Document type
{User Story / Application spec / Design document / Exec-plan / Implementation document / General document}

## Document to review
{full content of target document}

## Related context
### AC readiness criteria (single source — apply these verbatim in §2)
{full content of .claude/skills/create-exec-plan/ac-readiness.md, or "not available"}

### Process walkthrough laps (single source — apply these in §2c; include only for a process document)
{full content of .claude/skills/create-exec-plan/process-walkthrough.md, or "not applicable"}

### constraints.md (if applicable)
{content, or "not available"}

### Related User Story or exec-plan (if applicable)
{content, or "not available"}

### Project documentation rules (CLAUDE.md excerpt)
{relevant sections covering doc rules, diagram rules, etc.}

## Review criteria

### 1. DocDD structural compliance
- Does the frontmatter include the required fields (`status:`, `tracks:`, `ac_ids:` as applicable)?
- Is `status:` appropriate for the document's actual state?
- For US files: is `ac_ids:` present and consistent with the ACs defined in the document body?
- Are there any forward references (requirements doc linking to design/implementation)?

### 2. Acceptance criteria quality (for User Stories and exec-plans)

Judge each AC with the **five readiness checks supplied above** (R1 単一の観測可能な結果 / R2
given-when-then / R3 成功指標が具体 / R4 E2E ステップへのアンカー / R5 what であって how でない),
including the verdict rule (NOT READY when R1 / R2 / R5 fails). Use those checks as written —
do not substitute your own notion of a "good" AC, and name the failing check by ID in your findings.

`create-exec-plan`, `start-feature` and `run-exec-plan` apply the same file at their own gates, so a
verdict here should match theirs. This review is **advisory**: report the verdict, change nothing.

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

**For application specs** — the `## E2E シナリオ` section:
- Is it present, with at least one `E2E-NNN` carrying 前提 / 完了条件 / 満たす AC?
- Is each 完了条件 an observable end state, not a restatement of the steps?
- Does the `E2E-NNN → AC-xxx` table cover every AC? Flag any AC belonging to no scenario — it means
  either the goal image is missing a path or the AC is not needed for the finished thing.

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

### 2c. Process documents: does it survive one lap?

Applies only when the document under review **describes a process** — a loop, a resumable run, a
stop condition, a gate, or an exemption (scope table in
`.claude/skills/create-exec-plan/process-walkthrough.md`). For ordinary requirement or spec
documents, skip this section.

Do not check only that the steps read consistently. Walk the process and name the state after each
step, at least for these laps:

- **second iteration** — the state the first pass leaves behind is the next pass's input;
- **resume** — a fresh session starting from the files alone, mid-process;
- **exemption** — the `n/a` path, and whether every downstream gate knows about it.

Report a finding when a state is unreachable or inescapable, when two rules answer the same state
differently, when a gate fires on the state that means success, or when the process's own output
violates its own entry condition. Advisory, like the rest of this review.

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
{For spec: E2E シナリオ present? Any AC belonging to no E2E-NNN?}
{For exec-plan: [E2E] AC present and traced? / ⚠️ documentation-only, exempt}

### Process walkthrough (process documents only — omit otherwise)
{Second iteration: ✅ / ❌ <state where it breaks>}
{Resume from files alone: ✅ / ❌ <entry check that rejects the left-behind state>}
{Exemption path: ✅ / ❌ <downstream gate unaware of the exemption>}

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
