#!/usr/bin/env python3

import json
import sys

from _common import build_session_start_context, log


def main():
    try:
        additional_context = build_session_start_context()
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": additional_context,
            }
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except Exception as exc:
        log(f"[dev-assets][SessionStart] skipped: {exc}")
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "dev-assets SessionStart hook 未能加载上下文，本轮按普通会话继续。",
                    }
                },
                ensure_ascii=False,
            )
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
