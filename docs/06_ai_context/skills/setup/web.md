# セットアップスキル: Web アプリ（React / ASP.NET Core / .NET 8）

> **実行タイミング**: `init-project.md` 実行後、Phase 1 開始時に実行する
>
> **目的**: このスキルを実行することで、React フロントエンド + ASP.NET Core バックエンドの
> 構成・設計・開発手順がドキュメントとして確定し、
> チームメンバーとAIエージェントが同じ前提で開発を進められる状態になる。

---

## 確定事項（このスキルが定める標準）

以下はプロジェクト固有の事情がない限り変更しない。
変更する場合は `docs/00_project/decisions.md` に理由を記録すること。

### 技術スタック

#### フロントエンド（FE）

| 項目 | 採用技術 | 理由 |
|------|---------|------|
| 言語 | TypeScript 5.x | 型安全性、IDEサポート |
| UI ライブラリ | React 18.x | エコシステムの成熟度 |
| ビルドツール | Vite 5.x | 高速な開発サーバー・ビルド |
| ルーティング | React Router v6 | React の標準ルーティング |
| サーバー状態管理 | TanStack Query 5.x | API データの取得・キャッシュ・同期 |
| スタイリング | CSS Modules | スコープ付き CSS、ビルドツール不要 |
| コード品質 | ESLint + Prettier | 静的解析・フォーマット統一 |
| テスト | Vitest + React Testing Library | Vite との統合、軽量 |

#### バックエンド（BE）

| 項目 | 採用技術 | 理由 |
|------|---------|------|
| 言語 | C# 12 | .NET 8 のデフォルト |
| ランタイム | .NET 8 | LTS、2026年11月まで標準サポート |
| フレームワーク | ASP.NET Core 8 Web API | .NET 標準の REST API フレームワーク |
| ORM | Entity Framework Core 8 | LINQ によるタイプセーフなクエリ |
| DB | PostgreSQL 15 | Web アプリの標準。スケーラビリティ |
| API 仕様 | OpenAPI（Swagger / Swashbuckle） | FE との契約として自動生成 |
| 認証 | ASP.NET Core Identity + JWT | 標準認証基盤 |
| ロギング | Serilog 3.x | 構造化ログ |
| テスト | xUnit 2.x + Moq 4.x | .NET 標準テストスタック |

#### インフラ

| 項目 | 採用技術 |
|------|---------|
| CI | GitHub Actions |
| FE デプロイ | 静的ホスティング（Vercel / Azure Static Web Apps） |
| BE デプロイ | コンテナ（Docker + Azure App Service / Cloud Run） |

### アーキテクチャ

#### 全体構成

```
[ブラウザ]
    │ HTTPS / JSON
    ▼
[React SPA]  ─── TanStack Query ───► [ASP.NET Core Web API]
                                              │
                                     Controller → Service → Repository
                                              │
                                        [PostgreSQL]
```

#### FE アーキテクチャ：Feature ベース構成

関連するコンポーネント・フック・型をひとつの機能単位（Feature）にまとめる。
共通コンポーネントのみ `shared/` に置く。

```
src/
├── features/           # 機能単位で分割
│   └── {featureName}/
│       ├── components/ # その機能専用のコンポーネント
│       ├── hooks/      # その機能専用のフック
│       ├── api/        # TanStack Query のクエリ定義
│       └── types.ts    # その機能の型定義
├── shared/
│   ├── components/     # 汎用UIコンポーネント
│   ├── hooks/          # 汎用フック
│   └── types/          # 共通型定義
├── pages/              # ルートに対応するページコンポーネント
└── lib/                # 設定・ユーティリティ
```

#### BE アーキテクチャ：レイヤードアーキテクチャ

依存の方向は一方向のみ。FE との契約は OpenAPI 仕様で管理する。

```
Controller → Service → Repository → Model（Entity）
```

| レイヤー | 責務 | 置き場所 |
|---------|------|---------|
| Controller | HTTP リクエスト受付・レスポンス返却のみ | `Controllers/` |
| Service | ビジネスロジック | `Services/` |
| Repository | DB アクセスの抽象化（EF Core） | `Repositories/` |
| Model | DB エンティティ・DTO | `Models/` |

### ディレクトリ構成

モノレポ構成。FE と BE を同一リポジトリで管理する。

```
{APP_NAME}/
├── frontend/                         # React アプリ
│   ├── src/
│   │   ├── features/
│   │   ├── shared/
│   │   ├── pages/
│   │   ├── lib/
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                          # ASP.NET Core Web API
│   ├── {APP_NAME}.Api/
│   │   ├── Controllers/
│   │   ├── Services/
│   │   │   └── Interfaces/
│   │   ├── Repositories/
│   │   │   └── Interfaces/
│   │   ├── Models/
│   │   │   ├── Entities/             # DB エンティティ
│   │   │   └── DTOs/                 # リクエスト・レスポンス型
│   │   ├── Infrastructure/           # DI・EF Core 設定・ロギング
│   │   └── Program.cs                # DI 構築・ミドルウェア設定
│   └── {APP_NAME}.Api.Tests/
│       ├── Services/
│       ├── Controllers/
│       └── Repositories/
│
└── .github/
    └── workflows/
        ├── ci-frontend.yml
        └── ci-backend.yml
```

### 主要な不変条件

#### FE

| # | 条件 |
|---|------|
| INV-FE-001 | Feature 間の直接インポート禁止（`features/A` が `features/B` を参照しない） |
| INV-FE-002 | API 通信はすべて `features/{name}/api/` の TanStack Query フック経由 |
| INV-FE-003 | コンポーネントは props の型定義を必ず持つ（`any` 禁止） |
| INV-FE-004 | ページコンポーネントにロジックを書かない（フック・コンポーネントに切り出す） |

#### BE

| # | 条件 |
|---|------|
| INV-BE-001 | Controller → Service → Repository の依存方向のみ許可 |
| INV-BE-002 | Controller はロジックを持たず Service に委譲する |
| INV-BE-003 | Service は Repository インターフェースに依存する（実装クラスに直接依存しない） |
| INV-BE-004 | 入力バリデーションは Controller 入口（FluentValidation または DataAnnotations）で行う |
| INV-BE-005 | `async void` は禁止。すべて `async Task` または `async Task<T>` |
| INV-BE-006 | DB エンティティを Controller のレスポンスとして直接返さない（必ず DTO に変換） |

### コーディング規約の要点

```typescript
// FE: コンポーネントは Props 型を定義する
type TaskCardProps = {
  title: string;
  onComplete: () => void;
};
export function TaskCard({ title, onComplete }: TaskCardProps) { ... }

// FE: API フックは TanStack Query で定義する
export function useTaskList() {
  return useQuery({ queryKey: ['tasks'], queryFn: fetchTasks });
}
```

```csharp
// BE: Controller はロジックなし
[HttpGet]
public async Task<IActionResult> GetAll(CancellationToken ct)
    => Ok(await _taskService.GetAllAsync(ct));

// BE: private フィールドは _camelCase
private readonly ITaskService _taskService;

// BE: 非同期メソッドは Async サフィックス
public async Task<IEnumerable<TaskDto>> GetAllAsync(CancellationToken ct = default)
```

---

## インタビュー（プロジェクト固有）

エージェントは以下のみ確認する。技術スタックは確定事項のため聞かない。

| # | 質問 | 使用先 |
|---|------|--------|
| Q1 | アプリ名は？（PascalCase） | ソリューション名・パッケージ名・ディレクトリ名 |
| Q2 | 認証機能は必要ですか？ | JWT / ASP.NET Core Identity の有効化判断 |
| Q3 | FE と BE を同一リポジトリで管理しますか？（デフォルト: はい） | モノレポ構成の確認 |
| Q4 | 外部 API（決済・メール・地図等）との連携はありますか？ | Infrastructure 層の初期構成確認 |

---

## 生成ドキュメント一覧

| ファイル | 内容 | Phase |
|---------|------|-------|
| `docs/02_design/architecture.md` | 全体構成図・FE/BE レイヤー図 | 1 |
| `docs/02_design/api_spec.md` | OpenAPI ベースの API 仕様方針 | 1 |
| `docs/03_implementation/directory_structure.md` | FE・BE ディレクトリ構成 | 1 |
| `docs/03_implementation/coding_standards.md` | TypeScript / C# コーディング規約 | 1 |
| `docs/03_implementation/dependencies.md` | npm パッケージ・NuGet パッケージ一覧 | 1 |
| `docs/03_implementation/invariants.md` | INV-FE-001〜004 + INV-BE-001〜006 | 1 |
| `docs/03_implementation/patterns.md` | Feature ベース構成・Repository パターン・DTO 変換 | 1 |
| `CONTEXT.md` 追記 | FE / BE 技術スタック・命名規則の大原則を更新 | 0→1 |

---

## 開発サイクル（このプロジェクトでの標準フロー）

```
1. exec-plans/active/ から作業を選ぶ
        ↓
2. docs/02_design/api_spec.md で対象 API のインターフェースを確認・定義する
   （BE 実装前に FE との契約を先に決める）
        ↓
3. feature/{issue-or-task-name} ブランチで実装
   ├── BE: Controller → Service → Repository の順に作成
   └── FE: api/ → hooks/ → components/ → pages/ の順に作成
        ↓
4. テストを追加
   ├── BE: xUnit（Service・Controller カバレッジ 80% 以上）
   └── FE: Vitest + RTL（フック・コンポーネントの主要ロジック）
        ↓
5. docs/04_quality/review_checklist.md でセルフレビュー
        ↓
6. PR 作成 → レビュー → マージ
   ├── CI-BE: dotnet build + dotnet test + Roslyn アナライザー
   └── CI-FE: tsc + eslint + vitest
        ↓
7. exec-plans/active/ の進捗ログを更新
```

---

## 完了条件

- [ ] 上記「生成ドキュメント一覧」の全ファイルが作成されている
- [ ] `docs/06_ai_context/CONTEXT.md` の技術スタック・命名規則セクションが更新されている
- [ ] `CONTEXT.md` の現在フェーズが「Phase 2（要件定義・設計）」になっている
