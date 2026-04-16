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

Windows 上で動作する C#/.NET 9 WPF デスクトップアプリ。開いたフォルダとその下位階層全体を
管理対象とし、ファイルにタグを付与してタグを軸にした一括選択・任意フォルダへの移動などの
整理操作を提供する。

## 現在の状態

| ドキュメント                        | 状態     | 備考                                        |
|------------------------------------|----------|---------------------------------------------|
| docs/00_project/overview.md        | ✅ 完了  | 目的・技術スタック確定（再帰走査対応済み）    |
| docs/00_project/decisions.md       | ✅ 完了  | ADR-001〜004 記録済み（ADR-001/004 改訂済み）|
| docs/00_project/glossary.md        | ✅ 完了  | 主要用語定義済み                             |
| docs/01_requirements/constraints.md | ✅ 完了  | 制約・非対応事項確定                         |
| docs/01_requirements/user_stories/ | ✅ 完了  | US-001〜003 作成済み（再帰走査・任意移動対応）|
| docs/02_design/architecture.md     | ✅ 完了  | WPF MVVM 構成確定（FolderNode / AsyncLoad）  |
| docs/02_design/data_model.md       | ✅ 完了  | TagStore / FileEntry / FolderNode 定義済み   |
| docs/03_implementation/invariants.md | ✅ 完了 | INV-001〜007 定義済み（INV-007 移動引き継ぎ）|
| docs/03_implementation/patterns.md | ✅ 完了  | MVVM・Repository パターン記述               |

## 次のアクション

1. `exec-plans/active/001_initial_project_setup.md` の実行計画を再帰走査対応に更新
2. `/start-feature` でブランチ確認後、`src/` ディレクトリを作成してプロジェクト初期化
3. `IFileSystemService.GetFilesAsync` を `IAsyncEnumerable` で実装（非同期再帰走査）

## 重要な決定事項（最新3件）

- **ADR-004（改訂）**: 移動先は開いたフォルダ配下の任意フォルダ（ルート直下のみから変更）
- **ADR-001（改訂）**: 管理スコープは「開いたフォルダの下位階層全体」（直下のみから変更）
- **ADR-003**: タグデータは `.filetags` JSON（相対パスをキー使用）、フォルダルートに1ファイル

## 不変条件チェックポイント（実装開始前に確認）

- `invariants.md` の INV-003（ファイルは配下のみ）を `GetFilesAsync` 実装時に確認
- INV-007（移動後にタグ引き継ぎ）は `MoveFiles` と `UpdateFileKey` 実装時に確認
- `.filetags` のキーは相対パス（`/` 区切り）で正規化すること（data_model.md 参照）
