# arXiv Researcher

> **将论文转化为工程资产** — Claude Code 原生科研助手，打造从阅读到落地的完整闭环。

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

## 🚀 痛点与解决方案

作为工程师，你可能经历过：
- 📄 **收藏癖**: 收藏了 100 篇 PDF，真正读完的不到 10 篇。
- 🔧 **复现难**: 环境配不对、代码跑不通、依赖冲突。
- 🚫 **落地难**: 学术代码难以直接用于生产环境。
- 🗂️ **知识碎片**: 笔记散落各处，回顾困难。

**arXiv Researcher** 提供标准化的 **SOP (标准作业程序)**：

```mermaid
graph LR
    A[🔍 发现] --> B[📖 阅读]
    B --> C[🔬 复现]
    C --> D[🛠️ 工程化]
    D --> E[🌟 贡献]
```

## ⚡️ 30 秒快速开始

### 1. 安装

```bash
git clone https://github.com/teslavia/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

### 2. 使用

重启 Claude Code 后即可使用：

```bash
# 1. 搜索论文 (自动标注 GitHub Stars ⭐)
/arxiv-search "speculative decoding"

# 2. 初始化项目 (下载 PDF，建立目录)
/arxiv-init 2401.12345

# 3. 深度阅读 (生成结构化笔记)
/arxiv-read

# 4. 一键复现 (Clone 代码，分析依赖)
/arxiv-repro

# 5. 工程化实验 (生成 API/ONNX/训练骨架)
/arxiv-lab api

# 6. 开源贡献 (生成 Issue/PR/技术博客)
/arxiv-contrib blog
```

## 🌟 核心功能

### 🔍 智能搜索 (`/arxiv-search`)
不只是搜索，更是**筛选**。
- 自动抓取 GitHub Stars，快速判断影响力。
- 优先展示包含代码实现的论文。
- 过滤无关结果，直达核心。

### 📁 标准化项目空间 (`/arxiv-init`)
每篇论文都是一个独立的**工程项目**。
- `paper.pdf`: 原始论文。
- `src/`: 官方代码实现 (gitignored)。
- `playground/`: 你的实验与魔改代码。
- `SUMMARY.md`: 结构化知识库。

### 📚 沉淀式知识库 (Knowledge Base)
**拒绝"收藏夹吃灰"，打造你的第二大脑。**

- **自定义存储**: 安装时可选择知识库路径 (默认 `~/knowledge/arxiv`)，数据完全掌控。
- **本地优先**: 所有 PDF、代码、笔记存储在本地，无需联网即可访问。
- **AI 就绪**: 结构化的笔记天然适合作为 RAG (检索增强生成) 的语料。
- **上下文持久化**: `/arxiv-context` 瞬间恢复"科研现场"。

#### 🗃️ 目录结构 (Directory Structure)

```text
~/knowledge/arxiv/             # 根目录 (可配置)
├── README.md                  # 全局看板
├── .context                   # 状态文件
├── cs.CL/                     # arXiv 类别
│   └── 2401.12345_title/      # 论文项目
│       ├── info.yaml          # 元数据
│       ├── paper.pdf          # 论文原件
│       ├── SUMMARY.md         # 深度笔记
│       ├── REPRODUCTION.md    # 复现日志
│       ├── src/               # 官方源码
│       └── playground/        # 实验代码
└── ...
```

### 📖 深度阅读 (`/arxiv-read`)
AI 辅助阅读，提取关键信息：
- **Context**: 解决什么核心问题？
- **Method**: 架构与创新点。
- **Results**: 关键指标对比。
- **Open Questions**: 潜在的改进方向。

### 🛠️ 工程化实验室 (`/arxiv-lab`)
**打通学术代码与生产环境的最后一公里。**
生成通用的深度学习脚手架，让 Claude 结合论文上下文自动填充逻辑。

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `demo` | 通用推理骨架 | 快速验证模型效果 |
| `api` | FastAPI 微服务 | 生产环境部署 |
| `train`| PyTorch 训练循环 | 复现训练过程 |
| `onnx` | ONNX 导出工具 | 模型量化与加速 |
| `viz` | 可视化 Hook | 解释模型注意力/特征 |

### 🌟 开源贡献生成器 (`/arxiv-contrib`)
将你的复现经验转化为社区贡献。
- **Issue**: 自动生成包含环境信息的复现失败报告。
- **PR**: 提交 Bug 修复或新功能。
- **Blog**: 一键生成技术博客，分享复现心得。

## 📂 项目结构

```text
arxiv-researcher/
├── assets/                # 通用工程模板 (Scaffolds)
│   ├── api_template.py    # FastAPI 骨架
│   ├── train_template.py  # 训练循环骨架
│   └── ...
├── scripts/               # 核心 Python 脚本
│   ├── arxiv_fetch.py     # 搜索与元数据
│   ├── lab.py             # 工程化实验逻辑
│   └── ...
├── skills/                # Claude Code 技能定义
│   ├── arxiv-search/
│   └── ...
└── knowledge/             # (运行时生成) 你的本地论文库
```

## 🧩 扩展系统

用自然语言定义你的专属工作流：

```bash
# 创建播客脚本生成器
/arxiv-extend create podcast -i "生成 5 分钟播客脚本，讨论论文优缺点"

# 创建 Notion 导入格式
/arxiv-extend create notion -i "格式化为 Notion 数据库导入格式"
```

## 🤝 贡献

欢迎提交 PR！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 License

MIT License
