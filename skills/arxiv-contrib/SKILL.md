---
name: arxiv-contrib
description: 生成开源贡献材料 (Issue/PR/Blog)。用法：/arxiv-contrib [issue|pr|blog|all]
---

# 开源贡献生成器

## 功能

在 `contribution/` 目录生成 Issue、PR、Blog 模板，帮助建立开源技术影响力。

## 用法

```
/arxiv-contrib [type]
```

## 参数

- 无参数或 `all`: 生成所有模板
- `issue`: 仅生成 Issue 模板
- `pr`: 仅生成 PR 模板
- `blog`: 仅生成 Blog 模板

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/contrib.py [type]
```

## 生成的文件

### ISSUE.md
复现失败时的 Issue 模板：
- 环境信息（OS、Python、CUDA 版本）
- 复现步骤
- 错误日志
- 预期 vs 实际行为

### PR.md
Bug 修复或环境适配的 PR 描述：
- 问题描述
- 解决方案
- 测试结果
- Checklist

### BLOG.md
复现报告转技术博客：
- 论文简介
- 核心方法
- 复现过程
- 性能数据
- 总结与展望

## 相关指令

- `/arxiv-repro` - 先完成复现
- `/arxiv-lab` - 工程化改造后再贡献
