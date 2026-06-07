---
name: check-doc-invariants
description: |
  Checks structural invariants of documents in docs/**/*.md and exec-plans/.
  Verifies reference directions, frontmatter completeness, lifecycle consistency,
  and AC traceability. Called from pre-pr and gc, or run standalone.
disable-model-invocation: true
---

# Skill: Document Invariant Check

> **When to run**:
> - Before creating a PR (called from `pre-pr`)
> - During weekly GC (called from `gc`)
> - After writing or updating documents
>
> **Purpose**: Detect structural violations in documentation — broken reference directions,
> incomplete frontmatter, lifecycle inconsistencies, and AC traceability gaps — before they
> accumulate into hard-to-trace drift.
>
> **Prerequisites**: `docs/` directory must exist (Phase 1 must be complete)

---

## What this skill does

1. Collect all `docs/**/*.md` and `exec-plans/**/*.md`
2. Parse frontmatter and extract cross-links from each file
3. Check each document against the five built-in invariants below
4. Report violations with fix instructions

---

## Built-in invariants

### DOC-INV-001: Reference direction

Documents must not reference documents at a more concrete abstraction layer.

| Layer | Path | May reference |
|-------|------|---------------|
| 1 – Requirements | `docs/01_requirements/` | External resources, `constraints.md` within layer 1 |
| 1.5 – Exec-plans | `exec-plans/` | `docs/01_requirements/` (US files) only |
| 2 – Design | `docs/02_design/` | Layer 1 and below |
| 3 – Implementation | `docs/03_implementation/` | Layers 1–2 and below |
| 4 – Quality | `docs/04_quality/` | All `docs/` layers |

**Violation example**: A `docs/01_requirements/` file links to `docs/02_design/api_spec.md`.

**Note**: Links going upward in abstraction (e.g., implementation doc referencing a requirement)
are valid forward references — only downward references (requirements referencing implementation) are violations.

---

### DOC-INV-002: Frontmatter completeness

Every `docs/**/*.md` must have:
- `status:` — one of `draft`, `active`, `deprecated`

Documents in `docs/02_design/` and `docs/03_implementation/` that correspond to code must have:
- `tracks:` — glob pattern(s) pointing to the tracked source files

Every `docs/01_requirements/user_stories/US-*.md` must also have:
- `ac_ids:` — non-empty list of AC identifiers defined in the document body

---

### DOC-INV-003: Lifecycle consistency

- `active` documents must not link to `deprecated` documents
- If a link target has `status: deprecated`, flag it as a violation and suggest updating to the successor document (if known)

---

### DOC-INV-004: AC traceability

For each `exec-plans/active/*.md`:
- Every `AC-NNN` line must correspond to a US file whose `ac_ids:` contains that identifier

For each `docs/01_requirements/user_stories/US-*.md`:
- Every AC-ID in `ac_ids:` should appear in at least one exec-plan (warn if none found — it may simply not have been planned yet)

---

### DOC-INV-005: Diagram rules (CLAUDE.md compliance)

- ASCII art blocks (lines containing `┌`, `│`, `└`, `├`, `┤`, `┬`, `┴`, `┼`, or `+--+` patterns)
  must be followed within 3 lines by a non-empty plain-text explanation paragraph
- Flow / sequence / class diagrams expressed as ASCII art are a violation when they could be
  expressed as Mermaid (warn level — use context to judge)

*Violation level*: Warning (non-blocking)

---

## Steps

### Step 1: Collect all documents

```bash
find docs -name "*.md" 2>/dev/null | sort
find exec-plans -name "*.md" 2>/dev/null | sort
```

For each file:
- Parse the YAML frontmatter (content between the first pair of `---` delimiters)
- Extract all Markdown links: `[text](path)` patterns
- Note the file's layer number based on its path prefix

### Step 2: Check DOC-INV-001 (Reference direction)

Assign layer numbers:

| Prefix | Layer |
|--------|-------|
| `docs/01_requirements/` | 1 |
| `exec-plans/` | 1.5 |
| `docs/02_design/` | 2 |
| `docs/03_implementation/` | 3 |
| `docs/03_implementation/invariants.md` | 3 |
| `docs/04_quality/` | 4 |
| `docs/05_*/` and `docs/06_*/` | 5+ |

For each link `[text](target)` in a document at layer N:
- Resolve `target` relative to the repository root
- Determine target layer M
- If M > N → violation (higher-layer document referencing a lower-layer document)

Skip external URLs (starting with `http://` or `https://`).

### Step 3: Check DOC-INV-002 (Frontmatter completeness)

For each `docs/**/*.md`:
1. Check `status:` exists and is `draft`, `active`, or `deprecated`
2. For `docs/02_design/` and `docs/03_implementation/` files: check `tracks:` key exists
3. For `docs/01_requirements/user_stories/US-*.md`: check `ac_ids:` exists and is a non-empty list

### Step 4: Check DOC-INV-003 (Lifecycle consistency)

1. Build a map: file path → `status:` value
2. For each `active` document, scan its links
3. For each linked path, look up its status in the map
4. Flag any link from an `active` document to a `deprecated` target

### Step 5: Check DOC-INV-004 (AC traceability)

1. Collect exec-plan AC-IDs: scan `exec-plans/active/*.md` for lines matching
   `- \[[ x]\] AC-\d+:` and extract the identifiers
2. Collect US AC mappings: from each `docs/01_requirements/user_stories/US-*.md`,
   read `ac_ids:` frontmatter
3. Cross-check:
   - For each exec-plan AC-ID: is it present in any US's `ac_ids:`? If not → violation
   - For each US `ac_ids:` entry: is it present in any exec-plan? If not → warning

### Step 6: Check DOC-INV-005 (Diagram rules)

For each `docs/**/*.md` and `exec-plans/**/*.md`:
1. Find ASCII art blocks: consecutive lines starting with box-drawing characters or `+--`
2. Check that within 3 lines after the block ends, a non-empty paragraph exists
3. If not → warning

---

## Result report format

```
=== Document invariant check results ===

Documents checked : {count}
Exec-plans checked: {count}

❌ DOC-INV-001 violations (reference direction): {count}
  - docs/01_requirements/user_stories/US-001_foo.md → docs/02_design/api_spec.md (line 12)
    Fix: Remove or replace the forward reference with a plain description

❌ DOC-INV-002 violations (frontmatter): {count}
  - docs/02_design/data_model.md: missing tracks:
    Fix: Add tracks: field pointing to relevant source files

❌ DOC-INV-003 violations (lifecycle): {count}
  - docs/02_design/api_spec.md (active) → docs/02_design/old_api.md (deprecated) at line 34
    Fix: Update the link to the successor document, or remove the reference

❌ DOC-INV-004 violations (AC traceability): {count}
  - AC-003 in exec-plans/active/2026-01-feature.md has no matching US ac_ids:
    Fix: Add AC-003 to the corresponding US file's ac_ids: frontmatter

⚠️ DOC-INV-005 warnings (diagram rules): {count}
  - docs/02_design/screen_layout.md: ASCII art at line 42 has no following description
    Fix: Add a plain-text explanation paragraph immediately after the diagram

---
Overall: ✅ All passed / ❌ {count} violation(s) / ⚠️ {count} warning(s)
```

---

## Completion criteria

- [ ] All `docs/**/*.md` and `exec-plans/**/*.md` collected
- [ ] DOC-INV-001 through DOC-INV-005 checked
- [ ] All violations reported with specific file paths, line numbers, and fix instructions
- [ ] Result report output
