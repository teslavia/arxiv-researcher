---
name: arxiv-lab
description: 在 playground/ 中创建通用深度学习脚手架，用于工程化实验。用法：/arxiv-lab [type]
---

# 工程化实验室 (Engineering Lab)

## 核心理念

`/arxiv-lab` 不再尝试生成特定模型的硬编码代码，而是生成 **通用深度学习脚手架 (Generic Scaffolding)**。
这种 "AI-Native" 的工作流利用 Claude 的理解能力，将通用骨架适配到当前论文的具体上下文中。

## 用法

```bash
/arxiv-lab [type]
```

## 工作流：Scaffold + In-filling

1. **生成骨架**: 运行指令生成通用模板文件。
2. **AI 填充**: 提示 Claude 结合论文上下文完善代码。

### 示例

```bash
# 1. 生成 API 服务骨架
/arxiv-lab api

# 2. 让 Claude 完善逻辑 (直接在对话中输入)
"读取 playground/api.py，结合 src/ 中的模型定义，完善 load_model 和 predict 函数。"
```

## 支持的类型

| 类型 | 描述 | 适用场景 |
|------|------|----------|
| `demo` | **通用推理骨架** (默认) | 定义 Input -> Model -> Output 的标准流程 |
| `train`| **通用训练循环** | 包含 Dataset, DataLoader, Loss, Optimizer 的标准结构 |
| `viz`  | **通用 Hook 可视化** | 用于提取 Feature Map 或 Attention Map |
| `api`  | **FastAPI 服务骨架** | 包含生命周期管理、健康检查、Pydantic 定义 |
| `onnx` | **通用导出脚本** | 包含动态轴 (Dynamic Axes) 配置和 Dummy Input 生成 |
| `benchmark` | **通用性能测试** | 包含 Warmup, Latency (P95/P99), Throughput 计算 |

## 执行逻辑

```python
python3 ~/.claude/skills/arxiv-researcher/scripts/lab.py [type]
```

## 模板特点

- **模型无关**: 适用于 CV (ResNet), NLP (Transformer), RL (PPO) 等所有架构。
- **最佳实践**: 内置了 `torch.no_grad()`, `model.eval()`, `pydantic` 校验, `pathlib` 路径处理等工程规范。
- **明确引导**: 关键位置留有 `TODO` 注释，引导 AI 或用户填充具体逻辑。
