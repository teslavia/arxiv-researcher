---
name: arxiv-extend
description: 创建自定义 arXiv 工作流扩展。用法：/arxiv-extend <name> <instruction>
---

# 扩展系统

## 功能

用自然语言定义新的工作流，创建自定义指令扩展。

## 用法

```
/arxiv-extend create <name> -i "<instruction>"
/arxiv-extend list
/arxiv-extend run <name>
```

## 参数

- `create <name>`: 创建名为 `<name>` 的扩展
- `-i "<instruction>"`: 扩展的自然语言指令
- `list`: 列出所有已创建的扩展
- `run <name>`: 运行指定扩展

## 执行

```bash
# 创建扩展
python3 ~/.claude/skills/arxiv-researcher/scripts/extend.py create podcast -i "生成播客脚本讨论论文优缺点"

# 列出扩展
python3 ~/.claude/skills/arxiv-researcher/scripts/extend.py list

# 运行扩展
python3 ~/.claude/skills/arxiv-researcher/scripts/extend.py run podcast
```

## 示例扩展

```bash
# 翻译笔记
python3 scripts/extend.py create translate -i "将 SUMMARY.md 翻译为中文"

# Notion 导出
python3 scripts/extend.py create notion -i "格式化为 Notion 导入格式"

# 播客脚本
python3 scripts/extend.py create podcast -i "生成播客脚本讨论论文优缺点"

# Twitter 线程
python3 scripts/extend.py create twitter -i "生成 Twitter 线程介绍论文亮点"
```

## 扩展存储

扩展定义保存在 `/knowledge/arxiv/.extensions/` 目录

## 相关指令

- `/arxiv-read` - 先生成 SUMMARY.md
- `/arxiv-contrib` - 内置的贡献模板
