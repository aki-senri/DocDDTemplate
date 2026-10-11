---
name: create-spec
description: |
  Drafts an independent application spec document under docs/02_spec/ from approved requirements
  (docs/01_requirements/), together with the required end-to-end scenarios — one file per scenario
  under docs/01-02_e2e/ (E2E-NNN, traced across the ACs they need). The spec describes WHAT the app
  does — purpose, features, behavior, scope and non-goals — NOT how it is built (no architecture,
  data model, or API internals; that is technical design). Output is always a draft for human review
  (/doc-review) and approval — it never decides requirements and never auto-approves. After
  approval, hands off to /create-exec-plan.
disable-model-invocation: true
---

# Skill: Create Application Spec

> **When to run**: After requirements exist (`docs/01_requirements/`) and before creating an
> implementation plan, when you want a consolidated application spec ("what the app is and
> does") before planning the work.
>
> **Purpose**: Turn approved requirements into a single, coherent **application spec** (the
> product/functional specification) so that humans and AI share one picture of the app before
> implementation planning. This is the DocDD-appropriate home for "Planner"-style spec
> drafting: it automates the **authoring** of the spec, while the **decision** of what to build
> and the **approval** of the spec stay with the human. It writes the *what*, never the
> technical *how* (architecture/data model/API internals belong to design, not here).
>
> **Prerequisites**:
> - `docs/01_requirements/` must contain the requirements this spec is for
>   (User Story file(s) and/or `constraints.md`)

---

## Design principle (read first)

This skill drafts the *what*; it does not decide, approve, or design the *how*.

| Action | Who / Where |
|--------|-------------|
| Decide *what to build* (requirements, scope, product direction) | **Human** — already in `docs/01_requirements/`; this skill must not invent or change it |
| Draft the *application spec* (consolidated what/behavior) and its E2E scenarios from approved requirements | **This skill** (automated authoring) → `docs/02_spec/` and `docs/01-02_e2e/` |
| Review the draft independently | `/doc-review` |
| **Approve** the spec and its scenarios | **Human** (merge to `main` = approval; see CLAUDE.md spec-version management). Approval is per document; it is not the per-plan **freeze** of a scenario, which happens later, when a plan names it (`e2e-interaction.md`) |
| Technical *how* (architecture, data model, API) | **Out of scope** — that is design, not this spec |

The output is always `status: draft`. The skill never marks a spec `active`, never merges,
and never proceeds to implementation planning on its own.

---

## What this skill does

1. Locate and read the approved requirements in `docs/01_requirements/`
2. If requirements are missing, not yet approved (`status: draft`), or too ambiguous to
   specify against, **halt** and direct the user to approve/define them first (do not guess
   intent)
3. Draft the application spec under `docs/02_spec/` (whole-app scope/structure first), and the
   required E2E scenarios derived from the US goal image — one file each under `docs/01-02_e2e/`
4. Trace each spec feature back to the US/AC it satisfies, and each E2E scenario across the set
   of ACs it needs (`E2E-001 → AC-001, AC-003`)
5. Suggest `/doc-review` for an independent check, then human approval, then `/create-exec-plan`

---

## Steps

### Step 1: Read the requirements

- List `docs/01_requirements/user_stories/US-*.md` and read the relevant US file(s) and
  `docs/01_requirements/constraints.md`.
- Identify the user stories, their `ac_ids:`, acceptance conditions, and constraints
  (TC/BC/PF/SC) that shape what the app must do.
- **Read the `## ゴール像` section of each source US file.** Its 完成時にできること,
  主要ユーザージャーニー, and 非ゴール are the input for the E2E scenarios (`docs/01-02_e2e/`)
  (required) and for Scope & non-goals. If a US file has no `## ゴール像` section — e.g. it was
  written before that section became required — **halt** and report:

  ```
  US-XXX に ## ゴール像 節がありません。
  E2E シナリオはゴール像の主要ユーザージャーニーから起こすため、これが無いと
  「通しで何ができるようになるか」を仕様側で作文することになります。
  先に /create-requirements の Q4（完成時にできること / 主要ユーザージャーニー / 非ゴール）を
  US-XXX に追記してください。
  ```

  Proceed only once the goal image exists (or the user explicitly confirms drafting without it,
  in which case record that choice in the report).
- **Confirm the requirements are approved before drafting from them.** Check the `status:`
  frontmatter of the relevant US file(s). The spec must be built on *approved* requirements,
  not on in-progress ones. If a US is still `status: draft` (i.e. not yet approved/frozen),
  **halt** and report so the human can approve the requirements first:

  ```
  この仕様の起点となる要件（US-XXX）が status: draft のままです。
  仕様は承認済み要件から起草します。先に要件をレビュー・承認（status: active 化／マージ）してください。
  ```

  Only proceed once the source requirements are approved (or the user explicitly confirms
  drafting from a draft requirement).

**If no requirements exist, or they are too vague to specify against**: **halt** and report:

```
仕様の起点となる要件が docs/01_requirements/ にありません（または曖昧です）。
先に /create-requirements で User Story と受け入れ条件（AC）を定義してください。
```

Deciding *what to build* is the human's call — never invent requirements to fill the gap.

### Step 2: Draft the application spec (scope-over-detail)

Write to `docs/02_spec/` — the spec layer (layer 2), sitting between requirements (layer 1)
and design (layer 3). For a single-app project use `docs/02_spec/app_spec.md`; split into
multiple files only if the spec grows large. If a spec file already exists, **extend** it
rather than overwriting.

Capture the **what**, in this order (scope and structure first, granular detail last):

| Section | Content |
|---------|---------|
| Purpose / overview | What the app is and the problem it solves (1–2 paragraphs) |
| Scope & non-goals | What is in scope; explicitly what is NOT (prevents scope creep) |
| Features | The feature set, each as a short capability statement |
| Behavior | How the app behaves for the key flows (rules, states, edge behavior) |

The end-to-end scenarios are **not** a section of the spec: each is its own file under
`docs/01-02_e2e/` — see below. They are never omitted.

Do **not** include technical design: no architecture, layering, data models, or API
internals. Those belong to design (`docs/03_design/`), a separate later step if needed.

For each feature **and each behavior section**, note the **US/AC it satisfies** (e.g.,
"satisfies AC-002") so the downstream exec-plan can trace AC → spec → code (keeps AC traceability
intact). The marker is what lets a plan's `## Sources` row name the section as the AC's source; a
section that describes an AC's behavior without saying so is easy to miss and easy to mistake for
background (`../create-exec-plan/ac-sources.md`「What counts as a source」).

#### The E2E scenarios (required) — `docs/01-02_e2e/`

Features are fragments; a spec made only of fragments can satisfy every AC and still not work
when used end to end. The scenarios are what keep the *whole* in view, and each is the source the
exec-plan's `[E2E]` acceptance criterion is written against. **They are never `(if applicable)`
and never omitted.**

Derive the scenarios from the `## ゴール像` section of the source US file — specifically its
主要ユーザージャーニー. One scenario per distinct end-to-end path (a normal path at minimum;
add key alternate/failure paths where the goal image calls for them).

**One scenario, one file**: `docs/01-02_e2e/E2E-NNN_{slug}.md`. `E2E-NNN` is unique across the
project — take the next free number, never reuse one. While a spec still has old-layout scenarios,
count those too: the next free number is above every ID in either layout. A file per scenario is
what lets a scenario be approved, routed (CLAUDE.md「変更のルーティング」) and frozen by a plan on its
own, rather than as a paragraph of a larger spec file. Write each as:

```markdown
---
status: draft
---

# E2E-001: {scenario name}

{Mermaid flowchart or sequence diagram of the through-flow, per CLAUDE.md diagram rules}

{One-line plain-text summary of what the user accomplishes in this scenario.}

- 前提: {starting state}
- 完了条件: {observable end state — what is true when the scenario has succeeded}
- 満たす AC: AC-001, AC-003, AC-005
```

**Why the scenarios live outside the spec.** The directory name is a range, `01-02`: a scenario
stands in a two-way relationship with both the requirements (layer 1) and the spec (layer 2), and a
single layer number would rank it above one and below the other. The reference-direction rule for a
range is DOC-INV-001 in `../check-doc-invariants/SKILL.md`; when a scenario may correct the US or
the spec — and when that stops — is [`e2e-interaction.md`](e2e-interaction.md).

**Cross-cutting traceability.** `満たす AC` is the point of a scenario: feature-level traceability
runs *downward* (feature → satisfies AC-002), which cannot express "these several ACs together must
add up to one working flow." The `E2E-NNN → AC-xxx, AC-yyy` mapping runs *across* the ACs and is
what lets `run-tests` and `pre-pr` check E2E coverage rather than only per-AC coverage. Each
scenario file's `満たす AC` line is the **only** place the mapping is written; the at-a-glance table
goes in this skill's report, not into the spec, where a second copy would drift from the files.

Every AC defined in the source requirements should appear in at least one E2E scenario. If an AC
belongs to no scenario, say so explicitly in the report — it usually means either the goal image
is missing a path, or the AC is not actually needed for the finished thing.

**A project whose spec still has a `## E2E シナリオ` section** (the earlier layout, which put the
scenarios inside `docs/02_spec/**`) keeps it valid for now — DOC-INV-006 reads both layouts and
reports the old one as a ⚠️ migration candidate. Do not add new scenarios there: draft them in
`docs/01-02_e2e/`. Moving the existing ones is the human's step, done as DOC-INV-006's fix hint
describes, because a moved scenario breaks every active plan's `## Sources` row that names it.

**A scenario is not frozen when this skill writes it — and approving it does not freeze it
either.** Approval (the human merging the draft to `main`) makes it the current target; the freeze
happens per plan, when an exec-plan that names the scenario in its `## Sources` is finalized. Until a
plan freezes it, the scenario, the US and the spec may each be corrected to match the others —
drafting a scenario is often how a gap in the requirements is found — though an edit to an approved
document still goes through CLAUDE.md「変更のルーティング」. Report such a gap (the
`Requirements gaps` line of the report) rather than writing it into the scenario as if it were
decided: the freeze point and the complement-detection rule are in
[`e2e-interaction.md`](e2e-interaction.md).

Each drafted file gets frontmatter:

```yaml
---
status: draft
---
```

`status: draft` is mandatory — this spec, and each scenario file, is not yet approved.

### Step 3: Hand off for review and approval

Do **not** approve, mark `active`, or proceed to planning. Report the draft and the required
human gate (see report format): independent review → human approval → planning.

---

## Layer / reference rule

`docs/02_spec/` is the spec layer (layer 2). It may reference requirements
(`docs/01_requirements/`) and the E2E scenarios (`docs/01-02_e2e/`). The scenarios are a range
layer spanning 1 and 2: they may reference the US and the spec, and both may reference them
(DOC-INV-001 in `../check-doc-invariants/SKILL.md`). Neither may pull in technical design detail
(that is `docs/03_design/`, layer 3) or implementation detail — keep the spec and the scenarios
about *what*, not *how*.

---

## Completion criteria

- [ ] Requirements in `docs/01_requirements/` were read and confirmed approved (not
      `status: draft`) — or the skill halted and directed to approve/define them first
- [ ] The `## ゴール像` section of each source US was read (or the skill halted because it was
      missing)
- [ ] An application spec was drafted under `docs/02_spec/` covering purpose, scope/non-goals,
      features, and behavior — with no **new** scenario added to a `## E2E シナリオ` section. An
      existing old-layout section is left in place (moving it is the human's step) and named in
      the report as a migration candidate
- [ ] At least one scenario exists for the spec, in either layout, and every scenario this run
      drafted is a file `docs/01-02_e2e/E2E-NNN_{slug}.md` carrying `status: draft`, a
      `# E2E-NNN:` heading, a Mermaid diagram, 前提, 完了条件, and 満たす AC
- [ ] The `E2E-NNN → AC-xxx` mapping is shown in the report, and any AC belonging to no scenario
      was reported
- [ ] The spec describes *what* the app does, with NO technical design (architecture/data
      model/API internals)
- [ ] Every drafted file — spec and scenarios — has `status: draft` frontmatter
- [ ] Each feature and behavior section references the US/AC it satisfies
- [ ] The spec was NOT approved/marked active and did NOT proceed to planning automatically
- [ ] Independent review + human approval + next step were communicated

Final report output by the agent:

```
=== Application spec drafted (DRAFT — not yet approved) ===

From requirements : docs/01_requirements/user_stories/US-XXX_{name}.md
Drafted spec      : docs/02_spec/app_spec.md
Drafted scenarios : docs/01-02_e2e/E2E-001_{slug}.md, docs/01-02_e2e/E2E-002_{slug}.md
Old-layout E2E    : {spec file § E2E シナリオ (E2E-NNN, …) — a migration candidate for the human; or "none"}
AC coverage       : AC-001 → {feature} | AC-002 → {feature} | ...
E2E シナリオ      : E2E-001 {name} → AC-001, AC-003 | E2E-002 {name} → AC-002, AC-004
AC not in any E2E : {AC list, or "none"}
Requirements gaps : {outcomes a scenario needed that the US does not state — for the human to promote, drop or rework; or "none"}

Next steps (human-gated):
  1. Review  : run /doc-review for an independent check of the spec
  2. Approve : edit as needed, then approve the spec and the scenarios (merge — see
               spec-version management). A scenario freezes later, per plan
  3. Plan    : run /create-exec-plan to turn the approved spec + ACs into a plan
               (the scenarios above become the plan's [E2E] acceptance criteria)
```
