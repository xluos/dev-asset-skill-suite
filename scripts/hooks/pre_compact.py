#!/usr/bin/env python3
"""PreCompact hook — intentionally a no-op.

In earlier versions this hook refreshed progress.md's auto-sync block via
`capture sync-working-tree`, but SessionStart already does the same refresh
at the start of every conversation. Running it again right before context
compaction adds no signal (the agent's transcript already carries the prior
sync) and burns extra git commands. Kept as a stub so existing hook
installations don't error out — safe to remove from settings if you want.
"""

from _common import log


def main():
    log("[dev-memory][PreCompact] no-op (refresh handled at SessionStart)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
