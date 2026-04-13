---
name: dev-assets-sync
description: Use when the current conversation reaches a commit-related checkpoint or another clear persistence checkpoint, and Codex should write only this round's durable memory back into the current branch memory while keeping repo-shared metadata in sync.
---

# Dev Assets Sync

在提交相关检查点，或在当前对话已经形成需要跨会话保留的稳定结论时，把这次会话结束后仍然有价值的信息同步到当前 branch 记忆，并顺带刷新 repo 共享层的轻量元信息。

**Announce at start:** 用一句简短的话说明将先沉淀本次检查点留下的关键信息。

## Workflow

### Step 1: Decide whether this moment is worth syncing

只在当前时点已经形成明确的持久化价值时触发 `sync`。

### Step 2: Summarize only what this checkpoint should leave behind

优先提炼：

- 当前进展
- 当前阻塞与注意点
- 下一步
- 关键决策与原因
- 本次新增的共享资料入口

然后运行：

```bash
python3 /absolute/path/to/dev-assets-sync/scripts/dev_asset_sync.py record-session --repo <repo-path> --summary-file <summary.json>
```

### Step 3: Keep branch state and repo metadata separate

`record-session` 的默认落点是：

- 进展 / 风险 / 下一步 / 分支级决策 → branch 文件
- 新增资料入口 → repo `sources.md`
- HEAD / 最近访问分支 → manifest

它默认不做这些事：

- 不重建整个 branch memory
- 不把实现流水账写回记忆
- 不把 branch-specific 当前状态写进 repo 共享正文

### Step 4: Lifecycle hooks are the default low-friction path

如果希望不依赖对话里显式触发，就使用仓库提供的生命周期 hook 模板与脚本：

- `SessionStart` 恢复当前 repo+branch 记忆
- `PreCompact` 刷新 working-tree-derived navigation
- `Stop` / `SessionEnd` 只保留轻量 HEAD marker

推荐的 repo-local 落地点：

- Claude: `.claude/settings.local.json`
- Codex: `.codex/hooks.json`

可复用模板：

- Claude: `hooks/hooks.json`
- Codex: `hooks/codex-hooks.json`

## Commands

```bash
python3 /absolute/path/to/dev-assets-sync/scripts/dev_asset_sync.py record-session --repo <repo-path> --summary-file <summary.json>
python3 /absolute/path/to/dev-assets-sync/scripts/dev_asset_sync.py sync-working-tree --repo <repo-path>
python3 /absolute/path/to/dev-assets-sync/scripts/dev_asset_sync.py record-head --repo <repo-path>
```

## Always / Never

**Always:**

- 把提交检查点和阶段性里程碑都视为 `sync` 触发点
- 优先沉淀本次提交留下的关键信息，而不是累积历史
- 明确区分 branch 当前记忆、repo 共享入口、Git 历史

**Never:**

- 把 `sync` 当成 append-only 日志工具
- 把 `sync` 当成全局状态重建工具
- 为了“怕漏”就把所有改动详情抄进记忆
- 把 commit history 当成 dev-assets 的一部分
