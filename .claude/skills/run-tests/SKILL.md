---
name: run-tests
description: |
  Skill to run tests and verify results against the spec (AC-IDs).
  When tests fail, includes a decision gate to determine whether the test correctly expresses the spec before deciding on action.
  Also serves the red-first path: for a run where a failure is expected (the test was just written
  from an AC, before its implementation), it classifies the failure as a valid red (the AC's
  expectation did not hold) or an invalid red (it never ran), because only the former is evidence.
  Prohibits modifying tests to match implementation behavior.
  Can be called internally by pre-pr, start-feature, and complete-exec-plan, or run standalone.
# disable-model-invocation is intentionally false: running tests is a read-only, non-destructive
# verification action, and the autonomous driver (run-exec-plan) must invoke it reliably as a
# subroutine after each AC. Making it model-invocable lets the driver call it via the Skill tool
# (single source of truth, no inlined-step drift) and lets the model run tests when appropriate.
# The write-side verification skills (check-invariants / check-doc-freshness) stay true, because
# ambient auto-invocation of skills that modify code/docs would undermine the human governance gates.
disable-model-invocation: false
---

# Skill: Test Execution & Spec Verification

> **When to run**:
> - After code changes (at any time)
> - **Right after writing a test from an AC, before implementing it** (red-first — the run whose
>   expected outcome is a failure; see [`red-first.md`](red-first.md))
> - During baseline verification in the `start-feature` skill
> - Called from the `pre-pr` skill
> - During completion verification in the `complete-exec-plan` skill
>
> **Purpose**: Position tests as "executable expressions of the spec" and ensure the implementation satisfies the spec.
> Treat test failures as a "spec compliance verification gate" rather than an opportunity to modify tests.
>
> **Prerequisites**:
> - `docs/05_quality/test_strategy.md` must exist and have the `test_command` field set

---

## What this skill does

1. Read the test command from `test_strategy.md`
2. Run the tests
2b. If this is a **red-first run** (a failure is expected): classify valid vs. invalid red
3. If all pass: verify AC-ID coverage, checking functional and `[E2E]` ACs separately
4. If failures: determine the course of action through the **spec alignment gate**

---

## Steps

### Step 1: Read the test command

Load the frontmatter of `docs/05_quality/test_strategy.md`.

```yaml
---
test_command: dotnet test
test_command_fe: npm test        # if FE/BE are separate (optional)
test_command_be: dotnet test     # if FE/BE are separate (optional)
coverage_threshold: 80
---
```

- If neither `test_command` nor `test_command_fe/be` is defined:
  Guide the user to add `test_command` to `test_strategy.md` and stop.

### Step 2: Run tests

Execute commands according to the frontmatter.

- If both `test_command_fe` and `test_command_be` are present, run both
- Record the results (pass/fail, count, names of failed tests)

### Step 2b: Red-first run — classify the failure

A **red-first run** is one where a failure is the expected outcome: the caller has just written a
test from an AC, before the implementation that satisfies it exists
(`run-exec-plan` Step 0c / Step 2a, or a human doing the same by hand).
The caller says so when invoking this skill; when nobody says so, this step does not apply.

In such a run, "it failed" is not yet evidence. Classify it per
[`red-first.md`](red-first.md) — follow that file; do not re-derive the criteria here:

| Result | Report | Meaning for the caller |
|--------|--------|------------------------|
| **Valid red** — the assertion about the AC's expected result did not hold | `✅ valid red` with `expected` / `actual` | The test measures the AC. Proceed to implement |
| **Invalid red** — compile error, unresolved symbol, harness/setup failure, wrong command | `❌ invalid red` with the failing phase | The test measured nothing. **Do not report this as "expected"** and do not let the caller proceed to implementation |
| **Green** — the test passed on its first run | `⚠️ green on first run` | Either the AC is already satisfied or the test does not assert it. The caller decides which; this skill does not weaken the test to make it red |

Report the `expected` / `actual` pair verbatim — the caller writes it into the plan's Decision Log,
where it becomes the frozen expectation.

The spec alignment gate (Step 4) does **not** apply to a red-first run: there is no implementation
yet, so "the implementation has a bug" and "the spec changed" are both meaningless. It applies from
the moment the AC's implementation exists.

### Step 3: If all pass — AC coverage check

If all tests pass, verify AC-ID coverage.

1. Load execution plans in `exec-plans/active/` and list the AC-XXX items in `## Acceptance Criteria`
2. Split them into **functional ACs** and **E2E ACs** — an E2E AC is one whose description starts
   with the `[E2E]` marker (`- [ ] AC-005: [E2E] ...`)
3. Read test files and verify that a test exists for each AC-ID, and report the two groups separately

```
Acceptance criteria coverage:
  ✅ AC-001 → AuthServiceTest: Login_WithInvalidPassword_Returns401
  ✅ AC-002 → AuthServiceTest: Session_Expired_RequiresReauth
  ❌ AC-003 → No test created

E2E acceptance criteria coverage:
  ✅ AC-005 [E2E] → LoginJourneyE2ETest: SignIn_To_Dashboard_EndToEnd  (green)
  ❌ AC-006 [E2E] → No test created
```

- If any AC-IDs are uncovered, issue a warning and prompt to create tests
- If called from `pre-pr` or `complete-exec-plan`, put processing on hold if there are uncovered AC-IDs

E2E acceptance criteria are checked separately, because a per-AC coverage check cannot see the
failure mode they exist for: every functional AC green while the through-flow does not work. So
for each `[E2E]` AC verify **both** that a test exists **and** that it is among the tests that
just passed — an E2E AC with no test, or with a test that did not actually run, is uncovered.

**Two different situations, two different outcomes.** Keep them apart:

| Situation | Outcome |
|-----------|---------|
| The plan **has** a `[E2E]` AC, but its test is missing, or did not run, or failed | ❌ **hold** — same weight as a failing test |
| The plan has **no** `[E2E]` AC at all | ⚠️ **report only, do not hold** |

The second case is a warning rather than a hold because it has legitimate causes: the plan predates
the E2E requirement, or it is documentation-only (see `create-exec-plan`). Report it as
`⚠️ このプランに [E2E] AC がありません` and direct the user to `create-exec-plan` — **do not invent
the criterion here.** Deciding what to build is an outer gate.

When called from `pre-pr` or `complete-exec-plan`, an uncovered `[E2E]` AC puts processing on hold
in the same way an uncovered functional AC does; a missing `[E2E]` AC does not.

### Step 4: If failures — spec alignment gate

**When tests fail, always go through this gate before modifying tests or implementation.**
(Except in a red-first run — see Step 2b. There the failure is the expected result, and the
answer is always "implement".)

For each failed test, present the following information.

```
❌ Test failure: AuthServiceTest.Login_WithInvalidPassword_Returns401

  Corresponding spec:
    AC-001 (exec-plans/active/{plan-name}.md)
    "Login with an invalid password should return 401"

  Test details:
    Expected: StatusCode = 401
    Actual:   StatusCode = 500

  ─────────────────────────────────────────
  Please decide:

    A) The test correctly expresses the spec
       → There is a bug in the implementation. Please fix the implementation.

    B) The spec has changed and the test is outdated
       → Confirm the content of the spec (AC-001) and modify the test based on the spec.
       ⚠️  Modifying tests to match implementation behavior is prohibited.
           Always ground test modifications in a spec document (AC-ID).
       ⚠️  If this test's expectation was frozen by a red-first observation
           (a `AC-NNN red-first:` entry in the plan's Decision Log), option B requires
           a spec change — not a second look at the same spec (INV-T02).
  ─────────────────────────────────────────
```

**If A is chosen:**
- Prompt to fix the implementation and stop
- Do not change the tests

**If B is chosen:**
1. Identify the spec document (the exec-plan containing the AC-ID) to be changed
2. Confirm the spec has actually changed
3. Record the reason for the change in the exec-plan's `## Decision Log`
4. Modify the test based on the spec
5. Re-run the tests and return to Step 3

---

## AC-ID tagging convention

Tag tests with AC-IDs to track the correspondence between tests and specs.
(Project-specific conventions are recorded in `test_strategy.md`)

**C# / xUnit:**
```csharp
[Fact]
[Trait("AC", "AC-001")]
public void Login_WithInvalidPassword_Returns401() { ... }
```

**TypeScript / Vitest:**
```typescript
describe('AC-001: Login with invalid password', () => {
  it('returns 401', () => { ... });
});
```

---

## Result report format

```
=== Test execution results ===

Command  : {test_command}
Result   : ✅ All {n} tests passed / ❌ {n} test(s) failed

[Red-first]  (only for a red-first run — omit otherwise)
✅ valid red   AC-003 → {test name}  expected: {…}  actual: {…}
❌ invalid red AC-004 → {test name}  ({compile error | setup failure} — measured nothing)
⚠️ green on first run AC-005 → {test name}

[AC Coverage]
✅ AC-001 → Test exists
✅ AC-002 → Test exists
❌ AC-003 → No test created

[E2E AC Coverage]
✅ AC-005 [E2E] → Test exists and passed
❌ AC-006 [E2E] → No test created  (hold)
(or: ⚠️ このプランに [E2E] AC がありません — create-exec-plan で追加してください)

---
Overall: ✅ No issues / ❌ Please review the spec alignment gate
```

---

## Completion criteria

- [ ] Test command was run
- [ ] If this was a red-first run: each failure was classified as valid red / invalid red / green on
      first run per [`red-first.md`](red-first.md), and an invalid red was **not** reported as
      expected
- [ ] If all passed: AC-ID coverage was verified, functional and `[E2E]` ACs reported separately
- [ ] Every `[E2E]` AC has a test that exists **and** passed — otherwise processing is on hold
      (or the absence of any `[E2E]` AC in the plan was reported)
- [ ] If failures: determined "fix implementation" or "fix test based on spec" through the spec alignment gate
- [ ] Output the result report
