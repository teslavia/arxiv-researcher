---
name: arxiv-init
description: 初始化 arXiv 论文项目空间，下载 PDF。用法：/arxiv-init <arxiv_id 或 URL>
---

# 初始化论文项目

## 功能

下载 arXiv 论文 PDF，创建标准化项目目录结构，设置为当前活跃论文。

## 用法

```
/arxiv-init <arxiv_id | URL>
```

## 参数

- `<arxiv_id>`: arXiv ID（如 `2401.12345`）
- `<URL>`: arXiv 论文 URL（如 `https://arxiv.org/abs/2401.12345`）

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/init_project.py <arxiv_id>
```

## 创建的目录结构

```
/knowledge/arxiv/<YYMM>.<Category>/<ID>_<SnakeTitle>/
├── paper.pdf         # 论文 PDF
├── info.yaml         # 元数据
├── SUMMARY.md        # 阅读笔记（待填写）
├── REPRODUCTION.md   # 复现日志（待填写）
├── .gitignore        # 忽略大文件
├── env_setup.sh      # 环境配置脚本
├── src/              # 代码目录
├── models/           # 模型权重
├── data/             # 数据目录
├── playground/       # 实验脚本
└── contribution/     # 开源贡献材料
```

## 相关指令

- `/arxiv-search <query>` - 搜索论文
- `/arxiv-read` - 深度阅读论文
- `/arxiv-context` - 查看当前活跃论文
