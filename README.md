# DocDD Template

A starter template for **Document-Driven Development (DocDD)**.  
Combined with Claude Code, it creates an environment where AI agents can develop autonomously while reading living documentation.

> 日本語版: [README.ja.md](README.ja.md)

---

## What is DocDD?

A development methodology that places "living documentation" — always in sync with code — at the center, enabling AI agents to operate with the correct context throughout the entire development workflow.

```
Documents     = Definitions  (what to build)
Skills        = Operations   (how to proceed)
settings.json = Triggers     (when to run automatically)
```

- **CONTEXT.md** (≤50 lines) always acts as a navigation map showing "where we are now"
- `tracks:` fields define the correspondence between documents and code, automatically detecting drift
- A structured Phase 0–4 workflow manages everything consistently from requirements through operations

---

## Development Phases

| Phase | Description | Key outputs |
|-------|-------------|-------------|
| Phase 0 | Project initialization | CONTEXT.md, overview.md, decisions.md |
| Phase 1 | Knowledge base construction | invariants.md, patterns.md, architecture.md |
| Phase 2 | Requirements, spec & design | user_stories, app_spec.md, api_spec.md, data_model.md |
| Phase 3 | Implementation | Code + keeping documentation in sync |
| Phase 4 | Quality & operations | review_checklist.md, test_strategy.md |

---

## Quick Start

### 1. Copy the template

Copy this repository into your new project repository, or use it as a template.

```
.claude/                   ← keep as-is (skills and settings)
```

### 2. Initialize the project

Run the following in Claude Code:

```
/init-project
```

This collects project overview, tech stack, development rules, and platform via an interview, then auto-generates Phase 0 → Phase 1 documents.

### 3. Start implementing features

```
/create-requirements ← define User Stories / goal image / AC conditions (optional, recommended)
/create-spec         ← draft the application spec and E2E scenarios (optional; skip for small changes)
/create-exec-plan    ← create an execution plan (define AC-001~ and the [E2E] AC,
                       record each AC's sources, check AC readiness)
/start-feature       ← pre-implementation review, AC readiness re-check, branch creation
/run-exec-plan       ← autonomously implement ACs one by one: read the AC's sources,
                       test first, re-anchor to the spec on green (opt-in)
   (or manually: write the AC's test and confirm it fails → write code
    → /check-doc-freshness → /check-invariants → /run-tests)
/pre-pr              ← comprehensive pre-PR check
/complete-exec-plan  ← move plan to completed
```

> Only `create-exec-plan` onward is required for a minimal loop; `create-requirements` / `create-spec`
> are recommended when "what to build" is vague or shared across a team.

---

## Who does what (human vs AI)

DocDD splits responsibilities: **the human makes decisions, the AI does execution.**

- **The human invokes** the governance/decision skills (define requirements, freeze ACs, start the loop, review, merge).
- **The AI runs** the verification/support skills internally — the human normally does not call these directly; higher-level skills run them automatically.

For the detailed responsibility split, the human-perspective flow, and who calls which skill, see
[`ONBOARDING.md` §6-0](ONBOARDING.md#6-0-what-the-human-does-responsibility-split)
(日本語: [`ONBOARDING.ja.md` §6-0](ONBOARDING.ja.md#6-0-人が何をするか責任分担)).
The full flow with all skill dependencies is in [`SKILL_FLOW.md`](SKILL_FLOW.md).

---

## Skills

Run skills in Claude Code chat by typing `/skill-name`.

### Invoked directly by the human (governance / decisions)

| Skill | Purpose |
|-------|---------|
| `init-project` | Project initialization (Phase 0 → Phase 1). Run once at adoption |
| `create-requirements` | Define User Stories, the **goal image** (what the user can do when done / primary journey / non-goals), acceptance conditions, and constraints (`docs/01_requirements/`) |
| `create-spec` | Draft the application spec — *what* the app does — plus **E2E scenarios** (`E2E-001 → AC-001, AC-003` cross-cutting traceability) from approved requirements (`docs/02_spec/`, `status: draft`; needs human approval) |
| `create-exec-plan` | Create a new execution plan with acceptance criteria (AC-001~) and **at least one `[E2E]` AC** (documentation-only plans carry none), each checked for **AC readiness** (testability) and given a **`## Sources`** row naming the US bullets and spec section it condenses. A plan that changes a DocDD process carries a **process-walkthrough** verification AC |
| `start-feature` | Pre-implementation review, AC readiness re-check, loading of the US / spec sections in `## Sources`, and branch name decision (once per feature) |
| `run-exec-plan` | Gate on **AC readiness** before the loop starts (a NOT READY criterion halts it), place the `[E2E]` test red, then autonomously implement ACs one by one (**read the AC's sources** → **write the failing test** → implement → test → fix → **re-anchor to the spec section** → next); halts only on stop conditions (opt-in) |
| `pre-pr` | Comprehensive pre-PR check (invariants / doc-freshness / doc-invariants / review_checklist / run-tests / exec-plan update) |
| `complete-exec-plan` | Move execution plan from `active/` to `completed/` |
| `promote-spec` | Promote a next-version spec (`spec/<label>` branch) into the current target (sprint boundary) |
| `gc` | Periodic garbage collection (documentation and architecture health check; weekly) |

### Run internally by the AI (verification / support)

| Skill | Purpose |
|-------|---------|
| `run-tests` | Run tests and verify against spec (spec alignment gate determines action on failure; classifies valid vs. invalid red on a red-first run) |
| `check-invariants` | Verify invariants in `invariants.md` against implementation code |
| `check-doc-freshness` | Check freshness of documents corresponding to changed code |
| `check-doc-invariants` | Check documents for structural-rule (doc-INV) violations |
| `update-context` | Update CONTEXT.md to reflect current state |

### Optional independent review (human-invoked when desired, no authoring context)

| Skill | Purpose |
|-------|---------|
| `doc-review` | Independent agent reviews a requirements or spec document (AC testability via the shared readiness checks, completeness, references) |
| `docode-review` | Independent agent reviews changed code against the ACs and general quality |

> `run-tests` is model-invocable (callers invoke it via the Skill tool); the other internal skills are executed by higher-level skills following their `SKILL.md` steps inline. See CLAUDE.md "検証スキルの呼び出しポリシー".

---

## Directory Structure

```
project-root/
├── .claude/
│   ├── settings.json          # Hook configuration (auto-reminders on code changes)
│   └── skills/                # Skill definitions
│       ├── init-project/
│       ├── create-requirements/
│       ├── create-spec/
│       ├── create-exec-plan/
│       ├── start-feature/
│       ├── run-exec-plan/
│       ├── pre-pr/
│       ├── complete-exec-plan/
│       ├── promote-spec/
│       ├── run-tests/
│       ├── check-invariants/
│       ├── check-doc-freshness/
│       ├── check-doc-invariants/
│       ├── doc-review/
│       ├── docode-review/
│       ├── update-context/
│       └── gc/
├── docs/                      # ← generated by init-project (does not exist initially)
│   ├── 00_project/            # overview.md, decisions.md, glossary.md
│   ├── 01_requirements/       # constraints.md, user_stories/
│   ├── 02_spec/               # app_spec.md (what the app does)
│   ├── 03_design/             # architecture.md, data_model.md, api_spec.md
│   ├── 04_implementation/     # invariants.md, patterns.md, dependencies.md
│   ├── 05_quality/            # test_strategy.md, review_checklist.md
│   ├── 06_operations/         # environments.md, monitoring.md
│   └── 07_ai_context/         # CONTEXT.md (navigation map)
└── exec-plans/                # ← generated by create-exec-plan (does not exist initially)
    ├── active/                # In-progress execution plans
    └── completed/             # Completed execution plans
```

---

## Harness (Automation)

PostToolUse hooks are configured in `.claude/settings.json`.

| Trigger | Reminder |
|---------|---------|
| Editing `exec-plans/completed/` | Prompts to run `update-context` |
| Editing `exec-plans/active/` | Prompts to verify CONTEXT.md is updated |
| Editing test files (`*.Test.cs` / `*.test.ts` / `*.spec.ts`, etc.) | Prompts to confirm the change is grounded in a spec (AC-ID) |
| Editing code files | Prompts to run `check-doc-freshness`, and to use `run-tests` spec alignment on test failures |

Code file detection is language-agnostic (anything other than `.md`, `.json`, `.yaml`, and other document/config files is treated as code).

---

## Test Assurance (Spec Alignment Gate)

In DocDD, tests are positioned as "executable expressions of the spec."

### Red-first (INV-T02)

An expression of the spec has to be written **from the spec**. For each AC the test is authored
first — from the AC line **and its sources**, before the implementation exists — and run to confirm
it fails for the
right reason; that red observation is recorded in the exec-plan's decision log and freezes the
expectation. A test written alongside the code records what the code does and goes green either way.

`/run-exec-plan` does this per AC, and puts the plan's `[E2E]` test in place, red, before any AC is
implemented. The procedure, the valid/invalid red distinction and the exemptions are in
[`.claude/skills/run-tests/red-first.md`](.claude/skills/run-tests/red-first.md).

### AC sources and the spec re-anchor

An exec-plan AC is **one line** — `spec-gate.py` parses `AC-(\d{3}):`, so the checkable bullets stay
in the User Story and the behavior stays in the spec section marked "satisfies AC-NNN". A plan that
does not say where its one-liners point hands the implementer an interpretation instead of a goal.

Each plan therefore carries a `## Sources` table, one row per AC, and it is read at two moments:

- **before the test is drafted** (`run-exec-plan` Step 1b, `start-feature` Step 2) — so the given /
  when / then come from the whole frozen goal, not from a condensation of it;
- **before the AC's box is checked** (`run-exec-plan` Step 3a) — the *spec re-anchor*: passing tests
  prove only what was transcribed into them, so the finished behavior is compared once more against
  the spec section the AC traces to.

Sources are frozen spec material only — never the implementation code, which would undo red-first.
The table format, the four ways a source can disagree with its AC line, and the re-anchor verdicts
are in [`.claude/skills/create-exec-plan/ac-sources.md`](.claude/skills/create-exec-plan/ac-sources.md).

### Spec alignment gate

When a test fails after its implementation exists, do not immediately fix the test.
The `run-tests` skill presents the following decision gate:

```
A) The test correctly expresses the spec
   → There is a bug in the implementation. Fix the implementation.

B) The spec has changed and the test is outdated
   → Fix the test based on the spec (AC-ID).
   ⚠️ Fixing tests to match implementation behavior is prohibited (INV-T01)
```

### Traceability via AC-IDs

Include the acceptance criteria IDs (AC-001, AC-002, ... from the exec-plan) in test code
to track the correspondence between specs and tests.

```csharp
// C# / xUnit
[Trait("AC", "AC-001")]
public void Login_WithInvalidPassword_Returns401() { ... }
```

```typescript
// TypeScript / Vitest
describe('AC-001: Login with invalid password', () => {
  it('returns 401', () => { ... });
});
```

The `run-tests` skill verifies that all AC-IDs have corresponding tests.

### When to run within the workflow

| Timing | Purpose |
|--------|---------|
| `start-feature` start | Baseline check (start implementation from a green state) |
| During implementation (anytime) | Verify anytime with `/run-tests` |
| `pre-pr` | Final check before PR (put on hold if there are failures or uncovered ACs) |
| `complete-exec-plan` | All AC-ID tests passing is a required condition for completion |

---

## Document–Code Synchronization

Set a `tracks:` field in each document's frontmatter to define the corresponding code files.

```yaml
---
status: active
tracks:
  - src/**/models/**
  - src/**/repositories/**
---
```

The `check-doc-freshness` skill reads this field and detects missed documentation updates when code changes.

---

## Detailed Specification

Refer to each skill's `SKILL.md`. Document structure, required/optional criteria, status lifecycle, and the exec-plan template are all consolidated in `init-project/SKILL.md`.

---

## License

[MIT](LICENSE)
