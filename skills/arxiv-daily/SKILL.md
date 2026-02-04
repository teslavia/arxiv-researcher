---
name: arxiv-daily
description: 获取 arXiv 最近论文简报。用法：/arxiv-daily <topic>
---

# 每日论文简报

## 功能

获取指定主题的最新 arXiv 论文，支持过滤仅有代码的论文。

## 用法

```
/arxiv-daily <topic> [--days N] [--code-only]
```

## 参数

- `<topic>`: 研究主题（如 "LLM inference", "vision transformer"）
- `--days N`: 查看最近 N 天的论文（默认 7）
- `--code-only`: 仅显示有 GitHub 代码的论文

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/daily.py "<topic>" --days 7
```

## 输出示例

```
📅 arXiv Daily: LLM inference (Last 7 days)

1. [2401.12345] Speculative Decoding Improvements ⭐ 856
   Published: 2024-01-15
   GitHub: https://github.com/...

2. [2401.12346] Efficient KV Cache Compression
   Published: 2024-01-14
   (No code)

Found 15 papers, 8 with code.
```

## 相关指令

- `/arxiv-search <query>` - 更精确的搜索
- `/arxiv-init <id>` - 初始化感兴趣的论文
