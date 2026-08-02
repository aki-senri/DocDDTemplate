---
name: create-requirements
description: |
  Creates structured requirements documents for this project.
  Guides the user through defining User Stories, a required goal image (what the user can do
  when it is done, the primary end-to-end journey, and non-goals), acceptance conditions, and
  constraints, then generates the corresponding files under docs/01_requirements/.
  Bridges to create-exec-plan by providing ready-to-use AC material, and to create-spec by
  providing the journey that becomes the E2E scenarios.
disable-model-invocation: true
---

# Skill: Create Requirements

> **When to run**: Before starting feature planning, when you want to define what to build before writing code
>
> **Purpose**: Create structured requirements documents (User Stories + goal image + constraints)
> so that humans and AI agents share a common understanding of both "what the system must do"
> **and "what the finished thing is"**. Requirements alone state obligations; without a goal
> image, a downstream spec can satisfy every requirement and still be the wrong thing.
>
> **Prerequisites**: Phase 1 documents must exist (`docs/07_ai_context/CONTEXT.md`)

---

## What this skill does

1. Assigns a US number by checking existing User Story files
2. Conducts an interview to define the User Story and its **goal image** (required)
3. Generates `docs/01_requirements/user_stories/US-XXX_{name}.md`
4. Optionally updates `docs/01_requirements/constraints.md` with new constraints
5. Suggests running `/create-spec` to draft the application spec from these requirements
   (then `/create-exec-plan` after the spec is approved)

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

### Q1b. Feature title (human-readable)

> "Give this feature a short human-readable title. (e.g., `ユーザーログイン`, `CSV エクスポート`)"

→ Used as the document heading: `# US-XXX — {Q1b}`

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
→ These ACs serve as **source material** for `/create-exec-plan`.
  When creating an exec-plan, each AC heading is condensed into a single `- [ ] AC-XXX: <description>` line
  (the exec-plan format expected by `spec-gate.py`); the detailed bullet points stay in the US file.

---

### Q4. Goal image — the finished picture (**required**)

Requirements alone describe *what the system must do*; they do not pin down *what the finished
thing looks like when used end to end*. Without that, a spec can satisfy every AC and still be
the wrong thing. This question is the layer that fixes the goal, so it **cannot be skipped**.

Ask Q4a–Q4c one at a time. **All three are required.** Q4d is optional.

#### Q4a. What the user can do when it is done (1–3 sentences)

> "この機能が完成したとき、利用者は何をできるようになりますか？ 1〜3文で書いてください。"

→ Used for the `### 完成時にできること` subsection

#### Q4b. Primary user journey (the end-to-end flow)

> "その利用者が最初から最後まで通しで使うときの流れを教えてください。
> （例: フォルダを開く → ファイルを選ぶ → タグを付ける → 一覧で絞り込む）"

Express this as a **Mermaid diagram** per the project diagram rules (CLAUDE.md) — a flowchart or
sequence diagram is usually right for a journey. Follow it with a one-line plain-text summary of
the flow.

→ Used for the `### 主要ユーザージャーニー` subsection
→ This is the material `/create-spec` turns into E2E scenarios, and the reason a plan can carry
  an `[E2E]` acceptance criterion at all.

#### Q4c. Non-goals (what this feature will NOT do)

> "この機能で『作らないもの』を挙げてください。スコープ外を明示することで、後の仕様がここを
> 越えて広がるのを防ぎます。"

→ Used for the `### 非ゴール` subsection

#### Q4d. UI sketch (optional)

> "画面の大まかなスケッチはありますか？（Enter でスキップできます）"
>
> If yes: "Describe the layout. A rough sketch in words is fine."

When generating the UI sketch, follow the project diagram rules (CLAUDE.md):
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

→ Used for the `### UI スケッチ` subsection (omitted entirely if Q4d was skipped)

#### If the user cannot answer Q4a–Q4c

**Halt — do not invent a goal image and do not proceed with the section omitted.** Deciding what
the finished thing is remains the human's call (same principle as `/create-spec` halting on
missing requirements). Report:

```
ゴール像（完成イメージ）が未定のままです。
要件は満たすが意図と異なるものが出来上がるのを防ぐため、この節は省略できません。
- 完成時に利用者が何をできるようになるか
- 通しの利用フロー（主要ユーザージャーニー）
- 非ゴール（作らないもの）
上記が定まってから /create-requirements を再開してください。
```

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

# US-XXX — {Q1b: human-readable feature title}

## ユーザーストーリー

> **{Who}として、**
> {What}したい。
> **なぜなら、** {Why}から。

## ゴール像

### 完成時にできること

{Q4a: 1–3 sentences}

### 主要ユーザージャーニー

{Q4b: Mermaid diagram of the end-to-end flow, followed by a one-line plain-text summary}

### 非ゴール

- {Q4c: what this feature will NOT do}

### UI スケッチ

{Q4d content — omit this subsection entirely if Q4d was skipped}
{Use Mermaid when possible; if using AA, always follow it with a plain-text explanation}

## 受け入れ条件

### AC-001: {title}

- [ ] {condition}
- [ ] {condition}

### AC-002: {title}

- [ ] {condition}
- [ ] {condition}

## 関連

{Q6 content — omit if empty}
```

**Note on `ac_ids` frontmatter**: List all AC numbers defined in Q3.
**Note on `tracks`**: Leave as `src/**/<placeholder>` if the implementation path is not yet known.

---

## Steps

1. Run the pre-check to determine the next US number
2. Complete the Q1–Q6 interview (halt at Q4 if the goal image cannot be answered)
3. Apply the interview answers to the template and create the US file
4. If Q5 had answers, append the new constraint rows to `constraints.md`
5. Report completion and suggest next steps

---

## Completion criteria

- [ ] `docs/01_requirements/user_stories/US-XXX_{name}.md` has been created
- [ ] The file contains `status: draft`, `ac_ids`, a user story, and at least one AC
- [ ] The `## ゴール像` section is present and contains all three required parts:
      完成時にできること (Q4a) / 主要ユーザージャーニー (Q4b, Mermaid) / 非ゴール (Q4c)
- [ ] `constraints.md` updated if new constraints were defined in Q5

Final report output by the agent:

```
=== Requirements document created ===

File    : docs/01_requirements/user_stories/US-XXX_{name}.md
ACs     : AC-001, AC-002, ... (list all defined)
ゴール像 : {Q4a in one line} / ジャーニー {n} ステップ / 非ゴール {n} 件
Constraints added: {count} (or "none")

Next step: Run /create-spec to draft the application spec (docs/02_spec/) from these requirements.
  (Then, after the spec is reviewed and approved, run /create-exec-plan.)
  Suggested feature   : {Q1}
  ACs to spec for     : {AC list from Q3}
  ゴール像            : /create-spec turns 主要ユーザージャーニー into E2E scenarios

  Note: For a small change that needs no application spec, you may skip /create-spec and run
  /create-exec-plan directly.
```
