---
name: arxiv-search
description: 搜索 arXiv 论文，带 GitHub Stars 标注。用法：/arxiv-search <query>
---

# arXiv 论文搜索

## 功能

智能搜索 arXiv 论文，自动标注 GitHub Stars 和代码可用性。

## 用法

```
/arxiv-search <query> [--max N]
```

## 参数

- `<query>`: 搜索关键词（如 "speculative decoding", "LLM inference"）
- `--max N`: 最大返回数量（默认 10）

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/arxiv_fetch.py --search "<query>" --max 10
```

## 输出示例

```
1. [2401.12345] Speculative Decoding for LLMs ⭐ 1.2k
   Authors: ...
   GitHub: https://github.com/...

2. [2401.54321] Fast Inference with Draft Models
   Authors: ...
   (No code available)
```

## 相关指令

- `/arxiv-init <id>` - 下载并初始化论文项目
- `/arxiv-daily <topic>` - 获取每日论文简报
