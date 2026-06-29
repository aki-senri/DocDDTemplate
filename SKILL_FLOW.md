# DocDD Skill Operation Flow & Gap Analysis

> **Human-perspective flow & responsibility split** (the two-layer split of skills the human invokes
> vs. skills the AI runs internally) is documented in
> [`ONBOARDING.md` §6-0](ONBOARDING.md#6-0-what-the-human-does-responsibility-split)
> (日本語: [`ONBOARDING.ja.md` §6-0](ONBOARDING.ja.md#6-0-人が何をするか責任分担)).
> This document covers the detailed flow including all skill dependencies.

## 1. Overall Flow

```mermaid
flowchart TD
    START([Project Start]) --> INIT

    subgraph PHASE01["Phase 0→1: Initialization"]
        INIT["/init-project\n· Ask for overview / tech stack / dev rules\n· Generate docs/**\n· Generate CONTEXT.md"]
    end

    INIT --> REQ

    subgraph PLAN_PHASE["Implementation Planning (at each feature start)"]
        REQ["/create-requirements\n· Interview on User Story\n· Define AC conditions\n· Generate docs/01_requirements/user_stories/US-XXX.md\n· Update constraints.md"]
        REQ -.->|optional review| DR
        DR["/doc-review\n· Independent agent reviews docs (requirements or spec)\n· Checks AC testability, completeness\n· Checks reference direction\n· Returns verdict: ✅/⚠️/❌"]
        SPEC["/create-spec\n· Draft application spec (what the app does)\n· from approved requirements\n· Generate docs/02_spec/ (status: draft)\n· Independent review + HUMAN approval before freeze"]
        REQ --> SPEC
        SPEC -.->|optional review| DR
        SPEC -->|after human approval| PLAN
        REQ -.->|small change: skip spec| PLAN
        PLAN["/create-exec-plan\n· Interview on goals & scope\n· Define AC-001~\n· Save to exec-plans/active/\n· Update priority tasks in CONTEXT.md"]
        PLAN --> SF
        SF["/start-feature\n① Confirm baseline with run-tests\n② Load CONTEXT.md\n③ Load invariants.md\n④ Load exec-plan (AC)\n⑤ Decide branch name\n⑥ Record start in progress log"]
    end

    SF --> IMPL

    subgraph IMPL["Implementation Loop"]
        DRIVER["/run-exec-plan (opt-in)\nAutonomous driver: per AC\nimplement→verify→fix→next\nHalts only on stop conditions"]
        CODE["Code change\n(Write / Edit)"]
        HOOK["PostToolUse hook\n⚠ Warning message only\n(does not block)"]
        CDF["/check-doc-freshness\nUpdate docs corresponding to\nchanged files via tracks: field"]
        CI["/check-invariants\nVerify no INV-XXX violations"]
        RT["/run-tests\nRun tests + spec alignment gate\n(forbids adjusting tests to match impl)"]

        DRIVER -->|drives inner loop| CODE
        CODE --> HOOK
        HOOK -.->|manual, or auto via driver| CDF
        HOOK -.->|manual, or auto via driver| CI
        HOOK -.->|manual, or auto via driver| RT
        CDF --> CODE
        CI --> CODE
        RT -->|green: next AC| DRIVER
        RT -->|red: fix| CODE
    end

    IMPL --> PREPR

    subgraph PREPR_PHASE["Before PR Creation"]
        PREPR["/pre-pr\n① check-invariants\n② check-doc-freshness\n③ check-doc-invariants\n④ Confirm review_checklist\n⑤ run-tests + AC coverage check\n⑥ Update exec-plan progress checkboxes"]
    end

    PREPR --> PR
    PR["Create PR → Review → Merge"]
    PR --> COMPLETE

    subgraph COMPLETE_PHASE["Completion (after PR merge)"]
        COMPLETE["/complete-exec-plan\n① Confirm all AC checkboxes\n② run-tests (final check)\n③ AC coverage check\n④ Move active/ → completed/\n⑤ Update CONTEXT.md priority tasks"]
    end

    COMPLETE --> NEXT
    NEXT{Next plan exists?}
    NEXT -->|Yes| PLAN
    NEXT -->|No| GC_WAIT

    subgraph GC_PHASE["Periodic Maintenance (weekly)"]
        GC_WAIT["Standby"]
        GC["/gc\n① Full scan: check-doc-freshness\n② Full scan: check-invariants\n③ Full scan: check-doc-invariants\n④ Document lifecycle cleanup\n⑤ update-context\n⑥ Generate GC report"]
        GC_WAIT -->|Weekly or after large merge| GC
        GC --> GC_WAIT
    end

    subgraph SPEC_PROMO["Spec Version Promotion (sprint boundary)"]
        SPECBR["spec/* branch\n· Accumulate next-version spec (docs only)\n· In-version fixes commit to main directly"]
        PROMO["/promote-spec\n· Diff main vs the spec branch → classify NEW/CHANGED/REMOVED ACs\n· Find stale impl + in-flight collisions\n· HUMAN decision, then merge --no-ff\n· Tag new target snapshot (spec-target-*); prev already tagged, seed baseline on 1st\n· Create reconcile exec-plan for stale ACs"]
        SPECBR --> PROMO
    end

    PROMO -->|reconcile + new-AC plans| PLAN

    UC["/update-context\n· On phase transition\n· On priority task change\n· On tech stack change\n(called automatically from gc)"]
    GC --> UC
```

> **Note**: `complete-exec-plan` updates `CONTEXT.md` **directly** in its own Step 4; it does not invoke the `update-context` skill. Only `gc` calls `update-context` internally.

---

## 2. Skill Call Relationships

| Caller | Callee | Type |
|--------|--------|------|
| `create-requirements` | `create-spec` | Handoff (suggests next step) |
| `create-requirements` | `doc-review` | Optional handoff (user-triggered) |
| `create-spec` | `doc-review` | Handoff (suggests independent review of the spec) |
| `create-spec` | `create-exec-plan` | Handoff (after human approval of the spec) |
| `pre-pr` | `check-invariants` | Internal call |
| `pre-pr` | `check-doc-freshness` | Internal call |
| `pre-pr` | `check-doc-invariants` | Internal call |
| `pre-pr` | `run-tests` | Internal call |
| `start-feature` | `run-tests` | Internal call |
| `run-exec-plan` | `run-tests` | Internal call (per AC, inline) |
| `run-exec-plan` | `check-invariants` | Internal call (per AC, inline) |
| `run-exec-plan` | `check-doc-freshness` | Internal call (advisory) |
| `complete-exec-plan` | `run-tests` | Internal call |
| `complete-exec-plan` | —— | Updates `CONTEXT.md` directly (does not call `update-context`) |
| `gc` | `check-doc-freshness` | Internal call (full scan) |
| `gc` | `check-invariants` | Internal call (full scan) |
| `gc` | `check-doc-invariants` | Internal call (full scan) |
| `gc` | `update-context` | Internal call |
| `promote-spec` | `create-exec-plan` | Handoff (suggests new-AC plans after promotion) |
| `promote-spec` | `start-feature` | Handoff (reconcile exec-plan → begin reconciliation) |
| `PostToolUse` hook | —— | Warning message only (no skill call) |

---

## 3. Gap List

### 3-1. Structural Hook Issues (Most Critical)

> **Note**: As of the current implementation, both `PostToolUse` and `UserPromptSubmit` hooks are configured in `.claude/settings.json` using Python (`python3`). G1 and G3 from the original analysis are resolved; the remaining hook concern is G2.

| # | Issue | Impact | Severity |
|---|-------|--------|----------|
| G1 | ~~`PostToolUse` hook specifies `shell: "powershell"`, non-functional on Linux/Mac~~ **Resolved** — hooks now use `python3` commands | — | ✅ Resolved |
| G2 | **Hook only displays a warning message and does not block** | Developer can ignore the warning and continue implementing | 🟡 Medium |
| G3 | ~~`UserPromptSubmit` hook does not exist~~ **Resolved** — `spec-gate.py` is already configured | — | ✅ Resolved |

### 3-2. Bypasses Before Implementation Starts

| # | Bypass | Result | Severity |
|---|--------|--------|----------|
| B1 | Issue "implement this" without running `create-exec-plan` | Implementation starts with no AC / undefined spec | 🔴 Critical |
| B2 | Begin implementation without running `start-feature` | Baseline tests unchecked; CONTEXT.md / invariants.md unread | 🟠 High |
| B3 | exec-plan exists but implementation is instructed while skipping `start-feature` steps | Step 0 (baseline check) is skipped; pre-existing failing tests go unnoticed | 🟠 High |

### 3-3. Bypasses During Implementation

| # | Bypass | Result | Severity |
|---|--------|--------|----------|
| B4 | Ignore hook warning after code change | Proceeds to next implementation without verifying docs | 🟡 Medium |
| B5 | Skip manual call to `check-doc-freshness` | Doc/impl drift accumulates silently | 🟡 Medium |
| B6 | Skip manual call to `check-invariants` | INV violations go undetected until just before PR | 🟡 Medium |
| B7 | Fix failing tests without going through the spec alignment gate | Test changes without spec justification occur (INV-T01 violation) | 🟠 High |

> **Inner-loop automation (issue #11)**: The bypasses above stem partly from the implementation
> loop being a *manual chain* (code → manually invoke CDF/CI/RT). `/run-exec-plan` provides an
> **opt-in autonomous inner loop** that, within a frozen AC set, runs implement → run-tests →
> check-invariants → advance without per-step confirmation, while still halting at the
> **outer gates** (B7's spec alignment gate, irreversible actions, ambiguous AC). It automates
> *execution*, not *governance* — see "自律実装ループ" in CLAUDE.md for the stop conditions.

### 3-4. Bypasses Before PR

| # | Bypass | Result | Severity |
|---|--------|--------|----------|
| B8 | **Create PR without running `pre-pr`** | All checks skipped: invariants, doc-freshness, review_checklist, tests, AC coverage | 🔴 Critical |
| B9 | Create PR despite ❌ in `pre-pr` results | Quality gate becomes meaningless | 🟠 High |

### 3-5. Bypasses in Completion

| # | Bypass | Result | Severity |
|---|--------|--------|----------|
| B10 | Do not run `complete-exec-plan` after PR merge | Zombie plans remain in `exec-plans/active/`; CONTEXT.md goes stale | 🟡 Medium |
| B11 | Skip weekly `gc` runs | Drift accumulates, increasing future correction cost | 🟡 Medium |

---

## 4. Mandatory Gates vs. Optional Gates in the Flow

```mermaid
flowchart TD
  A[Implementation request] --> R["create-requirements (optional)"]
  R --> B["create-exec-plan (optional)"]
  B --> C["start-feature (optional)"]

  C --> L[Implementation loop: optional checks]
  L --> L

  L --> P["pre-pr (optional)"]
  P --> M[Create PR → Merge]
  M --> Q["complete-exec-plan (optional)"]
  Q --> G["gc (optional, weekly)"]
  G --> Z[Done]
```

**Mandatory gates (impossible to skip): currently zero.**
All skills are manually invoked, and hooks do not block execution.

> **Spec version promotion** (`/promote-spec`) is a separate, human-gated event that runs at sprint
> boundaries rather than on the linear path above. It merges a `spec/*` branch into `main`, tags the
> outgoing version (`spec-target-*`), and feeds reconcile / new-AC plans back into the planning phase.
> The merge is a deliberate human decision; the skill only assists analysis before and bookkeeping after.

---

## 5. Improvement Proposals

### High Priority

| Improvement | Approach |
|-------------|----------|
| **Extend `spec-gate.py` to also check for `create-requirements`** | Currently `spec-gate.py` (UserPromptSubmit) checks for an exec-plan but not a User Story. Add a check for `docs/01_requirements/user_stories/` so that implementing without a US also triggers a warning |
| **Remind to run `pre-pr` before PR creation** | Add a `PostToolUse` hook that detects MCP calls like `mcp__github__create_pull_request` and warns if `pre-pr` has not been executed |

### Medium Priority

| Improvement | Approach |
|-------------|----------|
| **Change hook warnings to blocking** | Return `exit 1` from `post-tool-notify.py` to block Write/Edit and force user confirmation (use `exit 2` for a softer block if full blocking is too aggressive) |
| **`complete-exec-plan` reminder** | Prompt users to run `complete-exec-plan` via a post-merge hook or message |
