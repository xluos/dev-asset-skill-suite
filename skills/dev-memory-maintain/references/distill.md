# 主动语义沉淀流程

目标是从用户指定的资料、当前代码事实或 Git 证据中提炼跨会话仍有价值的知识，并对照已有记忆生成一批可审核的新增或修订建议。此流程可反复调用；第一次调用和后续增量沉淀使用同一套规则。

## 执行准备

1. 确认目标 Git 仓库和分支。默认使用当前仓库与当前分支；用户指定时使用指定值。
2. 确认本次资料范围。优先使用用户点名的文档、目录、代码、提交或链接；没有给范围时，结合当前任务只选择最可能承载稳定事实的 `AGENTS.md`、README、核心文档、关键实现和近期 Git 变更，不做无边界全仓扫描。
3. 确认 `dev-memory-cli` 可用。若正在 dev-memory-skill-suite 源码仓内开发，可使用 `node <repo>/bin/dev-memory.js`；否则使用已安装的 `dev-memory-cli`。
4. 后续所有命令都显式传 `--repo <REPO>`，指定了非当前分支时再传 `--branch <BRANCH>`。
5. 沉淀范围默认是 `branch`；只有用户明确要求或证据表明内容跨分支稳定成立时，才提出 repo 共享层写入建议。

以下用 `<CLI>` 表示上一步确认的 CLI 命令。

## 和其他流程的边界

- `init` 只创建存储骨架；运行 `<CLI> init --repo <REPO> [--branch <BRANCH>]` 确保骨架存在即可。
- `distill` 处理“外部事实 → 语义记忆”，既适用于首批建档，也适用于后续主动增量沉淀。
- `tidy` 处理“已有记忆 → 整理、去重和校准”；本次主要诉求是清理记忆自身时切换到整理流程。
- `archive` 处理分支结束后的共享知识上提和分支归档。
- `session-scan` 继续负责后台会话沉淀；主动 distill 不修改其 cursor，也不伪造会话扫描记录。

## 硬规则

- 只写能够从本次资料或代码事实中找到依据、且下一次开发仍有价值的内容。
- 不复制整份 PRD、README、代码、聊天或 Git 历史；把来源压缩成可独立理解的结论，并保留低成本回源入口。
- 临时进度、一次性命令输出、显然能从 Git 低成本恢复的实现流水不写入语义记忆。
- branch 层保存当前分支目标、范围、约束、决策、风险、术语、入口和文件导航；repo 层只保存跨分支稳定成立的长期知识。
- 每次都先读取已有记忆并做差量判断。已有正确内容保持不动；同义内容不重复追加；旧结论失效时提出精确改写，不追加一条互相矛盾的新结论。
- 在向用户展示本批 proposal 并获得确认前，不执行任何 `capture record`、`rewrite-entry` 或 `delete-entry` 语义写入。
- distill 没有 `completed` 状态，也不能成为后续 capture/session-scan 的写入门禁。

## 第一阶段：定位并读取已有记忆

先运行：

```bash
<CLI> init --repo <REPO> [--branch <BRANCH>]
<CLI> read show --repo <REPO> [--branch <BRANCH>]
```

按 `read show` 返回的权威路径读取当前 branch 和必要的 repo 共享层文件。需要查相近旧条目时，优先使用：

```bash
<CLI> read search --repo <REPO> [--branch <BRANCH>] --query "<关键词>"
<CLI> capture list-entries --repo <REPO> [--branch <BRANCH>] --kind <KIND>
<CLI> capture find-candidates --repo <REPO> [--branch <BRANCH>] --kind <KIND> --query "<旧结论>"
```

不要在 `~/.dev-memory` 下做无范围全局搜索。

## 第二阶段：读取本次证据

围绕已确认的资料范围读取原始事实，并记录每条候选记忆的依据。判断重点：

- 下一次会话如果不知道它，是否容易重复踩坑或重新调研？
- 它是稳定约束、决策原因、风险、术语、资料入口或关键文件导航吗？
- 它属于当前分支，还是确实跨分支稳定成立？
- 它是否已经存在，或会推翻一条已有记忆？

资料不足时明确列为“待补证据”，不要猜测后写入。

## 第三阶段：生成差量 proposal

向用户展示本批 proposal。每项至少包含：

- `action`：`add`、`upsert`、`rewrite` 或 `skip`
- `kind`：目标 capture kind
- `content`：准备落盘的完整、可独立理解内容
- `target`：branch 或 repo
- `evidence`：文件路径、文档入口、commit 或用户明确提供的事实
- `reason`：为什么值得跨会话保留

常用 kind：

- branch：`overview`、`scope`、`constraint`、`filemap`、`decision`、`risk`、`glossary`、`source`
- repo：`shared-overview`、`shared-constraint`、`shared-decision`、`shared-context`、`shared-source`

`add` 用于不存在的新条目；`upsert` 用于 overview/scope/constraint/filemap 等当前状态块；`rewrite` 必须带已有 entry id；`skip` 用于重复、短期或证据不足的候选。

让用户确认、删除或修改 proposal。用户未确认时保持只读。

## 第四阶段：确认后写入

把多行内容放入临时文件，避免 shell 转义破坏正文。按用户确认后的 proposal 执行：

```bash
# add / upsert
<CLI> capture record --repo <REPO> [--branch <BRANCH>] \
  --kind <KIND> --content-file <FILE>

# rewrite
<CLI> capture rewrite-entry --repo <REPO> [--branch <BRANCH>] \
  --id <ENTRY_ID> --content-file <FILE>
```

如果 append 写入被相似度检查阻止，先核对返回的 matches。应修订旧条目时改走 `rewrite-entry`；确认确实是不同事实后才允许 `--force`。

不要为了批量方便绕过 capture 直接编辑记忆文件。

## 第五阶段：复核

写入后重新运行：

```bash
<CLI> read show --repo <REPO> [--branch <BRANCH>]
```

读取所有实际变更的目标 section，确认：

- 新条目落到了正确的 branch/repo 层和 section
- upsert 没有覆盖无关内容
- rewrite 已替换旧结论，没有留下互相矛盾的并行条目
- 没有把临时信息或整段源文档写入记忆

## 完成输出

向用户说明：

- 本次读取了哪些资料范围
- 新增、upsert、rewrite、skip 各多少项
- 实际改动了哪些记忆文件
- 哪些候选因重复或证据不足未写入
- 是否仍有需要用户补充的资料
