---
name: create-spec
description: |
  Drafts an independent application spec document under docs/02_spec/ from approved requirements
  (docs/01_requirements/). The spec describes WHAT the app does — purpose, features, behavior,
  functional screen/UX flows, scope and non-goals — NOT how it is built (no architecture, data
  model, or API internals; that is technical design). Output is always a draft for human review
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
2. If requirements are missing or too ambiguous to specify against, **halt** and direct the
   user to `/create-requirements` (do not guess intent)
3. Draft the application spec under `docs/02_spec/` (whole-app scope/structure first)
4. Trace each spec feature back to the US/AC it satisfies
5. Suggest `/doc-review` for an independent check, then human approval, then `/create-exec-plan`

---

## Steps

### Step 1: Read the requirements

- List `docs/01_requirements/user_stories/US-*.md` and read the relevant US file(s) and
  `docs/01_requirements/constraints.md`.
- Identify the user stories, their `ac_ids:`, acceptance conditions, and constraints
  (TC/BC/PF/SC) that shape what the app must do.

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
| Screen / UX flows | Functional-level flows (Mermaid preferred per CLAUDE.md diagram rules; if ASCII art, always follow with a plain-text explanation) |

Do **not** include technical design: no architecture, layering, data models, or API
internals. Those belong to design (`docs/03_design/`), a separate later step if needed.

For each feature, note the **US/AC it satisfies** (e.g., "satisfies AC-002") so the
downstream exec-plan can trace AC → spec → code (keeps AC traceability intact).

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

- [ ] Requirements in `docs/01_requirements/` were read (or the skill halted and directed to
      `/create-requirements`)
- [ ] An application spec was drafted under `docs/02_spec/` covering purpose, scope/non-goals,
      features, behavior, and (if applicable) screen/UX flows
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

Next steps (human-gated):
  1. Review  : run /doc-review for an independent check of the spec
  2. Approve : edit as needed, then approve/freeze (merge — see spec-version management)
  3. Plan    : run /create-exec-plan to turn the approved spec + ACs into a plan
```
