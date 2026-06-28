---
name: create-design
description: |
  Drafts design-spec documents under docs/02_design/ from approved requirements
  (docs/01_requirements/). Bridges the gap between "what to build" (requirements, layer 1)
  and "how it is structured" (design, layer 2), before an implementation plan is made.
  Output is always a draft for human review (/doc-review) and approval — it never decides
  requirements and never auto-approves. After approval, hands off to /create-exec-plan.
disable-model-invocation: true
---

# Skill: Create Design Spec

> **When to run**: After requirements exist (`docs/01_requirements/`) and before creating an
> implementation plan. This fills the previously-missing step between `/create-requirements`
> and `/create-exec-plan`.
>
> **Purpose**: Turn approved requirements (the *what*) into a structured design spec (the *how*:
> architecture, data model, API, UI flows) so that the implementation plan is built on an
> agreed design rather than improvised during coding. This is the DocDD-appropriate home for
> "Planner"-style spec drafting: it automates the **authoring** of the design, while the
> **decision** of what to build and the **approval** of the design stay with the human.
>
> **Prerequisites**:
> - `docs/01_requirements/` must contain the requirements this design is for
>   (User Story file(s) and/or `constraints.md`)
> - `docs/02_design/` must exist (created by `/init-project`)

---

## Design principle (read first)

This skill drafts; it does not decide or approve.

| Action | Who |
|--------|-----|
| Decide *what to build* (requirements, scope, product direction) | **Human** — already done in `docs/01_requirements/`; this skill must not invent or change it |
| Draft the *design spec* from approved requirements | **This skill** (automated authoring) |
| Review the draft independently | `/doc-review` (independent agent) |
| **Approve / freeze** the design | **Human** (merge = freeze; see CLAUDE.md spec-version management) |

The output is always `status: draft`. The skill never marks a design `active`, never merges,
and never proceeds to implementation planning on its own.

---

## What this skill does

1. Locate and read the approved requirements in `docs/01_requirements/`
2. If requirements are missing or too ambiguous to design against, **halt** and direct the
   user to `/create-requirements` (do not guess intent)
3. Draft the design-spec documents under `docs/02_design/` (scope/structure first)
4. Cross-reference each design back to the US/AC it satisfies (upward reference, layer 2 → 1)
5. Suggest `/doc-review` for an independent check, then human approval, then `/create-exec-plan`

---

## Steps

### Step 1: Read the requirements

- List `docs/01_requirements/user_stories/US-*.md` and read the relevant US file(s) and
  `docs/01_requirements/constraints.md`.
- Identify the User Story, its `ac_ids:`, the acceptance conditions, and any constraints
  (TC/BC/PF/SC) that shape the design.

**If no requirements exist, or they are too vague to design against** (e.g., no concrete AC):
**halt** and report:

```
設計の起点となる要件が docs/01_requirements/ にありません（または曖昧です）。
先に /create-requirements で User Story と受け入れ条件（AC）を定義してください。
```

Deciding *what to build* is the human's call — never invent requirements to fill the gap.

### Step 2: Decide which design documents are needed

Following `init-project`'s structure, draft only the documents the feature actually needs:

| File | When to draft |
|------|---------------|
| `docs/02_design/architecture.md` | Always — component/layer structure and boundaries |
| `docs/02_design/data_model.md` | When the feature persists or models data |
| `docs/02_design/api_spec.md` | When the feature exposes or consumes an API |
| `docs/02_design/ui_flows.md` | When the feature has a UI |

If a file already exists, **extend** it (append the new feature's design) rather than
overwriting prior design.

### Step 3: Draft the design (scope-over-detail)

Draft structure and boundaries first; defer granular detail to implementation.

- **architecture.md**: which components/layers, their responsibilities, and how they interact.
  Prefer a Mermaid diagram (flow/sequence/class) per CLAUDE.md diagram rules; if using ASCII
  art, always follow it with a plain-text explanation.
- **data_model.md / api_spec.md / ui_flows.md**: only the shape needed to plan implementation
  (entities and key fields; endpoints and contracts; screen flow) — not exhaustive detail.
- For each design element, note the **US/AC it satisfies** (e.g., "satisfies AC-002") so the
  downstream exec-plan can trace AC → design → code (keeps DOC-INV-004 traceability intact).

Each drafted file gets frontmatter:

```yaml
---
status: draft
tracks:
  - src/**/<relevant path pattern, or placeholder if unknown>
---
```

`status: draft` is mandatory — this design is not yet approved.

### Step 4: Hand off for review and approval

Do **not** approve, mark `active`, or proceed to planning. Instead report the drafts and the
required human gate (see report format below): independent review → human approval (freeze) →
implementation planning.

---

## Layer / reference rule

The design (layer 2) may reference requirements (layer 1) — this is a valid upward reference
(DOC-INV-001). The design must **not** be referenced *by* requirements, and must not pull in
layer-3 implementation detail. Keep links pointing up the abstraction ladder.

---

## Completion criteria

- [ ] Requirements in `docs/01_requirements/` were read (or the skill halted and directed to
      `/create-requirements`)
- [ ] At least `docs/02_design/architecture.md` was drafted (plus conditional docs as needed)
- [ ] Every drafted file has `status: draft` frontmatter
- [ ] Each design element references the US/AC it satisfies
- [ ] The design was NOT approved/marked active and did NOT proceed to planning automatically
- [ ] Independent review + human approval + next step were communicated

Final report output by the agent:

```
=== Design spec drafted (DRAFT — not yet approved) ===

From requirements : docs/01_requirements/user_stories/US-XXX_{name}.md
Drafted designs   : docs/02_design/architecture.md
                    {+ data_model.md / api_spec.md / ui_flows.md as applicable}
AC coverage       : AC-001 → {design element} | AC-002 → {design element} | ...

Next steps (human-gated):
  1. Review  : run /doc-review for an independent check of the design
  2. Approve : edit as needed, then approve/freeze (merge — see spec-version management)
  3. Plan    : run /create-exec-plan to turn the approved design + ACs into a plan
```
