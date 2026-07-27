# 主动语义沉淀维护流程

目标是从用户指定的资料、当前代码事实或 Git 证据中提炼跨会话仍有价值的知识，并对照已有记忆生成一批可审核的新增或修订建议。此流程可反复调用；第一次调用和后续增量沉淀使用同一套规则。

## 硬规则

- 始终只处理提示中指定的单个 repo + branch。
- 所有命令都使用提示中给出的 CLI 路径，并显式传 `--repo`、必要时传 `--branch`。
- 优先使用用户点名的文档、目录、代码、提交或链接；没有给范围时，结合当前任务选择最可能承载稳定事实的 `AGENTS.md`、README、核心文档、关键实现和近期 Git 变更，不做无边界全仓扫描。
- 只写能够从本次资料或代码事实中找到依据、且下一次开发仍有价值的内容。
- 不复制整份 PRD、README、代码、聊天或 Git 历史；把来源压缩成可独立理解的结论，并保留低成本回源入口。
- 每次都先读取已有记忆并做差量判断。已有正确内容保持不动；同义内容不重复追加；旧结论失效时提出精确改写。
- branch 层保存当前分支知识；repo 层只保存跨分支稳定成立的长期知识。
- 在向用户展示本批 proposal 并获得确认前，不执行任何语义记忆写入。
- distill 没有 `completed` 状态，也不能成为后续 capture/session-scan 的写入门禁。

## 和其他流程的边界

- `init` 只创建存储骨架。
- `distill` 处理“外部事实 → 语义记忆”，既适用于首批建档，也适用于后续主动增量沉淀。
- `tidy` 处理“已有记忆 → 整理、去重和校准”。
- `archive` 处理共享知识上提和分支归档。
- `session-scan` 继续负责后台会话沉淀；主动 distill 不修改其 cursor，也不伪造会话扫描记录。

## 第一阶段：定位已有记忆

运行：

```bash
<CLI> init --repo <REPO> [--branch <BRANCH>]
<CLI> read show --repo <REPO> [--branch <BRANCH>]
```

按输出中的权威路径读取当前 branch 和必要的 repo 共享层文件。需要查相近旧条目时使用：

```bash
<CLI> read search --repo <REPO> [--branch <BRANCH>] --query "<关键词>"
<CLI> capture list-entries --repo <REPO> [--branch <BRANCH>] --kind <KIND>
<CLI> capture find-candidates --repo <REPO> [--branch <BRANCH>] --kind <KIND> --query "<旧结论>"
```

不要在 `~/.dev-memory` 下做无范围全局搜索。

## 第二阶段：读取本次证据

围绕用户指定的资料范围读取原始事实。若用户没有给范围，先在本维护会话中请用户说明希望沉淀的资料或主题；用户明确允许从当前仓库自行提炼时，再按硬规则选择有限资料集。

对每条候选判断：

- 下一次会话如果不知道它，是否容易重复踩坑或重新调研？
- 它是否属于稳定约束、决策原因、风险、术语、资料入口或关键文件导航？
- 它属于当前分支，还是确实跨分支稳定成立？
- 它是否已经存在，或会推翻一条已有记忆？

资料不足时列为“待补证据”，不要猜测后写入。

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

`add` 用于不存在的新条目；`upsert` 用于当前状态块；`rewrite` 必须带已有 entry id；`skip` 用于重复、短期或证据不足的候选。

让用户确认、删除或修改 proposal。用户未确认时保持只读。

## 第四阶段：确认后写入

把多行内容放入临时文件，按确认后的 proposal 执行：

```bash
# add / upsert
<CLI> capture record --repo <REPO> [--branch <BRANCH>] \
  --kind <KIND> --content-file <FILE>

# rewrite
<CLI> capture rewrite-entry --repo <REPO> [--branch <BRANCH>] \
  --id <ENTRY_ID> --content-file <FILE>
```

如果 append 写入被相似度检查阻止，先核对 matches。应修订旧条目时改走 `rewrite-entry`；确认是不同事实后才允许 `--force`。不要绕过 capture 直接编辑记忆文件。

## 第五阶段：复核

重新运行 `<CLI> read show --repo <REPO> [--branch <BRANCH>]`，并读取所有实际变更的 section，确认：

- 新条目落到了正确的 branch/repo 层和 section
- upsert 没有覆盖无关内容
- rewrite 没有留下互相矛盾的并行条目
- 没有写入临时信息或整段源文档

## 完成输出

向用户说明：

- 本次读取了哪些资料范围
- 新增、upsert、rewrite、skip 各多少项
- 实际改动了哪些记忆文件
- 哪些候选因重复或证据不足未写入
- 是否仍有需要用户补充的资料
