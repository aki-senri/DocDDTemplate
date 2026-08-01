---
name: create-spec
description: |
  Drafts an independent application spec document under docs/02_spec/ from approved requirements
  (docs/01_requirements/). The spec describes WHAT the app does — purpose, features, behavior,
  required end-to-end scenarios (E2E-NNN, traced across the ACs they need), scope and non-goals
  — NOT how it is built (no architecture, data model, or API internals; that is technical design). Output is always a draft for human review
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
| Draft the *application spec* (consolidated what/behavior) from approved requirements | **This skill** (automated authoring) → `docs/02_spec/` |
| Review the draft independently | `/doc-review` |
| **Approve / freeze** the spec | **Human** (merge = freeze; see CLAUDE.md spec-version management) |
| Technical *how* (architecture, data model, API) | **Out of scope** — that is design, not this spec |

The output is always `status: draft`. The skill never marks a spec `active`, never merges,
and never proceeds to implementation planning on its own.

---

## What this skill does

1. Locate and read the approved requirements in `docs/01_requirements/`
2. If requirements are missing, not yet approved (`status: draft`), or too ambiguous to
   specify against, **halt** and direct the user to approve/define them first (do not guess
   intent)
3. Draft the application spec under `docs/02_spec/` (whole-app scope/structure first), including
   a required `## E2E シナリオ` section derived from the US goal image
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
  主要ユーザージャーニー, and 非ゴール are the input for this spec's `## E2E シナリオ` section
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
| E2E シナリオ (**required**) | The end-to-end usage scenarios — see below. Never omitted |

Do **not** include technical design: no architecture, layering, data models, or API
internals. Those belong to design (`docs/03_design/`), a separate later step if needed.

For each feature, note the **US/AC it satisfies** (e.g., "satisfies AC-002") so the
downstream exec-plan can trace AC → spec → code (keeps AC traceability intact).

#### The `## E2E シナリオ` section (required)

Features are fragments; a spec made only of fragments can satisfy every AC and still not work
when used end to end. This section is what keeps the *whole* in the spec, and it is the source
the exec-plan's `[E2E]` acceptance criterion is written against. **It is never `(if applicable)`
and never omitted.**

Derive the scenarios from the `## ゴール像` section of the source US file — specifically its
主要ユーザージャーニー. One scenario per distinct end-to-end path (a normal path at minimum;
add key alternate/failure paths where the goal image calls for them).

Write each scenario as:

```markdown
### E2E-001: {scenario name}

{Mermaid flowchart or sequence diagram of the through-flow, per CLAUDE.md diagram rules}

{One-line plain-text summary of what the user accomplishes in this scenario.}

- 前提: {starting state}
- 完了条件: {observable end state — what is true when the scenario has succeeded}
- 満たす AC: AC-001, AC-003, AC-005
```

**Cross-cutting traceability.** `満たす AC` is the point of this section: feature-level
traceability runs *downward* (feature → satisfies AC-002), which cannot express "these several
ACs together must add up to one working flow." The `E2E-NNN → AC-xxx, AC-yyy` mapping runs
*across* the ACs and is what lets `run-tests` and `pre-pr` check E2E coverage rather than only
per-AC coverage.

Also record the mapping as a table so it can be read at a glance:

```markdown
| E2E | シナリオ | 満たす AC |
|-----|---------|----------|
| E2E-001 | {name} | AC-001, AC-003, AC-005 |
| E2E-002 | {name} | AC-002, AC-004 |
```

Every AC defined in the source requirements should appear in at least one E2E scenario. If an AC
belongs to no scenario, say so explicitly in the report — it usually means either the goal image
is missing a path, or the AC is not actually needed for the finished thing.

Each drafted file gets frontmatter:

```yaml
---
status: draft
---
```

`status: draft` is mandatory — this spec is not yet approved.

### Step 3: Hand off for review and approval

Do **not** approve, mark `active`, or proceed to planning. Report the draft and the required
human gate (see report format): independent review → human approval (freeze) → planning.

---

## Layer / reference rule

`docs/02_spec/` is the spec layer (layer 2). It may reference requirements
(`docs/01_requirements/`) as upward references. It must **not** pull in technical design
detail (that is `docs/03_design/`, layer 3) or implementation detail — keep the spec about
*what*, not *how*.

---

## Completion criteria

- [ ] Requirements in `docs/01_requirements/` were read and confirmed approved (not
      `status: draft`) — or the skill halted and directed to approve/define them first
- [ ] The `## ゴール像` section of each source US was read (or the skill halted because it was
      missing)
- [ ] An application spec was drafted under `docs/02_spec/` covering purpose, scope/non-goals,
      features, behavior, and E2E シナリオ
- [ ] The `## E2E シナリオ` section exists with at least one `E2E-NNN` scenario, each carrying a
      Mermaid diagram, 前提, 完了条件, and 満たす AC
- [ ] The `E2E-NNN → AC-xxx` cross-cutting traceability table is present, and any AC belonging to
      no scenario was reported
- [ ] The spec describes *what* the app does, with NO technical design (architecture/data
      model/API internals)
- [ ] Every drafted file has `status: draft` frontmatter
- [ ] Each feature references the US/AC it satisfies
- [ ] The spec was NOT approved/marked active and did NOT proceed to planning automatically
- [ ] Independent review + human approval + next step were communicated

Final report output by the agent:

```
=== Application spec drafted (DRAFT — not yet approved) ===

From requirements : docs/01_requirements/user_stories/US-XXX_{name}.md
Drafted spec      : docs/02_spec/app_spec.md
AC coverage       : AC-001 → {feature} | AC-002 → {feature} | ...
E2E シナリオ      : E2E-001 {name} → AC-001, AC-003 | E2E-002 {name} → AC-002, AC-004
AC not in any E2E : {AC list, or "none"}

Next steps (human-gated):
  1. Review  : run /doc-review for an independent check of the spec
  2. Approve : edit as needed, then approve/freeze (merge — see spec-version management)
  3. Plan    : run /create-exec-plan to turn the approved spec + ACs into a plan
               (the E2E シナリオ above become the plan's [E2E] acceptance criterion)
```
