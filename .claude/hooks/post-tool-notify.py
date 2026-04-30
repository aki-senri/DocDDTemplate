#!/usr/bin/env python3
"""DocDD PostToolUse hook - notifies after Write/Edit on relevant files."""
import sys
import json
import re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")
if not file_path:
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
