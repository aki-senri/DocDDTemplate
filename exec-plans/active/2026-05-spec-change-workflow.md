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
- AC-001〜AC-004 の初回実装完了・push

### 2026-05-09（レビュー対応）
- サブエージェントによる独立レビューを実施
- レビュー指摘のうち以下3件を修正（定期スクリーニングで吸収不可な欠陥を優先）
  1. spec-gate.py 第3パターン（`機能.{0,10}(追加|作成|実装)`）に否定先読みを追加
  2. amend-spec Q5 を削除・Step 2 を常時実行に変更
  3. Decision Log 書き先フォールバックを amend-spec SKILL.md と CLAUDE.md に追記

## Decision Log

- 実装前の仕様変更はスキル不要（直接編集 + Decision Log 記録）と決定。コードがないため乖離リスクがゼロ。
- 実装済みの仕様変更は `/amend-spec` スキルで対応。check-doc-freshness による乖離確認が必要なため。
- レビュー指摘のうち constraints.md・US 削除・複数 AC 同時変更・hook による変更検知（D1/D2/D4/D5）は、定期スクリーニング（/gc）で吸収できると判断し対応しないことを決定。
