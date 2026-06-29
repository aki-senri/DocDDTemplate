---
name: check-doc-freshness
description: |
  Skill to check the freshness of documents corresponding to changed code files.
  Reads the tracks: field in docs/**/*.md frontmatter, identifies documents that have diverged from the changed code, and updates them.
  Can be called internally by the pre-pr skill, or run standalone.
disable-model-invocation: true
---

# Skill: Document Freshness Check

> **When to run**:
> - After code changes (called automatically from the `pre-pr` skill)
> - When you want to verify a specific file change on its own
> - During full-scan mode from the `gc` skill (targets all files)
>
> **Purpose**: Detect divergence between code and documentation early, and prevent documentation from becoming stale.
>
> **Prerequisites**: Each document's frontmatter must have a `tracks:` field set (see the "Document structure" section of the `init-project` skill)

---

## What this skill does

1. Collect the paths of changed code files
2. Match against the `tracks:` fields in `docs/**/*.md`
3. Identify documents that have diverged
4. Flag and fix sections that need updating

---

## Steps

### Step 1: Collect changed files

The target varies depending on the caller.

| Caller | Target files |
|--------|-------------|
| Called from `pre-pr` | List changed files via `git diff --name-only main...HEAD` (or branch diff) |
| Standalone execution | Ask the user: "Please provide the file path(s) to check" |
| Called from `gc` | Target all code files in the repository |

### Step 2: Match against `tracks:` fields

Read `docs/**/*.md` one by one and check the `tracks:` field in the frontmatter.

```yaml
---
status: active
tracks:
  - src/**/models/**        # example: path depends on language and structure
  - src/**/repositories/**
---
```

> The path patterns in `tracks:` vary by project language and directory structure.
> Configuration examples (by language):
> - C#: `src/**/Models/*.cs`, `src/**/Services/*.cs`
> - TypeScript: `src/**/types/*.ts`, `src/**/api/*.ts`
> - Python: `src/**/models/*.py`, `src/**/repositories/*.py`
> - Go: `internal/**/domain/*.go`, `internal/**/repository/*.go`

- Skip documents without `tracks:`
- Use glob matching for `tracks:` patterns against changed files (`*` = one level, `**` = multiple levels)
- Add matched documents to the "needs review" list

### Step 3: Check for divergence

Read each document in the "needs review" list one by one and check for divergence from the following angles.

| Document type | Check points |
|---------------|-------------|
| `data_model.md` | Are Model class additions/changes reflected in the ERD and descriptions? |
| `api_spec.md` | Are endpoint additions, changes, and deletions reflected in the document? |
| `directory_structure.md` | Is the placement of new directories/files described? |
| `patterns.md` | If a new pattern or convention was introduced, is it recorded? |
| `dependencies.md` | Are new libraries and version changes reflected? |
| `coding_standards.md` | Are convention additions/changes reflected? |
| `invariants.md` | Have any new invariants been added or changed? |

### Step 4: Apply updates

Update any documents where divergence was found.

1. Review the changes and identify the relevant sections of the document
2. Determine the update content and edit the document
3. Check that the `status:` in the frontmatter is not `deprecated` (if it is, record the content in the successor document instead)

---

## Result report format

```
=== Document freshness check results ===

Code files checked: {count}
Documents matched: {count}

✅ No issues: {count}
⚠️ Updates needed (addressed): {count}
  - docs/03_design/data_model.md: Added Model.Xxx
  - ...
❌ Not addressed (manual review needed): {count}
  - docs/xxx/yyy.md: {reason}

---
Overall: ✅ No issues / ⚠️ Updated / ❌ Manual action required
```

---

## Completion criteria

- [ ] Listed all changed code files
- [ ] Matched against all `tracks:` fields
- [ ] Updated all diverged documents (or explained N/A reason)
- [ ] Output the result report
