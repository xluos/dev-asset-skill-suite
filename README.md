# Dev Asset Skill Suite

Repo-aware and branch-coupled development memory skills for Codex and similar agent runtimes.

This repository packages a small skill suite for one job: keep development memory usable across sessions without turning the Git worktree into a second document store.

- `using-dev-assets` — entry router for Git-repository development conversations
- `dev-assets-setup` — initialize user-home repo+branch memory storage for the current repository
- `dev-assets-context` — recover current branch memory first, then pull repo-shared memory when needed
- `dev-assets-update` — rewrite current durable memory or shared source indexes when new understanding appears
- `dev-assets-sync` — treat commit-related moments as checkpoints and persist only durable memory

Detailed guide:

- [docs/dev-asset-skill-suite-guide.md](docs/dev-asset-skill-suite-guide.md)

## Install with `npx skills`

List available skills:

```bash
npx skills add xluos/dev-asset-skill-suite --list
```

Install the whole suite for Codex globally:

```bash
npx skills add xluos/dev-asset-skill-suite --skill '*' -a codex -g -y
```

Install the whole suite for all detected agents:

```bash
npx skills add xluos/dev-asset-skill-suite --all -g -y
```

## Repository Layout

```text
bin/
  dev-assets.js              # `npx dev-assets` CLI entry (hooks + install helpers)
hooks/
  hooks.json                 # Claude hook template (.claude/settings.local.json)
  codex-hooks.json           # Codex hook template (.codex/hooks.json)
  README.md
lib/
  dev_asset_common.py        # shared library used by hook scripts
scripts/
  hooks/                     # session_start/pre_compact/stop/session_end .py — invoked via `dev-assets hook ...`
  install_codex_hooks.sh     # one-shot installer; symlinked as install_claude_hooks.sh
  install_claude_hooks.sh -> install_codex_hooks.sh
  install_suite.py           # local symlink-based skill install (dev only)
  npm/                       # package check/build helpers
skills/
  using-dev-assets/
  dev-assets-setup/
  dev-assets-context/
  dev-assets-update/
  dev-assets-sync/
suite-manifest.json          # canonical list of suite + legacy skill names
```

## Storage Layout

By default the suite stores memory outside the repository:

```text
~/.dev-assets/repos/<repo-key>/
  repo/
    overview.md
    context.md
    sources.md
    manifest.json
  branches/
    <branch>/
      overview.md
      development.md
      context.md
      sources.md
      manifest.json
      artifacts/
        history/
```

- `repo/`: shared memory for the whole Git repository
- `branches/<branch>/`: branch-local working memory
- `repo-key`: derived from repository identity, not just the folder name
- `DEV_ASSETS_ROOT`: environment variable that overrides the default storage root (`~/.dev-assets/repos`); honored by the CLI and all bundled skill scripts

## Lifecycle Hooks

This suite now follows ECC-style lifecycle hooks instead of Git hooks, and it supports both Claude and Codex.

- Claude recommended repo-local target: `.claude/settings.local.json`
- Codex recommended repo-local target: `.codex/hooks.json`
- Claude reusable template: `hooks/hooks.json`
- Codex reusable template: `hooks/codex-hooks.json`
- Hook behavior guide: `hooks/README.md`

Current mapping by agent:

- Claude: `SessionStart`, `PreCompact`, `Stop`, `SessionEnd`
- Codex: `SessionStart`, `Stop`

Shared behavior:

- `SessionStart`: restore repo+branch memory into the new session
- `PreCompact`: refresh working-tree-derived navigation before compaction
- `Stop`: persist a lightweight HEAD marker after each response
- `SessionEnd`: persist the final HEAD marker at session end

Quick install into the current repository (Codex by default; pass `--agent claude` for Claude, or invoke the symlinked `install_claude_hooks.sh`):

```bash
sh scripts/install_codex_hooks.sh                    # Codex
sh scripts/install_codex_hooks.sh --agent claude     # Claude
sh scripts/install_claude_hooks.sh                   # equivalent to the line above
```

Or run either installer directly from GitHub in the repository you want to enable:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/xluos/dev-asset-skill-suite/main/scripts/install_codex_hooks.sh)"
sh -c "$(curl -fsSL https://raw.githubusercontent.com/xluos/dev-asset-skill-suite/main/scripts/install_claude_hooks.sh)"
```

The installer will:

- install `@xluos/dev-assets-cli` into the target repository
- merge hooks into `.codex/hooks.json` or `.claude/settings.local.json` depending on the chosen agent
- make hooks call `npx dev-assets hook ...`, so they no longer depend on repo-local Python paths

If the CLI is already a dev-dependency in the target repository, you can merge hooks directly without re-running the installer:

```bash
npx dev-assets install-hooks codex
npx dev-assets install-hooks claude
```

Or install the CLI alone (without merging any hooks):

```bash
npx dev-assets install-cli                           # default package: @xluos/dev-assets-cli
npx dev-assets install-cli --package file:/path/to/checkout
```

`install-hooks <agent>` requires the CLI to already be importable in the target repo's `node_modules`; the shell installer above handles that bootstrap step. Don't run `install-hooks claude` in a fresh repo without first running either the shell installer or `install-cli`.

Boundary:

- This repository ships reusable hook templates and a reusable CLI, but the actual repo-local config files are environment-local
- In this clone, Codex can read `.codex/hooks.json` directly; Claude typically uses a local `.claude/settings.local.json` file that may be ignored by user-level Git rules
- Global skill installs do not auto-load hooks yet, because this project is a skill suite rather than a standalone plugin
- Hook execution is now expected to go through `dev-assets` CLI, not raw `python3 scripts/hooks/*.py`

## Two Invocation Tracks

This suite has two distinct entry surfaces. They look similar but should not be confused.

- Lifecycle hooks → `npx dev-assets hook <session-start|pre-compact|stop|session-end>`. These run automatically from `.codex/hooks.json` or `.claude/settings.local.json` and are the only place where the `dev-assets` CLI is the right entry point.
- In-conversation skill workflows (`dev-assets-setup`, `dev-assets-context`, `dev-assets-update`, `dev-assets-sync`) → invoke each skill's bundled Python script under `<skill-dir>/scripts/`. The CLI does not wrap these because they are interactive workflow steps with skill-specific arguments, not background hook actions.

Inside SKILL.md files these script paths appear as `python3 /absolute/path/to/<skill>/scripts/<name>.py`. The agent is expected to substitute the actual on-disk skill directory at call time (the path the harness loaded the skill from), not to pass the literal placeholder string.

## Notes

- The suite no longer stores its primary memory inside the Git worktree by default.
- Branch memory is still the main execution context. Repo memory is a shared supplement, not a replacement.
- Detailed implementation history should stay in Git. When the agent needs exact changes, it should read `git log` / `git show` instead of copying commit history into dev assets.
- Shared document entrances can live in repo-level `sources.md`; branch-specific progress and next-step live in branch files.
- `dev-assets-setup` can migrate legacy `.dev-assets/<branch>/` content into the new user-home branch directory.
- `npx skills` does not need `scripts/install_suite.py`; the repository already follows standard skill discovery rules.
- `scripts/install_suite.py` remains useful for local symlink-based installs during development. Example — symlink all suite skills into Codex's user-level skill directory and prune legacy aliases:

  ```bash
  python3 scripts/install_suite.py --target ~/.codex/skills --force --remove-legacy
  ```
