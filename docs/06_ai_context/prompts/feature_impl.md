# プロンプトテンプレート：機能実装依頼

> このテンプレートをコピーして使用してください。`{{}}` の部分を埋めてください。

---

```
## コンテキスト

プロジェクト: FocusKeeper（Windows デスクトップアプリ、C# / .NET 8 / WPF）
参照ドキュメント:
- docs/06_ai_context/CONTEXT.md（ナビゲーションマップ）
- docs/03_implementation/invariants.md（不変条件・必読）
- docs/03_implementation/coding_standards.md（命名規則）
- docs/03_implementation/directory_structure.md（ファイル配置）

## 実装依頼

### 対象ユーザーストーリー
{{US-Wxx: ユーザーストーリーのタイトルと概要}}

### 受け入れ条件
{{docs/01_requirements/user_stories/windows.md から該当箇所をコピー}}

### 実装対象ファイル（予想）
{{変更・作成が必要なファイルパスの一覧}}

### 追加の制約・注意事項
{{ある場合のみ記入}}

## 期待する成果物

1. 実装コード（上記ファイルの変更/追加）
2. 対応するユニットテスト
3. 必要な場合はドキュメント更新（data_model.md 等）

## 禁止事項

- invariants.md の不変条件に違反しないこと
- ViewModel から Repository を直接参照しないこと
- async void を使用しないこと（WPFイベントハンドラ除く）
- 外部ネットワーク通信を含めないこと
```
