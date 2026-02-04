---
name: arxiv-read
description: 深度阅读当前 arXiv 论文，生成结构化笔记 SUMMARY.md。用法：/arxiv-read [id]
---

# 深度阅读论文

## 功能

阅读论文 PDF，生成结构化的 SUMMARY.md 笔记，包含问题背景、核心创新、方法细节、实验结果等。

## 用法

```
/arxiv-read [id]
```

## 参数

- 无参数: 阅读当前活跃论文
- `[id]`: 指定论文 ID

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/read.py [id]
```

## 生成的 SUMMARY.md 结构

```markdown
## Context
<!-- 解决什么问题？之前方法的痛点？ -->

## Key Insight
<!-- 核心创新一句话 -->

## Method
### Architecture
### Key Equations

## Results
| Method | Metric1 | Metric2 |
|--------|---------|---------|

## Takeaways
## Open Questions
## Related Papers
```

## 工作流

1. 读取 `paper.pdf`
2. 提取关键信息
3. 更新 `SUMMARY.md`
4. 更新 `info.yaml` 状态为 `learned`

## 相关指令

- `/arxiv-init <id>` - 先初始化论文
- `/arxiv-repro` - 阅读后复现代码
