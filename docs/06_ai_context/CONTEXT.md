# CONTEXT.md — FocusKeeper ナビゲーションマップ

> **更新ルール**: フェーズ移行・優先タスク変更のたびに更新する。1画面に収める。

---

## プロジェクト概要（3行）

FocusKeeperはPC画面上に現在の作業を常時オーバーレイ表示し、他の作業に目移りするのを防ぐWindowsデスクトップアプリです。
C# / .NET 8 / WPF で構築し、作業の入力・選択・設定ウィンドウを提供します。
ローカル完結型（SQLite、ネットワーク不要）、MSIX配布。

---

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語/FW | C# / .NET 8 / WPF |
| MVVMライブラリ | CommunityToolkit.Mvvm 8.x |
| DB | SQLite（Microsoft.Data.Sqlite） |
| DI | Microsoft.Extensions.DependencyInjection |
| ロギング | Serilog + Microsoft.Extensions.Logging |
| テスト | xUnit + Moq |
| 配布 | MSIX |

---

## 現在フェーズ・優先タスク

**フェーズ2: 要件定義・設計 → フェーズ3移行準備中**

優先タスク → [`exec-plans/active/2026-04-focus-keeper-initial.md`](../../exec-plans/active/2026-04-focus-keeper-initial.md)

---

## ドキュメント構成

| ディレクトリ | 内容 | 重要ファイル |
|------------|------|------------|
| `docs/00_project/` | 目的・用語・意思決定 | `overview.md`, `glossary.md`, `decisions.md` |
| `docs/01_requirements/` | 機能要件・非機能要件・ユーザーストーリー・制約 | `functional/windows.md`, `user_stories/windows.md` |
| `docs/02_design/` | アーキテクチャ・データモデル・UI遷移 | `architecture.md`, `data_model.md`, `ui_flows.md` |
| `docs/03_implementation/` | コーディング規約・構成・パターン・不変条件 | **`invariants.md`**（必読） |
| `docs/04_quality/` | テスト戦略・レビュー・セキュリティ | `test_strategy.md`, `review_checklist.md` |
| `docs/05_operations/` | 環境・デプロイ・監視 | `deployment.md` |
| `docs/06_ai_context/` | AIコンテキスト・プロンプト・スキル | `prompts/`, `skills/` |
| `exec-plans/active/` | 進行中の実行計画 | `2026-04-focus-keeper-initial.md` |

---

## 命名規則の大原則

- クラス・プロパティ・メソッド → PascalCase
- privateフィールド → `_camelCase`
- 非同期メソッド → `Async` サフィックス
- インターフェース → `I` プレフィックス
- 詳細 → [`docs/03_implementation/coding_standards.md`](../03_implementation/coding_standards.md)

---

## 最重要不変条件

```
依存方向: View → ViewModel → Service → Repository → Model（逆禁止）
async void: WPFイベントハンドラのみ許可
外部通信: 禁止
SQLパラメータ: 文字列結合SQL禁止
```

詳細 → [`docs/03_implementation/invariants.md`](../03_implementation/invariants.md)
