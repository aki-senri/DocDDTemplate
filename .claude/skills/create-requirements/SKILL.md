---
name: create-requirements
description: |
  Creates structured requirements documents for this project.
  Guides the user through defining User Stories, acceptance conditions, and constraints,
  then generates the corresponding files under docs/01_requirements/.
  Bridges to create-exec-plan by providing ready-to-use AC material.
disable-model-invocation: true
---

# Skill: Create Requirements

> **When to run**: Before starting feature planning, when you want to define what to build before writing code
>
> **Purpose**: Create structured requirements documents (User Stories + constraints) so that
> both humans and AI agents share a common understanding of "what the system must do."
>
> **Prerequisites**: Phase 1 documents must exist (`docs/06_ai_context/CONTEXT.md`)

---

## What this skill does

1. Assigns a US number by checking existing User Story files
2. Conducts an interview to define the User Story
3. Generates `docs/01_requirements/user_stories/US-XXX_{name}.md`
4. Optionally updates `docs/01_requirements/constraints.md` with new constraints
5. Suggests running `/create-exec-plan` using the ACs defined in the User Story

---

## Pre-check: US number assignment

Before the interview, check for existing files in `docs/01_requirements/user_stories/`:
- Find files whose names match the pattern `US-\d{3}_*.md` (e.g., `US-001_open_folder.md`)
- Ignore other files in that directory (e.g., `{platform}.md`, `common.md` created by `init-project`)
- Find the highest existing `US-NNN` number among matched files
- Assign the next number (e.g., if US-003 exists → assign US-004)
- If no matching files exist, start from US-001

Report to the user: `Next US number: US-XXX`

---

## Interview

Ask questions **one at a time, in order**.

---

### Q1. Feature name (slug)

> "What is the name of this feature? (alphanumeric and hyphens, e.g. `user-login`, `export-csv`)"

→ Used for the filename: `US-XXX_{Q1}.md`

---

### Q2. User Story (As a / I want / So that)

> "Let's define the User Story. Answer each of the following:"
>
> - **Who** is the user? (e.g., "a user who wants to organize files", "an administrator")
> - **What** do they want to do?
> - **Why** — what goal or benefit does this give them?

→ Used for the `## ユーザーストーリー` section

---

### Q3. Acceptance conditions

> "List the acceptance conditions that must be met for this User Story to be considered complete.
> Group related conditions under sub-headings (e.g., AC-001, AC-002).
> Each AC should have 2–5 checkable bullet points."

Example format to show the user:
```
AC-001: <title>
- [ ] <specific verifiable condition>
- [ ] <specific verifiable condition>

AC-002: <title>
- [ ] <specific verifiable condition>
```

→ Used for the `## 受け入れ条件` section
→ These ACs are later reused verbatim in `/create-exec-plan`

---

### Q4. UI sketch (optional)

> "Do you have a rough UI sketch for this feature? (You can skip this with Enter)"
>
> If yes: "Describe the layout. A rough sketch in words is fine."

When generating the UI sketch section, follow the project diagram rules (CLAUDE.md):
- If the layout can be expressed as a Mermaid diagram (e.g., state transitions, screen flow), **use Mermaid**.
- If Mermaid cannot represent it (e.g., 2D panel layout, table grid), use **ASCII art and always follow it with a plain-text explanation** of what the diagram shows and how it behaves.

Example of a valid AA + explanation block:

```
┌──────────┬──────────┐
│ ファイル名 │ タグ     │
└──────────┴──────────┘
```

上図はファイル一覧画面のレイアウト。左列にファイル名、右列に付与済みタグを表示する。
行を選択するとタグ編集パネルが右側にスライドインする。

→ Used for the `## UI スケッチ` section (omitted entirely if Q4 was skipped)

---

### Q5. New constraints (optional)

> "Does this feature introduce any new constraints?
> Examples: technical constraints (TC), business constraints (BC), performance requirements (PF), security constraints (SC).
> (You can skip this with Enter)"

If yes, collect:
- Constraint type: TC / BC / PF / SC
- ID (auto-assign next available ID per type by reading `constraints.md`)
- Constraint text

→ Appended to `docs/01_requirements/constraints.md`

---

### Q6. Related documents

> "Are there any related decisions or constraints to cross-reference?
> (e.g., `decisions.md: ADR-001`, `constraints.md: TC-003`)"

→ Used for the `## 関連` section

---

## Files to generate / update

| File | Action |
|------|--------|
| `docs/01_requirements/user_stories/US-XXX_{Q1}.md` | Create new |
| `docs/01_requirements/constraints.md` | Append new rows (only if Q5 has answers) |

---

## Template for `US-XXX_{name}.md`

```markdown
---
status: draft
ac_ids: [AC-001, AC-002]
tracks:
  - src/**/<relevant path pattern>
---

# US-XXX — {feature title from Q2}

## ユーザーストーリー

> **{Who}として、**
> {What}したい。
> **なぜなら、** {Why}から。

## 受け入れ条件

### AC-001: {title}

- [ ] {condition}
- [ ] {condition}

### AC-002: {title}

- [ ] {condition}
- [ ] {condition}

## UI スケッチ

{Q4 content — omit this section entirely if Q4 was skipped}
{Use Mermaid when possible; if using AA, always follow it with a plain-text explanation}

## 関連

{Q6 content — omit if empty}
```

**Note on `ac_ids` frontmatter**: List all AC numbers defined in Q3.
**Note on `tracks`**: Leave as `src/**/<placeholder>` if the implementation path is not yet known.

---

## Steps

1. Run the pre-check to determine the next US number
2. Complete the Q1–Q6 interview
3. Apply the interview answers to the template and create the US file
4. If Q5 had answers, append the new constraint rows to `constraints.md`
5. Report completion and suggest next steps

---

## Completion criteria

- [ ] `docs/01_requirements/user_stories/US-XXX_{name}.md` has been created
- [ ] The file contains `status: draft`, `ac_ids`, a user story, and at least one AC
- [ ] `constraints.md` updated if new constraints were defined in Q5

Final report output by the agent:

```
=== Requirements document created ===

File    : docs/01_requirements/user_stories/US-XXX_{name}.md
ACs     : AC-001, AC-002, ... (list all defined)
Constraints added: {count} (or "none")

Next step: Run /create-exec-plan to turn these ACs into an implementation plan.
  Suggested plan name : {Q1}
  Suggested ACs to use: {AC list from Q3}
```
