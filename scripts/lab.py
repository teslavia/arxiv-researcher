#!/usr/bin/env python3
"""Lab script generator for arxiv papers - creates playground scripts."""

import argparse
import shutil
import sys
from pathlib import Path

# Add local directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils import find_project

SKILL_DIR = Path(__file__).parent.parent
ASSETS_DIR = SKILL_DIR / "assets" / "templates"

# Templates for different script types
TEMPLATES = {
    "demo": "inference_demo_template.py",
    "train": "train_demo_template.py",
    "viz": "viz_attention_template.py",
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
        "train": "train_demo.py",
        "viz": "viz_attention.py",
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
        print(f"⚠️  Template not found: {template_path}")
        return None

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
        print(f"\n💡 Usage: /arxiv-lab <type> [--id <arxiv_id>]")
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
