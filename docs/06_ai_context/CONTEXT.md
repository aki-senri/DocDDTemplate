---
updated: 2026-04-16
phase: 1
---

# CONTEXT.md — FileTagExplorer ナビゲーションマップ

## 今どこにいるか

**フェーズ 1 完了 → フェーズ 2 開始準備中**

Phase 0（プロジェクト初期化）および Phase 1（ナレッジベース構築）のドキュメントが揃い、
Phase 2（要件定義・設計）の詳細化を開始できる状態。

## プロジェクト概要（1行）

Windows 上で動作する C#/.NET 9 WPF デスクトップアプリ。開いたフォルダ内のファイルに
タグを付与し、タグを軸にした一括選択・移動などの整理操作を提供する。

## 現在の状態

| ドキュメント                        | 状態     | 備考                           |
|------------------------------------|----------|-------------------------------|
| docs/00_project/overview.md        | ✅ 完了  | 目的・技術スタック確定          |
| docs/00_project/decisions.md       | ✅ 完了  | ADR-001〜003 記録済み          |
| docs/00_project/glossary.md        | ✅ 完了  | 主要用語定義済み               |
| docs/01_requirements/constraints.md | ✅ 完了  | 制約・非対応事項確定           |
| docs/01_requirements/user_stories/ | ✅ 完了  | US-001〜003 作成済み           |
| docs/02_design/architecture.md     | ✅ 完了  | WPF MVVM 構成確定              |
| docs/02_design/data_model.md       | ✅ 完了  | TagStore / FileEntry / Tag 定義 |
| docs/03_implementation/invariants.md | ✅ 完了 | INV-001〜006 定義済み          |
| docs/03_implementation/patterns.md | ✅ 完了  | MVVM・Repository パターン記述  |

## 次のアクション

1. `exec-plans/active/001_initial_setup.md` の実行計画に従い実装開始
2. `/start-feature` でブランチ確認後、`src/` ディレクトリを作成してプロジェクト初期化
3. Phase 2 の `api_spec.md`（コマンド仕様）を必要に応じて補完

## 重要な決定事項（最新3件）

- **ADR-003**: タグデータは `.filetags` JSON ファイルとしてフォルダ直下に保存（外部DB不使用）
- **ADR-002**: UI フレームワークは WPF + CommunityToolkit.Mvvm を採用
- **ADR-001**: 管理スコープは「開いたフォルダ内のみ」に限定（再帰的サブフォルダ走査は非対応）

## 不変条件チェックポイント（実装開始前に確認）

- `invariants.md` の INV-001（タグデータの一貫性）を最初に実装・テストすること
- `.filetags` ファイルのスキーマ変更は data_model.md と同期すること
