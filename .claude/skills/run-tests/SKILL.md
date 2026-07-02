---
name: run-tests
description: |
  Skill to run tests and verify results against the spec (AC-IDs).
  When tests fail, includes a decision gate to determine whether the test correctly expresses the spec before deciding on action.
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
3. If all pass: verify AC-ID coverage
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

### Step 3: If all pass — AC coverage check

If all tests pass, verify AC-ID coverage.

1. Load execution plans in `exec-plans/active/` and list the AC-XXX items in `## Acceptance Criteria`
2. Read test files and verify that a test exists for each AC-ID

```
Acceptance criteria coverage:
  ✅ AC-001 → AuthServiceTest: Login_WithInvalidPassword_Returns401
  ✅ AC-002 → AuthServiceTest: Session_Expired_RequiresReauth
  ❌ AC-003 → No test created
```

- If any AC-IDs are uncovered, issue a warning and prompt to create tests
- If called from `pre-pr` or `complete-exec-plan`, put processing on hold if there are uncovered AC-IDs

### Step 4: If failures — spec alignment gate

**When tests fail, always go through this gate before modifying tests or implementation.**

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

[AC Coverage]
✅ AC-001 → Test exists
✅ AC-002 → Test exists
❌ AC-003 → No test created

---
Overall: ✅ No issues / ❌ Please review the spec alignment gate
```

---

## Completion criteria

- [ ] Test command was run
- [ ] If all passed: AC-ID coverage was verified
- [ ] If failures: determined "fix implementation" or "fix test based on spec" through the spec alignment gate
- [ ] Output the result report
