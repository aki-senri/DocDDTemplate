#!/usr/bin/env python3
"""DocDD PostToolUse hook - notifies after Write/Edit on relevant files."""
import sys
import json
import os
import re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")
if not file_path:
    sys.exit(0)


def _project_root() -> str:
    return (
        os.environ.get("CLAUDE_PROJECT_DIR")
        or data.get("cwd")
        or os.getcwd()
    )


def _submodule_paths(project_root: str) -> list[str]:
    gitmodules = os.path.join(project_root, ".gitmodules")
    if not os.path.isfile(gitmodules):
        return []
    paths: list[str] = []
    try:
        with open(gitmodules, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"\s*path\s*=\s*(.+?)\s*$", line)
                if m:
                    paths.append(m.group(1).strip())
    except Exception:
        return []
    return paths


def _is_in_submodule(file_path: str) -> bool:
    project_root = _project_root()
    submodules = _submodule_paths(project_root)
    if not submodules:
        return False
    if os.path.isabs(file_path):
        try:
            rel = os.path.relpath(file_path, project_root)
        except ValueError:
            return False
    else:
        rel = file_path
    rel = os.path.normpath(rel).replace(os.sep, "/")
    # Path escapes the project root or is unrelated — not a submodule file.
    if rel == ".." or rel.startswith("../") or os.path.isabs(rel):
        return False
    for sub in submodules:
        sub_norm = os.path.normpath(sub).replace(os.sep, "/").strip("/")
        if not sub_norm or sub_norm == ".":
            continue
        if rel == sub_norm or rel.startswith(sub_norm + "/"):
            return True
    return False


# Skip notifications for files inside submodules.
# Submodules are external code; the parent's exec-plans/docs do not apply,
# and emitting DocDD guidance for them produces misleading messages.
if _is_in_submodule(file_path):
    sys.exit(0)

if re.search(r"exec-plans[/\\]completed", file_path):
    msg = (
        "[DocDD] 実行計画が completed に移動しました。"
        "update-context スキルで CONTEXT.md の現在フェーズ・優先タスクを更新してください。"
    )
elif re.search(r"exec-plans[/\\]active", file_path):
    msg = (
        "[DocDD] exec-plans/active を更新しました。"
        "CONTEXT.md の優先タスクが最新かどうか、必要に応じて update-context スキルを実行してください。"
    )
elif re.search(r"Tests?\.cs$|\.test\.(ts|tsx|js)$|\.spec\.(ts|tsx|js)$", file_path):
    msg = (
        "[DocDD] テストファイルを変更しました。"
        "この変更は仕様（AC-ID）に基づいていますか？"
        "実装の挙動に合わせたテスト修正は禁止です。"
        "変更理由を exec-plan の判断ログに記録してください。"
    )
elif not re.search(r"\.(md|txt|json|yaml|yml|toml|xml|html|css|svg|png|jpg|gif|ico|lock|sum)$", file_path):
    msg = (
        "[DocDD] コードファイルを変更しました。"
        "(1) check-doc-freshness でドキュメントとの乖離を確認してください。"
        "(2) テストが失敗した場合は、テストを修正する前に対応する仕様（AC-ID）を確認し、"
        "run-tests スキルで仕様照合ゲートを通してください。"
    )
else:
    sys.exit(0)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": msg
    }
}))
