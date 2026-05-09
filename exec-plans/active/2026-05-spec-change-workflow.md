---
status: active
created: 2026-05-09
completed:
---

# spec-change-workflow

## Goal & Scope

仕様変更フローを整備する。
実装前・実装済みの2ケースを明確に区別し、spec-gate の誤検知修正・CLAUDE.md への運用ガイド追記・`/amend-spec` スキル追加を行う。

## Acceptance Criteria

- [ ] AC-001: spec-gate.py の false positive を修正する（`実装前`・`実装済`・`実装方針`・`実装仕様`・`実装計画` が誤検知されない）
- [ ] AC-002: CLAUDE.md に実装前/実装済みの仕様変更フローを追記する
- [ ] AC-003: `/amend-spec` スキルを追加する（実装済み仕様の変更用）
- [ ] AC-004: SKILL_FLOW.md に仕様変更フローを追記する

## Task Breakdown

- [ ] spec-gate.py の IMPL_PATTERNS を否定先読みで修正
- [ ] CLAUDE.md のスキル一覧と手順に仕様変更フローを追記
- [ ] `.claude/skills/amend-spec/SKILL.md` を作成
- [ ] SKILL_FLOW.md のフロー図と Gap List を更新

## Progress Log

### 2026-05-09
- Plan created

## Decision Log

- 実装前の仕様変更はスキル不要（直接編集 + Decision Log 記録）と決定。コードがないため乖離リスクがゼロ。
- 実装済みの仕様変更は `/amend-spec` スキルで対応。check-doc-freshness による乖離確認が必要なため。
