---
name: arxiv-repro
description: 复现 arXiv 论文代码，Clone 仓库、分析依赖、生成环境配置。用法：/arxiv-repro [--repo owner/repo]
---

# 复现论文代码

## 功能

Clone 论文官方代码仓库，分析依赖，生成环境配置脚本，记录复现日志。

## 用法

```
/arxiv-repro [--repo owner/repo]
```

## 参数

- 无参数: 使用当前活跃论文的官方仓库
- `--repo owner/repo`: 指定 GitHub 仓库

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/repro.py [--repo owner/repo]
```

## 工作流

1. **Clone 代码**: 将仓库克隆到 `src/` 目录
2. **分析依赖**: 扫描 `requirements.txt`, `setup.py`, `environment.yml`
3. **生成环境脚本**: 创建 `env_setup.sh`（Conda/pip/Docker）
4. **识别模型**: 自动检测 HuggingFace 模型链接
5. **创建 Demo**: 复制推理模板到 `playground/`
6. **记录日志**: 更新 `REPRODUCTION.md`

## 生成的文件

- `env_setup.sh` - 一键环境配置
- `playground/inference_demo.py` - 最小可运行示例
- `REPRODUCTION.md` - 复现日志（显存、延迟等）

## 下载模型权重

```bash
huggingface-cli download <model_id> --local-dir models/
```

## 相关指令

- `/arxiv-read` - 先阅读理解论文
- `/arxiv-lab` - 进一步工程化实验
