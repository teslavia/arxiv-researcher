#!/usr/bin/env python3
"""Lab script generator for arxiv papers - creates playground scripts."""

import argparse
import json
import shutil
import sys
from pathlib import Path

ARXIV_ROOT = Path("/Volumes/TMAC/Satoshi/DEV/mac/knowledge/arxiv")
CONTEXT_FILE = ARXIV_ROOT / ".context"
SKILL_DIR = Path(__file__).parent.parent
ASSETS_DIR = SKILL_DIR / "assets"


def get_current_context() -> dict | None:
    """Get current paper context."""
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return None


def find_project(arxiv_id: str | None) -> Path | None:
    """Find project directory."""
    if arxiv_id is None:
        ctx = get_current_context()
        if ctx:
            return Path(ctx["path"])
        return None

    for category_dir in ARXIV_ROOT.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            for project_dir in category_dir.iterdir():
                if project_dir.name.startswith(arxiv_id):
                    return project_dir
    return None


# Templates for different script types
TEMPLATES = {
    "demo": "inference_demo_template.py",
    "api": "api_template.py",
    "onnx": "onnx_export_template.py",
    "benchmark": "benchmark_template.py",
}


def create_script(project_dir: Path, script_type: str) -> Path | None:
    """Create a script from template."""
    playground_dir = project_dir / "playground"
    playground_dir.mkdir(exist_ok=True)

    template_name = TEMPLATES.get(script_type)
    if not template_name:
        print(f"❌ Unknown script type: {script_type}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return None

    template_path = ASSETS_DIR / template_name

    # Map template to output filename
    output_names = {
        "demo": "inference_demo.py",
        "api": "api.py",
        "onnx": "export_onnx.py",
        "benchmark": "benchmark.py",
    }

    output_path = playground_dir / output_names[script_type]

    if template_path.exists():
        shutil.copy(template_path, output_path)
        print(f"✅ Created: {output_path}")
        return output_path
    else:
        # Generate inline if template doesn't exist
        print(f"⚠️  Template not found: {template_path}")
        print(f"   Creating minimal {script_type} script...")

        if script_type == "api":
            content = generate_api_template()
        elif script_type == "onnx":
            content = generate_onnx_template()
        elif script_type == "benchmark":
            content = generate_benchmark_template()
        else:
            return None

        output_path.write_text(content)
        print(f"✅ Created: {output_path}")
        return output_path


def generate_api_template() -> str:
    return '''#!/usr/bin/env python3
"""FastAPI service wrapper for the model."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="Model API", version="1.0.0")

# TODO: Import and initialize your model
# from src.model import Model
# model = Model.load("../models/checkpoint.pt")


class PredictRequest(BaseModel):
    """Request schema."""
    input: str
    # Add more fields as needed


class PredictResponse(BaseModel):
    """Response schema."""
    output: str
    # Add more fields as needed


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """Run inference."""
    try:
        # TODO: Implement inference
        # result = model.predict(request.input)
        result = "TODO: implement"
        return PredictResponse(output=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


def generate_onnx_template() -> str:
    return '''#!/usr/bin/env python3
"""Export model to ONNX format."""

import argparse
from pathlib import Path

# TODO: Import your model framework
# import torch
# import torch.onnx


def export_to_onnx(model_path: Path, output_path: Path, opset_version: int = 14):
    """Export model to ONNX format."""
    print(f"Loading model from {model_path}...")
    # TODO: Load your model
    # model = torch.load(model_path)
    # model.eval()

    print(f"Exporting to {output_path}...")
    # TODO: Create dummy input matching your model's input shape
    # dummy_input = torch.randn(1, 3, 224, 224)

    # TODO: Export
    # torch.onnx.export(
    #     model,
    #     dummy_input,
    #     output_path,
    #     opset_version=opset_version,
    #     input_names=["input"],
    #     output_names=["output"],
    #     dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}}
    # )

    print(f"✅ Exported to {output_path}")
    raise NotImplementedError("Implement ONNX export for your model")


def main():
    parser = argparse.ArgumentParser(description="Export model to ONNX")
    parser.add_argument("--model", "-m", type=Path, default=Path("../models/model.pt"),
                        help="Path to model checkpoint")
    parser.add_argument("--output", "-o", type=Path, default=Path("../models/model.onnx"),
                        help="Output ONNX path")
    parser.add_argument("--opset", type=int, default=14, help="ONNX opset version")
    args = parser.parse_args()

    export_to_onnx(args.model, args.output, args.opset)


if __name__ == "__main__":
    main()
'''


def generate_benchmark_template() -> str:
    return '''#!/usr/bin/env python3
"""Benchmark model performance."""

import argparse
import gc
import time
from pathlib import Path

# TODO: Import your framework
# import torch


def measure_latency(model, input_data, num_warmup: int = 5, num_runs: int = 20):
    """Measure inference latency."""
    # Warmup
    for _ in range(num_warmup):
        _ = model(input_data)

    # Measure
    latencies = []
    for _ in range(num_runs):
        start = time.perf_counter()
        _ = model(input_data)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # ms

    return {
        "mean_ms": sum(latencies) / len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
    }


def measure_memory():
    """Measure GPU memory usage."""
    try:
        import torch
        if torch.cuda.is_available():
            return {
                "allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
                "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024 / 1024,
            }
    except ImportError:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description="Benchmark model")
    parser.add_argument("--model", "-m", type=Path, default=Path("../models/model.pt"),
                        help="Path to model")
    parser.add_argument("--runs", "-r", type=int, default=20, help="Number of runs")
    args = parser.parse_args()

    print(f"🔄 Loading model from {args.model}...")
    # TODO: Load your model
    # model = load_model(args.model)

    print("📊 Running benchmark...")
    # TODO: Create input
    # input_data = create_sample_input()

    # TODO: Run benchmark
    # latency = measure_latency(model, input_data, num_runs=args.runs)
    # memory = measure_memory()

    # print(f"\\n📈 Results:")
    # print(f"   Latency: {latency['mean_ms']:.2f} ms (min: {latency['min_ms']:.2f}, max: {latency['max_ms']:.2f})")
    # if memory:
    #     print(f"   GPU Memory: {memory['max_allocated_mb']:.2f} MB")

    raise NotImplementedError("Implement benchmark for your model")


if __name__ == "__main__":
    main()
'''


def main():
    parser = argparse.ArgumentParser(description="Create playground scripts")
    parser.add_argument("type", nargs="?", choices=list(TEMPLATES.keys()) + ["all", "list"],
                        default="list", help="Script type to create")
    parser.add_argument("--id", help="arXiv ID (uses context if omitted)")
    args = parser.parse_args()

    if args.type == "list":
        print("📦 Available script types:\n")
        for name, template in TEMPLATES.items():
            print(f"   {name:10} - {template}")
        print(f"\n💡 Usage: lab.py <type> [--id <arxiv_id>]")
        print(f"   Example: lab.py demo")
        print(f"   Example: lab.py all")
        return

    project_dir = find_project(args.id)
    if project_dir is None:
        print("❌ No project found. Specify --id or set context first.")
        sys.exit(1)

    print(f"📁 Project: {project_dir.name}")

    if args.type == "all":
        for script_type in TEMPLATES.keys():
            create_script(project_dir, script_type)
    else:
        create_script(project_dir, args.type)

    print(f"\n📂 Scripts created in: {project_dir / 'playground'}")


if __name__ == "__main__":
    main()
