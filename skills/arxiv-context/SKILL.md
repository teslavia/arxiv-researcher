---
name: arxiv-context
description: 查看或切换当前活跃的 arXiv 论文。用法：/arxiv-context [id]
---

# 论文上下文管理

## 功能

查看或切换当前活跃的论文项目。其他指令（如 `/arxiv-read`、`/arxiv-repro`）默认操作当前活跃论文。

## 用法

```
/arxiv-context [id]
```

## 参数

- 无参数: 显示当前活跃论文信息
- `[id]`: 切换到指定论文（arXiv ID 或项目目录名）

## 执行

```bash
# 查看当前上下文
python3 ~/.claude/skills/arxiv-researcher/scripts/context.py

# 切换上下文
python3 ~/.claude/skills/arxiv-researcher/scripts/context.py 2401.12345
```

## 输出示例

```
📍 Current Context: 2401.12345_speculative_decoding

Title: Speculative Decoding for Large Language Models
Status: learned
Path: /knowledge/arxiv/2401.CS/2401.12345_speculative_decoding/
```

## 上下文文件

上下文信息存储在 `/knowledge/arxiv/.context`

## 相关指令

- `/arxiv-init <id>` - 初始化并自动设为当前上下文
- `/arxiv-read` - 阅读当前活跃论文
