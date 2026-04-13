#!/usr/bin/env python3

from _common import log, maybe_record_head, resolve_assets


def main():
    try:
        assets = resolve_assets()
        if not assets["branch_dir"].exists():
            log("[dev-assets][Stop] branch memory not initialized, skip")
            return 0
        payload = maybe_record_head()
        log(f"[dev-assets][Stop] recorded HEAD {payload['last_seen_head']} for {payload['branch']}")
    except Exception as exc:
        log(f"[dev-assets][Stop] skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
