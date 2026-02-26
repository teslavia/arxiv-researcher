---
name: arxiv-cli
description: 统一 arXiv CLI 技能。通过 `arxiv <subcommand>` 完成搜索、初始化、阅读、复现、实验、部署与贡献全流程。
---

# arxiv CLI Super Skill

## 定位

本技能是 arXiv Researcher 的统一入口。所有能力都通过同一个命令暴露：

```bash
arxiv <subcommand> [options]
```

建议先执行：

```bash
arxiv --help
```

## 全局安装

```bash
pip install -e .
```

安装后可直接使用 `arxiv` 命令。

## 子命令总览

### 1) 发现与筛选

```bash
arxiv search --search "speculative decoding" --max 10
arxiv fetch --search "speculative decoding" --max 10
arxiv daily "LLM inference" --days 7 --max 15 --code-only
```

- `search`: 按关键词检索 arXiv，支持 GitHub 代码仓库信息增强
- `fetch`: `search` 的兼容别名
- `daily`: 获取最近 N 天论文简报，可选仅保留有代码论文

关键参数：
- `search`: `--search/-s`(必填), `--max/-m`, `--json/-j`
- `daily`: `topic`(必填), `--days/-d`, `--max/-m`, `--code-only/-c`, `--json/-j`

### 2) 项目初始化与上下文

```bash
arxiv init 2401.12345
arxiv init https://arxiv.org/abs/2401.12345
arxiv context
arxiv context 2401.12345
arxiv context --clear
```

- `init`: 初始化论文项目目录（可选跳过 PDF 下载）
- `context`: 查看/切换当前活跃论文上下文

关键参数：
- `init`: `arxiv_id`(必填), `--no-pdf`, `--update-index`
- `context`: `[id]`, `--get/-g`, `--clear/-c`, `--json/-j`

### 3) 阅读与知识沉淀

```bash
arxiv read
arxiv read 2401.12345 --status
arxiv read --mark-learned
arxiv brain index
arxiv brain ask "What is the core contribution?" --top-k 5
```

- `read`: 检查阅读状态、标记学习进度
- `brain`: 本地语义索引与检索（先 `index`，再 `ask`）

关键参数：
- `read`: `[id]`, `--status/-s`, `--mark-learned/-m`
- `brain`: `index` 或 `ask <text> [--top-k N]`

### 4) 复现与工程化

```bash
arxiv repro --repo owner/repo
arxiv repro --scan-only --json
arxiv lab list
arxiv lab inference
arxiv lab all
arxiv deploy --target coreml
arxiv deploy --target tensorrt --quantize int8
arxiv dataset --output playground/dataset_sft.jsonl
arxiv fix "python playground/inference_demo.py"
```

- `repro`: clone 仓库、依赖扫描、生成环境脚本
- `lab`: 在 `playground/` 生成实验脚手架
- `deploy`: 生成端侧部署脚本模板
- `dataset`: 生成 SFT 数据集草稿
- `fix`: 执行命令并生成问题诊断提示

关键参数：
- `repro`: `[id]`, `--repo/-r`, `--scan-only/-s`, `--json/-j`
- `lab`: `[type]`(默认 `list`，支持 `all`)
- `deploy`: `--target`, `--quantize`, `--id`
- `dataset`: `--id`, `--output`
- `fix`: `command`(必填), `--id`

### 5) 扩展与开源贡献

```bash
arxiv extend list
arxiv extend create podcast -i "生成论文播客脚本"
arxiv extend get podcast
arxiv extend delete podcast

arxiv contrib issue
arxiv contrib pr
arxiv contrib blog
arxiv contrib all --json
```

- `extend`: 管理自定义扩展动作
- `contrib`: 生成 Issue/PR/Blog 贡献材料

关键参数：
- `extend`: `action`, `[name]`, `--instruction/-i`, `--json/-j`
- `contrib`: `type(issue|pr|blog|all)`, `[id]`, `--json/-j`

## 推荐操作顺序

```text
search/daily -> init -> read -> repro -> lab/deploy/dataset -> contrib
```

## 故障排查

- 命令不存在：确认已执行 `pip install -e .`
- 未找到论文项目：先执行 `arxiv init <id>` 或 `arxiv context <id>`
- 参数帮助：执行 `arxiv <subcommand> --help`
