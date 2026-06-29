# Phase 1 Setup: Windows Desktop App (WPF / .NET 8 / C#)

> **When to run**: Run after selecting Windows in Q4 of the `init-project` skill
>
> **Purpose**: Finalize the configuration, design, and development procedures needed for Windows WPF app development as documents,
> so that team members and AI agents can develop from the same baseline.

---

## Fixed decisions (standards defined by this skill)

Do not change the following unless there is a project-specific reason.
If a change is made, record the reason in `docs/00_project/decisions.md`.

### Tech stack

| Item | Technology | Reason |
|------|-----------|--------|
| Language | C# 12 | Default for .NET 8 |
| Runtime | .NET 8 (Desktop Runtime) | LTS, standard support until November 2026 |
| UI framework | WPF | Proven track record for overlay and always-on-top control; more mature than WinUI 3 |
| MVVM library | CommunityToolkit.Mvvm 8.x | Official Microsoft library; minimizes boilerplate with Source Generators |
| DI container | Microsoft.Extensions.DependencyInjection 8.x | .NET standard; low learning curve |
| Local DB | Microsoft.Data.Sqlite 8.x | Standard for locally self-contained apps; no ORM needed for this level of complexity |
| Logging | Serilog 3.x + Serilog.Sinks.File | File logging with rotation |
| Testing | xUnit 2.x + Moq 4.x | Standard .NET test stack |
| Packaging | MSIX | Windows 10/11 standard; guarantees clean uninstall |
| CI | GitHub Actions (windows-latest) | Environment where MSBuild is available |

### Architecture

Layered architecture + MVVM. **Dependencies are one-directional only.**

```
View → ViewModel → Service → Repository → Model
```

| Layer | Responsibility | Location |
|-------|---------------|---------|
| View | UI rendering and input only. No logic | `Views/` |
| ViewModel | UI state and command definitions. Delegates to Service | `ViewModels/` |
| Service | Business logic. Data operations through Repository | `Services/` |
| Repository | Abstraction of DB access (via interface) | `Repositories/` |
| Model | Data structure definitions only. No logic | `Models/` |

### Directory structure

```
{APP_NAME}.sln
├── src/
│   └── {APP_NAME}/
│       ├── App.xaml / App.xaml.cs    # DI setup and startup
│       ├── Models/                   # Data structures
│       ├── ViewModels/               # MVVM ViewModel
│       ├── Views/                    # XAML windows and dialogs
│       ├── Services/
│       │   └── Interfaces/           # Service interfaces
│       ├── Repositories/
│       │   └── Interfaces/           # Repository interfaces
│       ├── Infrastructure/           # DI config, DB init, logging
│       └── Assets/                   # Icons and themes
└── tests/
    └── {APP_NAME}.Tests/             # xUnit test project
        ├── Services/
        ├── ViewModels/
        └── Repositories/
```

### Key invariants

Follow the rules below during implementation. Violations are automatically detected by Roslyn analyzers + CI.

| # | Condition | On violation |
|---|-----------|-------------|
| INV-001 | Only the View → ViewModel → Service → Repository → Model dependency direction is allowed | Build error |
| INV-002 | ViewModel must not contain logic; delegate to Service | Build error |
| INV-003 | Do not write business logic in `.xaml.cs` (warning if over 50 lines) | Warning |
| INV-004 | `.cs` 300 lines, `.xaml` 200 lines, `App.xaml.cs` 100 lines maximum | Warning/Error |
| INV-005 | `async void` is prohibited except for WPF event handlers | Build error |
| INV-006 | `private` fields use `_camelCase`; async methods use `Async` suffix | Build warning |
| INV-007 | External network communication is prohibited | Warning |
| INV-008 | Input validation is performed at the Service layer entry point | Review comment |
| INV-T01 | Tests must not be modified to match implementation behavior. Test modifications must always be grounded in a spec (AC-ID) | Review comment |

### Key coding conventions

```csharp
// ViewModel: inherit ObservableObject + use Source Generator
[ObservableProperty] private string _currentTask = string.Empty;
[RelayCommand] private async Task ChangeTaskAsync() { ... }

// Async: always accept CancellationToken
public async Task<IEnumerable<TaskItem>> GetAllAsync(CancellationToken ct = default)

// private fields: _camelCase
private readonly ITaskService _taskService;
```

---

## Interview (project-specific)

The agent only asks the following. The tech stack is already fixed and should not be asked about.

| # | Question | Used for |
|---|----------|---------|
| Q1 | What is the app name? (PascalCase) | Solution name, namespace, executable name |
| Q2 | Will you persist data? (whether to use SQLite) | Deciding whether to enable `feat-sqlite` |
| Q3 | Does the app require internet access? (usually not needed) | Confirming the scope of INV-007 |
| Q4 | Is it a multi-window layout? (if there are windows other than the main window) | Confirming the initial structure of Views/ |

---

## Documents to generate

| File | Content | Phase |
|------|---------|-------|
| `docs/03_design/architecture.md` | Layer diagram, DI configuration, project structure | 1 |
| `docs/04_implementation/directory_structure.md` | Directory structure (reflects Q1 app name) | 1 |
| `docs/04_implementation/coding_standards.md` | C# / WPF coding conventions | 1 |
| `docs/04_implementation/dependencies.md` | NuGet package list and version management policy | 1 |
| `docs/04_implementation/invariants.md` | INV-001–008 + INV-T01 (Roslyn enforcement rules) | 1 |
| `docs/04_implementation/patterns.md` | MVVM, Repository, and DI implementation patterns | 1 |
| `docs/05_quality/test_strategy.md` | Test policy, test_command, AC-ID tagging convention | 1 |
| `CONTEXT.md` update | Update tech stack and core naming convention sections | 0→1 |

---

## Development cycle (standard flow for this project)

```
1. Select work from exec-plans/active/
        ↓
2. Confirm acceptance criteria in docs/01_requirements/user_stories/windows.md
        ↓
3. Confirm docs/04_implementation/invariants.md (required reading before implementation)
        ↓
4. Implement on feature/{issue-or-task-name} branch
   └── Create in order: View → ViewModel → Service → Repository
        ↓
5. Add xUnit tests (80%+ coverage for ViewModel and Service layers)
   └── Include AC-ID in tests with [Trait("AC", "AC-XXX")]
        ↓
6. Self-review with docs/05_quality/review_checklist.md
        ↓
7. Create PR → Review → Merge
   └── CI (GitHub Actions): dotnet build + dotnet test + Roslyn analyzers
        ↓
8. Update progress log in exec-plans/active/
```

---

## Completion criteria

- [ ] All files in the "Documents to generate" list above have been created
- [ ] The tech stack and naming convention sections of `docs/07_ai_context/CONTEXT.md` have been updated
- [ ] The current phase in `CONTEXT.md` is set to "Phase 2 (requirements & design)"
