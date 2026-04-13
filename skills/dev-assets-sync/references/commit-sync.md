# Commit Sync

The sync skill is triggered by commit-related moments, but it no longer mirrors commit history into dev-assets.

It should:

1. summarize only what this commit should leave behind
2. update only the branch or repo memory sections directly affected by this commit
3. update lightweight commit metadata when needed
4. leave detailed implementation history in Git

## `record-session` summary schema

`dev_asset_sync.py record-session` expects a JSON object with script-recognized keys. Do not infer field names from the prose bullets alone.

Accepted keys:

- `title`: string
- `overview_summary`: string or string array
- `implementation_notes`: string or string array
- `changes`: string or string array; alias of `implementation_notes`
- `risks`: string or string array
- `next_steps`: string or string array
- `sources`: string or string array
- `source_updates`: string or string array; alias of `sources`
- `decisions`: object array; each item should look like `{ "decision": "...", "reason": "...", "impact": "..." }`
- `memory`: string or string array
- `context_updates`: string or string array; alias of `memory`
- `review_notes`: string or string array
- `frontend_updates`: string or string array
- `backend_updates`: string or string array
- `test_updates`: string or string array

Minimal example:

```json
{
  "title": "本次检查点标题",
  "implementation_notes": [
    "完成了当前轮次最值得留存的进展"
  ],
  "risks": [
    "还有一个已知风险未消除"
  ],
  "next_steps": [
    "下次继续先做什么"
  ],
  "decisions": [
    {
      "decision": "之后优先检查页面入口装配和插件注入",
      "reason": "同批功能整组缺失时，先看单插件显隐容易偏题",
      "impact": "适用于同类插件化页面的排查顺序"
    }
  ],
  "sources": [
    "apps/example/page.tsx - 与这次检查点相关的共享资料入口"
  ]
}
```

Common mistakes:

- `current_progress` is not recognized; use `implementation_notes`
- `blockers_or_caveats` is not recognized; use `risks`
- `shared_sources` is not recognized; use `sources`
- `decisions` must be an object array, not a string array

Failure mode to remember:

- Wrong field names such as `shared_sources` are ignored
- `decisions` as `string[]` will fail when the script evaluates `item.get("decision")`
