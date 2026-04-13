#!/usr/bin/env python3

from _common import log, maybe_sync_working_tree, resolve_assets


def main():
    try:
        assets = resolve_assets()
        if not assets["branch_dir"].exists():
            log("[dev-assets][PreCompact] branch memory not initialized, skip")
            return 0
        payload = maybe_sync_working_tree()
        log(
            "[dev-assets][PreCompact] refreshed working-tree navigation for "
            f"{payload['branch']} ({payload['files_considered']} files)"
        )
    except Exception as exc:
        log(f"[dev-assets][PreCompact] skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
