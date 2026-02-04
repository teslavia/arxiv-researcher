---
name: arxiv-lab
description: 在 playground/ 中创建实验脚本，进行接口封装或 ONNX 转换。用法：/arxiv-lab [type]
---

# 工程化实验室

## 功能

在 `playground/` 目录中创建实验脚本，进行 API 封装、ONNX 导出、性能优化等工程化工作。

## 用法

```
/arxiv-lab [type]
```

## 参数

- 无参数: 创建基础推理脚本
- `type`: 脚本类型
  - `demo` - 最小可运行示例
  - `api` - FastAPI 服务封装
  - `onnx` - ONNX 导出脚本
  - `benchmark` - 性能基准测试

## 执行

```bash
python3 ~/.claude/skills/arxiv-researcher/scripts/lab.py [type]
```

## 创建的脚本

### demo (默认)
- `playground/inference_demo.py` - 基于模板的推理示例

### api
- `playground/api.py` - FastAPI 服务
- 包含健康检查、推理端点、错误处理

### onnx
- `playground/export_onnx.py` - ONNX 导出脚本
- 包含模型简化、量化选项

### benchmark
- `playground/benchmark.py` - 性能测试
- 测量延迟、吞吐量、显存占用

## 代码规范

- 移除硬编码路径
- 添加 Type Hint
- 使用 Black/Ruff 格式化

## 相关指令

- `/arxiv-repro` - 先完成复现
- `/arxiv-contrib` - 准备开源贡献
