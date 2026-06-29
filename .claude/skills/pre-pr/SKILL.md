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
⑤ run-tests             → Run tests and verify against spec
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
   DOC-INV-005 (diagram rules)
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
3. If there are changes to test files, confirm the changes are grounded in a spec (AC-ID)

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

---

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
⑥ exec-plan        : ✅ Progress updated

---
{If there are issues, list specific fix instructions here}
---

PR creation status: ✅ No issues / ❌ Fix the above and re-run
```

---

## Completion criteria

- [ ] All checks ① through ⑥ are complete
- [ ] All issues have been fixed, or documented as "N/A" with explanation
- [ ] If tests failed, they were resolved through the spec alignment gate
- [ ] If test files were changed, the reason is recorded in the decision log
- [ ] The progress log in exec-plan has been updated
- [ ] Output shows "PR creation status: ✅ No issues"
