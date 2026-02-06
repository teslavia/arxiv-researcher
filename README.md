# arXiv Researcher

> **将论文变成代码资产** — Claude Code 技能，打造工程师的个人科研闭环

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 为什么需要 arXiv Researcher？

作为工程师，你可能经历过：

- 📄 **论文堆积如山** — 收藏了 100 篇 PDF，真正读完的不到 10 篇
- 🔧 **复现困难重重** — 环境配不对、代码跑不通、结果对不上
- 🗂️ **知识碎片化** — 笔记散落各处，半年后完全想不起来
- 🚫 **无法落地** — 学术代码难以工程化，最终只能放弃

**arXiv Researcher** 用标准化的 SOP 解决这些问题：

```
Discovery → Learning → Verification → Engineering → Contribution
  搜索        阅读         复现          工程化         开源贡献
```

## 30 秒快速开始

### 1. 安装

```bash
git clone https://github.com/your-repo/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

### 2. 重启 Claude Code

### 3. 开始使用

```bash
# 搜索论文
/arxiv-search speculative decoding

# 初始化项目
/arxiv-init 2401.12345

# 深度阅读
/arxiv-read

# 复现代码
/arxiv-repro

# 工程化实验
/arxiv-lab api

# 准备开源贡献
/arxiv-contrib
```

## 核心功能

### 🔍 智能搜索 (`/arxiv-search`)

不只是搜索 — 自动标注 GitHub Stars，优先推荐有代码的论文。

```
/arxiv-search "LLM inference optimization"

📄 Results:
1. [2401.12345] Speculative Decoding for LLMs ⭐ 1.2k
2. [2401.54321] Fast KV Cache Compression ⭐ 856
3. [2312.98765] Efficient Attention Mechanisms (No code)
```

### 📁 标准化项目空间 (`/arxiv-init`)

每篇论文一个独立"实验室"，结构清晰，支持版本控制。

```
2401.12345_speculative_decoding/
├── paper.pdf           # 原始论文
├── SUMMARY.md          # 结构化笔记
├── REPRODUCTION.md     # 复现日志
├── src/                # 官方代码
├── models/             # 模型权重 (gitignored)
├── playground/         # 你的实验脚本
└── contribution/       # Issue/PR/Blog 草稿
```

### 📖 深度阅读 (`/arxiv-read`)

AI 辅助阅读，自动生成结构化笔记：

- **Context** — 解决什么问题？
- **Key Insight** — 核心创新一句话
- **Method** — 架构与关键公式
- **Results** — 性能对比表格
- **Open Questions** — 待探索的问题

### 🔬 一键复现 (`/arxiv-repro`)

自动化复现流程：

1. Clone 官方仓库到 `src/`
2. 分析依赖，生成 `env_setup.sh`
3. 识别 HuggingFace 模型链接
4. 创建最小推理 Demo
5. 记录显存、延迟到 `REPRODUCTION.md`

### 🛠️ 工程化实验室 (`/arxiv-lab`)

**AI-Native 工程流**: 即使是全新架构的论文，也能快速工程化。

1.  **生成骨架**: `/arxiv-lab` 提供符合最佳实践的 Python/PyTorch 脚手架。
2.  **AI 填充**: 利用 Claude 理解论文上下文的能力，填充具体逻辑。

支持模版：

```bash
/arxiv-lab demo      # 通用推理骨架
/arxiv-lab train     # 训练循环 (Dataset/Loader/Loop)
/arxiv-lab viz       # 模型内部可视化 (Hooks)
/arxiv-lab api       # FastAPI 微服务骨架
/arxiv-lab onnx      # ONNX 导出与量化
/arxiv-lab benchmark # 延迟与吞吐量压测
```

### 🌟 开源贡献生成器 (`/arxiv-contrib`)

一键生成专业的开源贡献材料：

- **Issue 模板** — 复现失败时的完整环境信息
- **PR 模板** — Bug 修复的规范描述
- **Blog 模板** — 复现报告转技术博客

## 完整指令列表

| 指令 | 功能 | 示例 |
|------|------|------|
| `/arxiv-search` | 搜索论文 | `/arxiv-search "vision transformer"` |
| `/arxiv-daily` | 每日简报 | `/arxiv-daily "LLM" --code-only` |
| `/arxiv-init` | 初始化项目 | `/arxiv-init 2401.12345` |
| `/arxiv-context` | 切换上下文 | `/arxiv-context` |
| `/arxiv-read` | 深度阅读 | `/arxiv-read` |
| `/arxiv-repro` | 复现代码 | `/arxiv-repro --repo owner/repo` |
| `/arxiv-lab` | 工程实验 | `/arxiv-lab api` |
| `/arxiv-contrib` | 开源贡献 | `/arxiv-contrib all` |
| `/arxiv-extend` | 自定义扩展 | `/arxiv-extend create translate -i "翻译为中文"` |

## 典型工作流

### 场景：复现一篇 Speculative Decoding 论文

```bash
# Day 1: 发现
/arxiv-search "speculative decoding 2024"
# 找到感兴趣的论文 2401.12345

# Day 1: 初始化
/arxiv-init 2401.12345
# 自动下载 PDF，创建项目空间

# Day 2: 阅读
/arxiv-read
# AI 辅助生成 SUMMARY.md

# Day 3: 复现
/arxiv-repro
# Clone 代码，配置环境，运行 Demo

# Day 4: 工程化
/arxiv-lab api
# 封装为 FastAPI 服务

# Day 5: 贡献
/arxiv-contrib blog
# 生成技术博客分享复现经验
```

## 扩展系统

用自然语言定义新工作流：

```bash
# 创建播客脚本生成器
/arxiv-extend create podcast -i "生成 5 分钟播客脚本，讨论论文优缺点"

# 创建 Twitter 线程生成器
/arxiv-extend create twitter -i "生成 Twitter 线程介绍论文亮点"

# 创建 Notion 导出器
/arxiv-extend create notion -i "格式化为 Notion 数据库导入格式"

# 查看所有扩展
/arxiv-extend list
```

## 系统要求

### 必需

- [Claude Code](https://github.com/anthropics/claude-code) CLI
- Python 3.8+
- Git

### 推荐

- `pdftotext` (Poppler) — PDF 文本提取
- `gh` (GitHub CLI) — 仓库操作
- `huggingface-cli` — 模型权重下载

```bash
# macOS
brew install poppler gh
pip install huggingface_hub

# Ubuntu
apt install poppler-utils gh
pip install huggingface_hub
```

## 配置

安装后，论文项目存储在：

```
~/knowledge/arxiv/
├── README.md          # 全局看板
├── .context           # 当前活跃论文
├── .extensions/       # 自定义扩展
└── 2401.CS/           # 按年月分类
    └── 2401.12345_paper_title/
```

可通过编辑主 SKILL.md 修改根目录位置。

## 目录结构

```
arxiv-researcher/
├── README.md              # 本文件
├── SKILL.md               # 主技能定义
├── install.sh             # 一键安装脚本
├── scripts/               # 核心脚本
│   ├── arxiv_fetch.py     # 搜索与下载
│   ├── init_project.py    # 项目初始化
│   ├── context.py         # 上下文管理
│   ├── daily.py           # 每日简报
│   ├── read.py            # 阅读辅助
│   ├── repro.py           # 复现工具
│   ├── lab.py             # 工程实验
│   ├── contrib.py         # 贡献生成
│   ├── utils.py           # 共享工具类
│   └── extend.py          # 扩展系统
├── assets/                # 通用工程模板
│   ├── api_template.py
│   ├── onnx_export_template.py
│   ├── benchmark_template.py
│   ├── train_demo_template.py
│   ├── viz_attention_template.py
│   ├── inference_demo_template.py
│   ├── ISSUE_TEMPLATE.md
│   └── PR_TEMPLATE.md
└── skills/                # 子技能定义
    ├── arxiv-search/
    ├── arxiv-init/
    ├── arxiv-daily/
    ├── arxiv-context/
    ├── arxiv-read/
    ├── arxiv-repro/
    ├── arxiv-lab/
    ├── arxiv-contrib/
    └── arxiv-extend/
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT License

---

**让每一篇论文都成为可复用的代码资产。**
