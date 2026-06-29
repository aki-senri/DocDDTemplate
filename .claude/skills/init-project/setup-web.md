# Phase 1 Setup: Web App (React / ASP.NET Core / .NET 8)

> **When to run**: Run after selecting Web in Q4 of the `init-project` skill
>
> **Purpose**: Finalize the configuration, design, and development procedures for a React frontend + ASP.NET Core backend as documents,
> so that team members and AI agents can develop from the same baseline.

---

## Fixed decisions (standards defined by this skill)

Do not change the following unless there is a project-specific reason.
If a change is made, record the reason in `docs/00_project/decisions.md`.

### Tech stack

#### Frontend (FE)

| Item | Technology | Reason |
|------|-----------|--------|
| Language | TypeScript 5.x | Type safety, IDE support |
| UI library | React 18.x | Mature ecosystem |
| Build tool | Vite 5.x | Fast dev server and builds |
| Routing | React Router v6 | Standard routing for React |
| Server state management | TanStack Query 5.x | API data fetching, caching, and synchronization |
| Styling | CSS Modules | Scoped CSS, no build tool needed |
| Code quality | ESLint + Prettier | Static analysis and unified formatting |
| Testing | Vitest + React Testing Library | Vite integration, lightweight |

#### Backend (BE)

| Item | Technology | Reason |
|------|-----------|--------|
| Language | C# 12 | Default for .NET 8 |
| Runtime | .NET 8 | LTS, standard support until November 2026 |
| Framework | ASP.NET Core 8 Web API | Standard .NET REST API framework |
| ORM | Entity Framework Core 8 | Type-safe queries with LINQ |
| DB | PostgreSQL 15 | Standard for web apps; scalable |
| API spec | OpenAPI (Swagger / Swashbuckle) | Auto-generated as the contract with FE |
| Authentication | ASP.NET Core Identity + JWT | Standard authentication infrastructure |
| Logging | Serilog 3.x | Structured logging |
| Testing | xUnit 2.x + Moq 4.x | Standard .NET test stack |

#### Infrastructure

| Item | Technology |
|------|-----------|
| CI | GitHub Actions |
| FE deployment | Static hosting (Vercel / Azure Static Web Apps) |
| BE deployment | Container (Docker + Azure App Service / Cloud Run) |

### Architecture

#### Overall structure

```
[Browser]
    │ HTTPS / JSON
    ▼
[React SPA]  ─── TanStack Query ───► [ASP.NET Core Web API]
                                              │
                                     Controller → Service → Repository
                                              │
                                        [PostgreSQL]
```

#### FE architecture: Feature-based structure

Group related components, hooks, and types into a single feature unit.
Only shared components go in `shared/`.

```
src/
├── features/           # Split by feature
│   └── {featureName}/
│       ├── components/ # Components specific to this feature
│       ├── hooks/      # Hooks specific to this feature
│       ├── api/        # TanStack Query query definitions
│       └── types.ts    # Type definitions for this feature
├── shared/
│   ├── components/     # General-purpose UI components
│   ├── hooks/          # General-purpose hooks
│   └── types/          # Common type definitions
├── pages/              # Page components corresponding to routes
└── lib/                # Config and utilities
```

#### BE architecture: Layered architecture

Dependencies are one-directional only. Contracts with FE are managed via OpenAPI spec.

```
Controller → Service → Repository → Model (Entity)
```

| Layer | Responsibility | Location |
|-------|---------------|---------|
| Controller | Receives HTTP requests and returns responses only | `Controllers/` |
| Service | Business logic | `Services/` |
| Repository | Abstraction of DB access (EF Core) | `Repositories/` |
| Model | DB entities and DTOs | `Models/` |

### Directory structure

Monorepo structure. FE and BE managed in the same repository.

```
{APP_NAME}/
├── frontend/                         # React app
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
│   │   │   ├── Entities/             # DB entities
│   │   │   └── DTOs/                 # Request and response types
│   │   ├── Infrastructure/           # DI, EF Core config, logging
│   │   └── Program.cs                # DI setup and middleware config
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

### Key invariants

#### FE

| # | Condition |
|---|-----------|
| INV-FE-001 | Direct imports between features are prohibited (`features/A` must not reference `features/B`) |
| INV-FE-002 | All API communication must go through TanStack Query hooks in `features/{name}/api/` |
| INV-FE-003 | Components must always have a props type definition (`any` is prohibited) |
| INV-FE-004 | Do not write logic in page components (extract to hooks or components) |

#### BE

| # | Condition |
|---|-----------|
| INV-BE-001 | Only the Controller → Service → Repository dependency direction is allowed |
| INV-BE-002 | Controller must not contain logic; delegate to Service |
| INV-BE-003 | Service must depend on the Repository interface (not directly on the implementation class) |
| INV-BE-004 | Input validation is performed at the Controller entry point (FluentValidation or DataAnnotations) |
| INV-BE-005 | `async void` is prohibited; use `async Task` or `async Task<T>` |
| INV-BE-006 | Do not return DB entities directly as Controller responses (always convert to DTOs) |
| INV-T01 | Tests must not be modified to match implementation behavior. Test modifications must always be grounded in a spec (AC-ID) |

### Key coding conventions

```typescript
// FE: Define a Props type for components
type TaskCardProps = {
  title: string;
  onComplete: () => void;
};
export function TaskCard({ title, onComplete }: TaskCardProps) { ... }

// FE: Define API hooks with TanStack Query
export function useTaskList() {
  return useQuery({ queryKey: ['tasks'], queryFn: fetchTasks });
}
```

```csharp
// BE: Controller has no logic
[HttpGet]
public async Task<IActionResult> GetAll(CancellationToken ct)
    => Ok(await _taskService.GetAllAsync(ct));

// BE: private fields use _camelCase
private readonly ITaskService _taskService;

// BE: async methods use Async suffix
public async Task<IEnumerable<TaskDto>> GetAllAsync(CancellationToken ct = default)
```

---

## Interview (project-specific)

The agent only asks the following. The tech stack is already fixed and should not be asked about.

| # | Question | Used for |
|---|----------|---------|
| Q1 | What is the app name? (PascalCase) | Solution name, package name, directory name |
| Q2 | Is authentication required? | Deciding whether to enable JWT / ASP.NET Core Identity |
| Q3 | Will FE and BE be managed in the same repository? (default: yes) | Confirming monorepo structure |
| Q4 | Is there any external API integration (payments, email, maps, etc.)? | Confirming the initial structure of the Infrastructure layer |

---

## Documents to generate

| File | Content | Phase |
|------|---------|-------|
| `docs/03_design/architecture.md` | Overall structure diagram, FE/BE layer diagrams | 1 |
| `docs/03_design/api_spec.md` | API specification policy based on OpenAPI | 1 |
| `docs/04_implementation/directory_structure.md` | FE and BE directory structure | 1 |
| `docs/04_implementation/coding_standards.md` | TypeScript / C# coding conventions | 1 |
| `docs/04_implementation/dependencies.md` | npm package and NuGet package list | 1 |
| `docs/04_implementation/invariants.md` | INV-FE-001–004 + INV-BE-001–006 + INV-T01 | 1 |
| `docs/04_implementation/patterns.md` | Feature-based structure, Repository pattern, DTO conversion | 1 |
| `docs/05_quality/test_strategy.md` | Test policy, test_command_fe/be, AC-ID tagging convention | 1 |
| `CONTEXT.md` update | Update FE/BE tech stack and core naming convention sections | 0→1 |

---

## Development cycle (standard flow for this project)

```
1. Select work from exec-plans/active/
        ↓
2. Confirm / define the target API interface in docs/03_design/api_spec.md
   (Decide the FE contract before BE implementation)
        ↓
3. Implement on feature/{issue-or-task-name} branch
   ├── BE: Create in order: Controller → Service → Repository
   └── FE: Create in order: api/ → hooks/ → components/ → pages/
        ↓
4. Add tests
   ├── BE: xUnit (80%+ coverage for Service and Controller) — include AC-ID with [Trait("AC", "AC-XXX")]
   └── FE: Vitest + RTL (main logic of hooks and components) — include AC-ID with describe('AC-XXX: ...')
        ↓
5. Self-review with docs/05_quality/review_checklist.md
        ↓
6. Create PR → Review → Merge
   ├── CI-BE: dotnet build + dotnet test + Roslyn analyzers
   └── CI-FE: tsc + eslint + vitest
        ↓
7. Update progress log in exec-plans/active/
```

---

## Completion criteria

- [ ] All files in the "Documents to generate" list above have been created
- [ ] The tech stack and naming convention sections of `docs/07_ai_context/CONTEXT.md` have been updated
- [ ] The current phase in `CONTEXT.md` is set to "Phase 2 (requirements & design)"
