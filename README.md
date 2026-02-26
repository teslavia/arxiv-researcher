<div align="center">
  <h1>arXiv Researcher</h1>
  <p><strong>将论文转化为工程资产（Code as Asset）</strong></p>
  <p>统一 CLI + 本地知识库 + 可复现实验脚手架</p>
</div>

<p align="center">
  <img src="assets/media/demo.gif" alt="Demo" width="800">
</p>

<div align="center">
  <a href="https://github.com/anthropics/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-Skill-blue" alt="Claude Code Skill"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
</div>

> 单文件多语言文档：中文主文档 + English/Japanese quick guide。
> Claude Code 统一入口：`/arxiv-cli`

## What Changed (Recent Refactor)

- 标准 Python 包结构：核心代码迁移到 `arxiv_engine/`。
- 统一命令入口：采用 Click 聚合为 `arxiv <subcommand>`。
- 技能收拢：`skills/` 仅保留 `skills/arxiv-cli/`。
- 安装方式统一：`install.sh` 使用 `python3 -m pip install -e .`。
- 依赖文件收拢：`requirements*.txt` 合并为单一 `requirements.txt`。

## Quick Start

### 1) 安装

```bash
git clone https://github.com/teslavia/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

如果遇到系统 Python 的 PEP 668 限制，请使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

可选增强依赖：

```bash
pip install -r requirements.txt
```

### 2) 查看统一命令

```bash
arxiv --help
```

### 3) Claude Code 最新使用方式

在 Claude Code 中，统一 slash 指令为：`/arxiv-cli`

推荐写法：

```text
/arxiv-cli 搜索最近 7 天 speculative decoding 且有代码的论文
/arxiv-cli 初始化 2401.12345 并切换为当前上下文
/arxiv-cli 复现当前论文并给出依赖安装建议
```

如果你希望固定为命令执行，也可以这样写：

```text
/arxiv-cli 执行: arxiv daily "speculative decoding" --days 7 --code-only
```

说明：`/arxiv-*` 分散指令为历史写法，统一入口已切换到 `/arxiv-cli`；底层执行仍是 `arxiv <subcommand>`。

## Core Commands (Terminal)

### 发现与筛选

```bash
arxiv search --search "speculative decoding" --max 10
arxiv fetch --search "speculative decoding" --max 10   # search 的兼容别名
arxiv daily "LLM inference" --days 7 --max 15 --code-only
```

### 初始化与上下文

```bash
arxiv init 2401.12345
arxiv context
arxiv context 2401.12345
arxiv context --clear
```

### 阅读与知识沉淀

```bash
arxiv read
arxiv read --status
arxiv read --mark-learned

arxiv brain index
arxiv brain ask "What is the core contribution?" --top-k 5
```

### 复现与工程化

```bash
arxiv repro --repo owner/repo
arxiv lab list
arxiv lab all
arxiv deploy --target coreml
arxiv dataset --output playground/dataset_sft.jsonl
arxiv fix "python playground/inference_demo.py"
```

### 扩展与贡献

```bash
arxiv extend list
arxiv extend create podcast -i "生成论文播客脚本"

arxiv contrib issue
arxiv contrib pr
arxiv contrib blog
arxiv contrib all --json
```

## Recommended Workflow

```text
search/daily -> init -> read -> repro -> lab/deploy/dataset -> contrib
```

## Project Layout

```text
arxiv-researcher/
├── arxiv_engine/
│   ├── cli.py                 # 统一 CLI 入口（Click）
│   ├── core/
│   │   └── utils.py           # 共享工具
│   └── pipelines/             # 各业务流水线
│       ├── search.py
│       ├── init_project.py
│       ├── read.py
│       ├── repro.py
│       └── ...
├── assets/templates/          # 实验/部署模板
├── skills/arxiv-cli/SKILL.md  # 单一超级技能文档
├── requirements.txt           # 统一依赖
├── setup.py                   # console_scripts: arxiv
└── install.sh                 # 安装技能 + pip install -e .
```

## Command Migration (Old -> New)

| 旧指令 | 新命令 |
|---|---|
| `/arxiv-search <query>` | `arxiv search --search "<query>"` |
| `/arxiv-daily <topic>` | `arxiv daily "<topic>"` |
| `/arxiv-init <id>` | `arxiv init <id>` |
| `/arxiv-context [id]` | `arxiv context [id]` |
| `/arxiv-read` | `arxiv read` |
| `/arxiv-repro` | `arxiv repro` |
| `/arxiv-lab <type>` | `arxiv lab <type>` |
| `/arxiv-deploy ...` | `arxiv deploy ...` |
| `/arxiv-contrib ...` | `arxiv contrib ...` |
| `/arxiv-extend ...` | `arxiv extend ...` |

Claude Code 统一入口：

- 推荐：`/arxiv-cli <你的目标或任务>`
- 需要精确控制时：`/arxiv-cli 执行: arxiv <subcommand> ...`

Claude Code 场景建议：

- 新对话优先使用 `/arxiv-cli`。
- 仅在历史会话或旧模板中使用 `/arxiv-*` 兼容写法。

## Troubleshooting

- `arxiv: command not found`：确认已执行 `python3 -m pip install -e .`。
- 无当前论文上下文：先执行 `arxiv init <id>` 或 `arxiv context <id>`。
- `brain` 回退 hash embedding：安装 `requirements.txt` 中相关依赖（`sentence-transformers`）。
- 查看子命令帮助：`arxiv <subcommand> --help`。

---

## English Quick Guide

### Install

```bash
git clone https://github.com/teslavia/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

### Main CLI

```bash
arxiv --help
arxiv search --search "speculative decoding" --max 10
arxiv init 2401.12345
arxiv read
arxiv repro
arxiv lab api
arxiv deploy --target coreml
arxiv contrib blog
```

### Key Updates

- Unified package under `arxiv_engine/`
- Single CLI router: `arxiv <subcommand>`
- Consolidated skill: `skills/arxiv-cli/`
- Single dependency file: `requirements.txt`

---

## 日本語クイックガイド

### インストール

```bash
git clone https://github.com/teslavia/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

### 主要コマンド

```bash
arxiv --help
arxiv search --search "speculative decoding" --max 10
arxiv init 2401.12345
arxiv read
arxiv repro
arxiv lab api
arxiv deploy --target coreml
arxiv contrib blog
```

### 直近の変更

- `arxiv_engine/` へのパッケージ再編
- `arxiv <subcommand>` の統一 CLI
- `skills/arxiv-cli/` へのスキル統合
- 依存関係を `requirements.txt` に一本化

## Contributing

PR welcome. See `CONTRIBUTING.md`.

## License

MIT
