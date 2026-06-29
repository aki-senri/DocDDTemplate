---
name: check-invariants
description: |
  Skill to verify the invariants defined in docs/04_implementation/invariants.md against implementation code.
  Can be called internally by the pre-pr skill, or used standalone during implementation.
disable-model-invocation: true
---

# Skill: Invariant Check

> **When to run**:
> - When implementation is complete (called automatically from the `pre-pr` skill)
> - At any time during implementation when you want to verify
> - During full-scan mode from the `gc` skill
>
> **Purpose**: Detect violations of the invariants defined in `invariants.md` before CI, reducing the cost of fixing issues.
>
> **Prerequisites**: `docs/04_implementation/invariants.md` must exist (Phase 1 must be complete)

---

## What this skill does

1. Load `invariants.md` and understand the conditions to apply
2. Check the conditions against the changed code files
3. Report violations and provide fix instructions

---

## Steps

### Step 1: Load invariants.md

Load `docs/04_implementation/invariants.md` and understand all INV conditions.

Each INV is defined in the following format (contents vary by project architecture and language):

```markdown
| # | Condition | On violation |
|---|-----------|-------------|
| INV-001 | {Layer dependency direction rule} | Build error |
| INV-002 | {File size limit} | Warning |
| INV-003 | {Naming convention} | Build warning |
```

Set check priority based on the severity of "On violation":
- `Build error` → must be fixed
- `Warning` → strongly recommended to fix
- `Review comment` → decide based on context

### Step 2: Collect changed files

| Caller | Target files |
|--------|-------------|
| Called from `pre-pr` | List changed files via `git diff --name-only main...HEAD` |
| Standalone execution | Ask the user: "Please provide the file or directory to check" |
| Called from `gc` | Target all code files under `src/**` |

### Step 3: Verify conditions

Load each INV in `invariants.md` and verify the changed files based on its contents.
**INV contents differ per project**, so the following are examples of check techniques only.

**Checking dependency direction:**
- Load `import` / `require` / `using` statements (or the dependency declaration syntax for the language) from each file and verify no dependencies go in the direction prohibited by the INV
- Example: Does the UI layer directly reference the data access layer?

**Checking file size:**
- Count the lines in each file and verify they do not exceed the limit defined in the INV

**Checking naming conventions:**
- Verify that names follow the patterns defined in the INV (e.g., `_camelCase`, `PascalCase`, `kebab-case`, etc.)

**Checking language/framework-specific forbidden patterns:**
- Verify that forbidden patterns listed in the INV (e.g., misuse of specific APIs, restrictions on side-effect-producing functions) are not present

**Other:**
- Use each INV's stated conditions directly as the verification criteria

### Step 4: Generate fix instructions

If violations are found, report them in the following format.

```
❌ INV-001 violation: {file path}
   Details: {what violates which rule}
   Fix: {specific fix instructions}
   Reference: docs/04_implementation/patterns.md §{related section}
```

---

## Result report format

```
=== Invariant check results ===

INVs checked: {count}
Files checked: {count}

✅ No issues: {count}
❌ Violations (build error level): {count}
  {violation details and fix instructions}
⚠️ Warnings (fix recommended): {count}
  {warning details and fix instructions}

---
Overall: ✅ All passed / ❌ Fixes required
```

---

## Completion criteria

- [ ] Loaded `invariants.md`
- [ ] Checked changed files against all INVs
- [ ] Provided fix instructions for all violations
- [ ] Output the result report
