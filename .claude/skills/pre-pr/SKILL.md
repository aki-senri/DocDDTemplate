---
name: pre-pr
description: |
  Comprehensive pre-PR check skill run before creating a pull request.
  Runs invariant checks, document freshness checks, review checklist, tests, and exec-plan progress update all at once.
disable-model-invocation: true
---

# Skill: Pre-PR Comprehensive Check

> **When to run**: After implementation is complete, immediately before creating a PR
>
> **Purpose**: Detect all quality standard violations, documentation inconsistencies, and missing progress records
> before reaching CI, minimizing PR review time.
>
> **Prerequisites**:
> - Implementation must be complete
> - `docs/04_implementation/invariants.md` must exist
> - `docs/05_quality/review_checklist.md` must exist

---

## What this skill does

Runs the following steps in order. If all pass, PR creation is allowed.

```
① check-invariants      → Verify code invariants
② check-doc-freshness   → Verify documentation freshness
③ check-doc-invariants  → Verify document structural invariants
④ review_checklist      → Code review checklist
⑤ run-tests             → Run tests and verify against spec, incl. [E2E] AC coverage
                          and red-first evidence (⚠️ only)
⑤b process walkthrough  → For a plan that changed a process: evidence check (⚠️ only)
⑥ exec-plan update      → Record progress in log
```

---

## Steps

### ① Invariant check (check-invariants)

Load `docs/04_implementation/invariants.md` and verify the following for each INV.

1. List changed files (`git diff --name-only HEAD` or from the known changes)
2. Review each INV and extract conditions applicable to the changed files
3. Report any violations and provide fix instructions
4. If no violations: display "✅ invariants: all passed"

**The check criteria follow `docs/04_implementation/invariants.md`.**
Typical violation pattern examples (adapt according to the project's invariants.md contents):

| Common INV types | Example check points |
|-----------------|---------------------|
| Layer dependency direction | Does an upper layer directly depend on a lower layer's implementation? |
| File size limit | Does the line count exceed the limit defined in the INV? |
| Naming conventions | Does the file follow the naming pattern defined in the INV? |
| Forbidden patterns | Are language/framework-specific forbidden APIs or antipatterns used? |
| Validation location | Is input validation performed in the layer specified by the INV? |

---

### ② Document freshness check (check-doc-freshness)

Verify that documents corresponding to changed code files are up to date.

1. List the paths of changed files
2. Check the `tracks:` field in the frontmatter of `docs/**/*.md`
3. Identify documents whose `tracks:` pattern matches the changed files
4. Open each matching document and check for discrepancies with the code changes
5. If discrepancies exist, identify the update locations and fix them
6. If no discrepancies: display "✅ doc-freshness: all passed"

**Typical cases requiring a check:**

| Code change | Documents to check |
|------------|-------------------|
| Model / Entity added or changed | `docs/03_design/data_model.md` |
| API endpoint added or changed | `docs/03_design/api_spec.md` |
| Directory structure changed | `docs/04_implementation/directory_structure.md` |
| New pattern or convention introduced | `docs/04_implementation/patterns.md` |
| External library added | `docs/04_implementation/dependencies.md` |

---

### ③ Document invariant check (check-doc-invariants)

Run the `check-doc-invariants` skill.

1. Collect all `docs/**/*.md` and `exec-plans/**/*.md`
2. Check DOC-INV-001 (reference direction), DOC-INV-002 (frontmatter completeness),
   DOC-INV-003 (lifecycle consistency), DOC-INV-004 (AC traceability),
   DOC-INV-005 (diagram rules), DOC-INV-006 (goal image / E2E traceability)
3. If no violations: display "✅ doc-invariants: all passed"

---

### ④ Review checklist

Load `docs/05_quality/review_checklist.md` and verify each item.

- ✅ Passed
- ❌ Not addressed (requires fix)
- N/A Not applicable

---

### ⑤ Test execution & spec verification (run-tests)

Run the `run-tests` skill.

1. All tests must pass
2. Every AC-ID must have a corresponding test (coverage check)
3. **Every `[E2E]` AC must have a test that exists and passed** (E2E coverage check)
4. If there are changes to test files, confirm the changes are grounded in a spec (AC-ID)

**Why E2E coverage is checked separately.** Steps 1–2 can both be ✅ while the feature does not
work when used end to end: each functional AC is green in isolation, and nothing verifies that
they add up. The `[E2E]` ACs (see `create-exec-plan`) are the criteria that cover the through-flow,
so they are checked as their own gate rather than folded into the per-AC count.

```
E2E acceptance criteria:
  ✅ AC-005 [E2E] → LoginJourneyE2ETest: SignIn_To_Dashboard_EndToEnd  (passed)
  ❌ AC-006 [E2E] → No test created
```

Two situations, two outcomes (same split as `run-tests`):

| Situation | Outcome |
|-----------|---------|
| The plan **has** a `[E2E]` AC, but its test is missing / did not run / failed | ❌ **blocks PR creation** — same weight as a failing test |
| The plan has **no** `[E2E]` AC at all | ⚠️ **report only, does not block** |

The second case has legitimate causes (the plan predates the E2E requirement, or it is
documentation-only — see `create-exec-plan`), so it is a warning. Report it and direct the user to
`create-exec-plan`. Do not write the criterion here — defining what to build is an outer gate.

**Red-first evidence check (⚠️ report only):**

For each AC in the plan, look in the plan's `## Decision Log` for an `AC-NNN red-first:` entry
positioned **before** that AC's `AC-NNN done.` entry — the record that the test was written from the
AC and observed failing before the implementation existed (see
[`../run-tests/red-first.md`](../run-tests/red-first.md)).

```
Red-first evidence:
  ✅ AC-001 → red 観測あり (done より前)
  ⚠️ AC-002 → 記録なし（テストが実装の写しでないことを後から確認できない）
  ➖ AC-003 → n/a（既存テストで保証される preservation AC）
```

This is a **warning, not a blocker**. The evidence lives in hand-written Decision Log text, so a
missing entry cannot be distinguished mechanically from a missed note; blocking on it would push
people to write the entry after the fact, which is exactly the evidence being destroyed. What blocks
PR creation stays what it was: failing tests, uncovered ACs, uncovered `[E2E]` ACs.

Report missing entries and, when the tests for those ACs were written after their implementation,
say so plainly rather than back-dating a `red-first` line. `/docode-review` is the check that can
still judge those tests on their content.

**Test file change verification:**

If test file changes are detected via `git diff --name-only main...HEAD`, verify the following:

```
⚠️ Test file changes detected:
  AuthServiceTest.cs has been modified.
  Please record the reason for the change in the decision log:
    [ ] Test fix due to spec change (AC-XXX update)
    [ ] Test addition for new acceptance criteria
    [ ] Refactoring (no behavioral change to tests)
    ❌ Test fix to match implementation behavior (this is NOT allowed)
```

- If tests fail: resolve through the `run-tests` spec alignment gate before re-running
- If AC-IDs are uncovered: add tests before re-running
- If a `[E2E]` AC is uncovered or its test did not pass: the through-flow is not verified — add or
  fix the E2E test before re-running. Do not proceed to PR on functional ACs alone
  (a plan with no `[E2E]` AC at all is a ⚠️ and does not block — see the table above)

---

### ⑤b Process walkthrough evidence (⚠️ report only)

If the plan changed a **process** — a loop, a resumable run, a stop condition, a gate, an exemption,
or a rule other rules consume (scope table in
[`../create-exec-plan/process-walkthrough.md`](../create-exec-plan/process-walkthrough.md)) — check
the plan's `## Decision Log` for a walkthrough record naming its laps.

```
Process walkthrough:
  ✅ AC-008 → 6周（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時）、検出 2 件 → 修正済み
  ⚠️ 記録なし（プロセスを変更しているが、記述の突き合わせしか行われていない可能性）
  ➖ n/a（状態遷移を伴わない変更）
```

**Warning, not a blocker**, for the same reason as the red-first evidence check: the record is
hand-written, so a missing line cannot be told apart mechanically from an unrecorded-but-done check.
Report it; do not reconstruct the walkthrough here — after the fact, "it looked consistent" is
exactly the judgement this check exists to replace.

### ⑥ exec-plan progress update

Update the `exec-plans/active/*.md` corresponding to the implemented work.

1. Check off completed tasks (`- [x]`)
2. Append today's date and a description of what was done to the progress log
3. If all acceptance criteria are met, guide the user to run the `complete-exec-plan` skill

---

## Result report format

```
=== pre-pr check results ===

① invariants       : ✅ all passed  / ❌ {count} violation(s)
② doc-freshness    : ✅ all passed  / ⚠️ {count} update(s) needed
③ doc-invariants   : ✅ all passed  / ❌ {count} violation(s) / ⚠️ {count} warning(s)
④ review_checklist : ✅ all passed  / ❌ {count} item(s) not addressed
⑤ run-tests        : ✅ all passed, AC coverage complete  / ❌ {count} failure(s) or uncovered ACs
  └ E2E coverage   : ✅ {n}/{n} [E2E] AC covered and green  / ❌ {count} uncovered or failing (blocks)
                     / ⚠️ プランに [E2E] AC がありません (does not block)
  └ Red-first      : ✅ {n}/{n} AC に赤の観測記録あり  / ⚠️ AC-NNN 記録なし (does not block)
                     / ➖ n/a (documentation-only)
⑤b walkthrough     : ✅ {n} 周の記録あり  / ⚠️ プロセス変更だが記録なし (does not block)
                     / ➖ n/a (状態遷移なし)
⑥ exec-plan        : ✅ Progress updated

---
{If there are issues, list specific fix instructions here}
---

PR creation status: ✅ No issues / ❌ Fix the above and re-run
```

---

## Completion criteria

- [ ] All checks ① through ⑥ (including ⑤b) are complete
- [ ] All issues have been fixed, or documented as "N/A" with explanation
- [ ] If tests failed, they were resolved through the spec alignment gate
- [ ] Every `[E2E]` AC in the plan has a test that exists and passed (or the plan's lack of an
      `[E2E]` AC was reported and referred back to `create-exec-plan`)
- [ ] Red-first evidence was checked per AC and any missing entry was reported (⚠️ — it does not
      block PR creation, and a missing entry is never filled in after the fact)
- [ ] For a plan that changed a process: the walkthrough record was checked and any absence
      reported (⚠️ — does not block, and is not reconstructed here)
- [ ] If test files were changed, the reason is recorded in the decision log
- [ ] The progress log in exec-plan has been updated
- [ ] Output shows "PR creation status: ✅ No issues"
