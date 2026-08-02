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
⑤c AC sources           → ## Sources present + spec re-anchor recorded per AC (⚠️ only)
⑤d docode-review evidence → For a plan completed by run-exec-plan: verdict recorded? (⚠️ only)
⑥ exec-plan update      → Record progress in log
```

> **Changes made with no exec-plan.** ⑤ (red-first evidence), ⑤b, ⑤c, ⑤d and ⑥ all read or write a
> plan file. A change made under the `exec-plans/.spec-override` exception has none — its evidence
> lives in the branch's commit messages instead. Note that CLAUDE.md has the override file **deleted
> once implementation completes**, which is before this skill runs: do not expect to find it. Check
> `git log main..HEAD` for the evidence before reporting ⚠️ for any of the five. Evidence recorded
> outside a plan file is a `➖`, not a missing record, and ⑥ has nothing to update. With no plan and
> no such record anywhere, the ⚠️ stands.
>
> This does **not** relax ⑤'s blocking parts. Failing tests, uncovered ACs and uncovered `[E2E]` ACs
> block a plan-less change exactly as they block any other.

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
  ✅ AC-008 → 7周（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時 / 依存の逆流）、検出 2 件 → 修正済み
  ✅ AC-004 → 依存の逆流のみ（改称のため 1〜6周は適用外と明記）、列挙あり、検出 1 件 → 修正済み
  ⚠️ 記録なし（プロセスを変更しているが、記述の突き合わせしか行われていない可能性）
  ⚠️ 依存の逆流の記録に参照元の列挙がない（何も見つからなかったのか、どこも見なかったのかを判別できない）
  ➖ n/a（状態遷移を伴わず、変更した箇所を指す記述も他に無い）
```

A lap-7-only record is **not** an under-specified one: the scope table in the single source admits a
rename as lap 7's own case, and the record format for it requires saying which laps do not apply and
why. Read for that sentence rather than for a lap count.

**When the change has no plan at all**, see the note under the ①–⑥ overview above — it governs ⑤,
⑤b, ⑤c, ⑤d and ⑥ alike, and is stated once there rather than repeated per check.

The lap-7 line is the one worth reading closely. `process-walkthrough.md` requires that lap to record
**both halves of its enumeration** — the call-site table it started from and the grep it widened
with — plus the referrers they returned, precisely because "依存の逆流: PASS" alone is not
falsifiable. Report the enumeration's absence separately from the record's absence.

**Warning, not a blocker**, for the same reason as the red-first evidence check: the record is
hand-written, so a missing line cannot be told apart mechanically from an unrecorded-but-done check.
Report it; do not reconstruct the walkthrough here — after the fact, "it looked consistent" is
exactly the judgement this check exists to replace.

### ⑤c AC sources and spec re-anchor (⚠️ report only)

Two things, both read from the plan file (see
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md)):

1. **`## Sources` present** — a table with a row for every AC, each naming a section or an explicit
   `n/a（理由）`. A plan authored before this convention has no table at all; report that too.
2. **Spec re-anchor recorded per AC** — each `AC-NNN done.` entry in the `## Decision Log` should
   carry a `spec 再アンカー:` line naming the section the finished result was checked against, or
   `n/a（理由）`.

```
AC sources / spec re-anchor:
  ✅ ## Sources: 5/5 AC に行あり
  ✅ AC-001 → spec 再アンカー記録あり（app_spec.md §「タグの付与」）
  ⚠️ AC-002 → 再アンカー記録なし（緑判定が spec に照らされたか後から確認できない）
  ➖ AC-003 → n/a（起点なし）
```

**Warning, not a blocker**, same reasoning as ⑤ and ⑤b: both artifacts are hand-written prose, so a
missing line cannot be distinguished mechanically from an unrecorded-but-performed check, and
blocking would teach people to add the line afterwards — destroying the evidence. What blocks PR
creation stays what it was: failing tests, uncovered ACs, uncovered `[E2E]` ACs.

**Do not fill in a missing table here.** Reconstructing sources after the implementation exists
means inferring them from the code, which is the one reading `ac-sources.md` forbids. Report the
absence; if the plan is still active, the rows are written at the plan from the US and spec — the
`create-exec-plan` path — never from the diff in front of you.

### ⑤d docode-review evidence for autonomous completions (⚠️ report only)

`run-exec-plan` Step 4a makes `docode-review` **mandatory** once every AC in a plan reaches `- [x]`
(it halts with stop condition (f) on a ❌ verdict rather than handing off — see
[`../run-exec-plan/SKILL.md`](../run-exec-plan/SKILL.md)). On the manual `start-feature` path,
`docode-review` stays optional, as before.

Check whether the plan's `## Decision Log` carries an `AC readiness: ... (Step 0b)` entry. Use
**only** this phrase as the marker — not `red-first:` / `spec 再アンカー:` entries, which are part of
the general Decision Log convention and can appear in a manually-authored plan too (a human following
the same write-up style writes the same phrases without ever running `run-exec-plan`). The
`(Step 0b)` phrase is the one that is actually unique to that skill's own gate, since only its Step
0b produces it. If such a marker is present, look for the **most recent**
`docode-review (Step 4a): verdict ...` entry — recency matters here, since a plan can legitimately
carry more than one (a reconcile plan reopening ACs runs Step 4a again on its own later completion,
per `run-exec-plan`'s resume rule).

```
docode-review evidence:
  ➖ n/a（手動実装 — run-exec-plan の痕跡なし。docode-review は引き続き任意）
  ✅ run-exec-plan 完了 → 直近の docode-review verdict ✅ Approved 記録あり
  ⚠️ run-exec-plan 完了の痕跡があるが docode-review の記録なし（Step 4a が実行されたか後から確認できない）
  ⚠️ 直近の docode-review verdict が ❌ Changes requested のまま（run-exec-plan は本来ここで HALT する
     はずであり、それでも PR に進むのは記録の上では未解決の指摘を残したままの手動判断）
```

**Warning, not a blocker**, for the same reason as ⑤/⑤b/⑤c: the marker and the verdict are both
hand-written Decision Log prose, so an absent line cannot be told apart mechanically from an
unrecorded-but-performed step. The real enforcement is upstream, inside `run-exec-plan` itself
(Step 4a blocks its own handoff on ❌) — this check is a backstop, not the gate. **Do not run
`docode-review` here to fill the gap**; report the absence and let the human decide whether to go
back and run it.

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
⑤b walkthrough     : ✅ {n} 周の記録あり（依存の逆流に参照元の列挙あり）
                     / ✅ 依存の逆流のみの記録あり（改称のため 1〜6周 適用外と明記）
                     / ⚠️ プロセス変更だが記録なし / ⚠️ 依存の逆流に列挙なし (does not block)
                     / ➖ n/a (状態遷移を伴わず、変更箇所を指す記述も他に無い)
                     / ➖ n/a (プラン無しの変更 — 記録は commit message)
⑤c AC sources      : ✅ {n}/{n} AC に起点行あり  / ⚠️ ## Sources なし (does not block)
  └ 再アンカー     : ✅ {n}/{n} AC に記録あり  / ⚠️ AC-NNN 記録なし (does not block)
                     / ➖ n/a (起点なし)
⑤d docode-review   : ✅ verdict 記録あり  / ⚠️ run-exec-plan 完了の痕跡ありだが記録なし (does not block)
                     / ⚠️ 直近の verdict が ❌ のまま (does not block) / ➖ n/a (手動実装)
⑥ exec-plan        : ✅ Progress updated

---
{If there are issues, list specific fix instructions here}
---

PR creation status: ✅ No issues / ❌ Fix the above and re-run
```

---

## Completion criteria

- [ ] All checks ① through ⑥ (including ⑤b and ⑤c) are complete
- [ ] All issues have been fixed, or documented as "N/A" with explanation
- [ ] If tests failed, they were resolved through the spec alignment gate
- [ ] Every `[E2E]` AC in the plan has a test that exists and passed (or the plan's lack of an
      `[E2E]` AC was reported and referred back to `create-exec-plan`)
- [ ] Red-first evidence was checked per AC and any missing entry was reported (⚠️ — it does not
      block PR creation, and a missing entry is never filled in after the fact)
- [ ] For a plan that changed a process: the walkthrough record was checked and any absence
      reported (⚠️ — does not block, and is not reconstructed here)
- [ ] The plan's `## Sources` table and the per-AC `spec 再アンカー:` records were checked and any
      absence reported (⚠️ — does not block, and neither is filled in here)
- [ ] For a plan showing signs of `run-exec-plan` completion: the `docode-review` verdict record was
      checked and any absence reported (⚠️ — does not block, and `docode-review` is not run here to
      fill the gap)
- [ ] If test files were changed, the reason is recorded in the decision log
- [ ] The progress log in exec-plan has been updated
- [ ] Output shows "PR creation status: ✅ No issues"
