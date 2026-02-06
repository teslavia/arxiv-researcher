#!/usr/bin/env python3
"""Reproduction helper for arxiv papers.

Clones code, downloads models, analyzes dependencies, generates environment setup.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Add local directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils import ARXIV_ROOT, CONTEXT_FILE, find_project, update_status


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


def get_github_repo(project_dir: Path) -> str | None:
    """Extract GitHub repo from info.yaml."""
    info_file = project_dir / "info.yaml"
    if info_file.exists():
        content = info_file.read_text()
        match = re.search(r'github_repo:\s*["\']?([^"\'\n]+)', content)
        if match and match.group(1).strip():
            return match.group(1).strip()
    return None


def clone_repo(repo: str, dest: Path) -> bool:
    """Clone GitHub repository."""
    if dest.exists() and any(dest.iterdir()):
        print(f"⚠️  src/ already exists, skipping clone")
        return True

    url = f"https://github.com/{repo}.git" if not repo.startswith("http") else repo
    print(f"📥 Cloning {url}...")

    try:
        subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True, timeout=300)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Clone failed: {e}")
        return False


def scan_dependencies(src_dir: Path) -> dict:
    """Scan source code for dependencies."""
    deps = {
        "python_imports": set(),
        "requirements_file": None,
        "setup_py": False,
        "pyproject": False,
        "conda_env": None,
        "dockerfile": False,
        "huggingface_models": set(),
    }

    # Check for config files
    if (src_dir / "requirements.txt").exists():
        deps["requirements_file"] = str(src_dir / "requirements.txt")
    if (src_dir / "setup.py").exists():
        deps["setup_py"] = True
    if (src_dir / "pyproject.toml").exists():
        deps["pyproject"] = True
    if (src_dir / "environment.yml").exists() or (src_dir / "environment.yaml").exists():
        deps["conda_env"] = str(list(src_dir.glob("environment.y*ml"))[0])
    if (src_dir / "Dockerfile").exists():
        deps["dockerfile"] = True

    # Scan Python files for imports and HF models
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(errors="ignore")

            # Extract imports
            for match in re.finditer(r'^(?:from|import)\s+(\w+)', content, re.MULTILINE):
                deps["python_imports"].add(match.group(1))

            # Find HuggingFace model references
            for match in re.finditer(r'["\']([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)["\']', content):
                candidate = match.group(1)
                if "/" in candidate and not candidate.startswith(("http", "/")):
                    deps["huggingface_models"].add(candidate)
        except Exception:
            continue

    deps["python_imports"] = sorted(deps["python_imports"])
    deps["huggingface_models"] = sorted(deps["huggingface_models"])

    return deps


def generate_env_setup(project_dir: Path, deps: dict) -> Path:
    """Generate environment setup script."""
    script_path = project_dir / "env_setup.sh"

    lines = [
        "#!/bin/bash",
        "# Auto-generated environment setup",
        f"# Project: {project_dir.name}",
        "",
        "set -e",
        "",
    ]

    if deps["conda_env"]:
        lines.extend([
            "# Conda environment found",
            f"conda env create -f {deps['conda_env']}",
            "",
        ])
    elif deps["requirements_file"]:
        lines.extend([
            "# Create virtual environment",
            "python -m venv venv",
            "source venv/bin/activate",
            "",
            f"pip install -r {deps['requirements_file']}",
            "",
        ])
    elif deps["setup_py"]:
        lines.extend([
            "# Install from setup.py",
            "python -m venv venv",
            "source venv/bin/activate",
            "pip install -e src/",
            "",
        ])
    else:
        # Generate requirements from imports
        common_packages = {
            "torch": "torch",
            "torchvision": "torchvision",
            "transformers": "transformers",
            "numpy": "numpy",
            "pandas": "pandas",
            "PIL": "Pillow",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "tensorflow": "tensorflow",
            "jax": "jax",
        }

        reqs = []
        for imp in deps["python_imports"]:
            if imp in common_packages:
                reqs.append(common_packages[imp])

        if reqs:
            lines.extend([
                "# Generated from imports (verify versions!)",
                "python -m venv venv",
                "source venv/bin/activate",
                f"pip install {' '.join(sorted(set(reqs)))}",
                "",
            ])

    # HuggingFace models
    if deps["huggingface_models"]:
        lines.extend([
            "# Download HuggingFace models",
            "# (uncomment and run manually)",
        ])
        for model in deps["huggingface_models"][:5]:  # Limit to 5
            lines.append(f"# huggingface-cli download {model} --local-dir models/")
        lines.append("")

    lines.extend([
        "echo '✅ Environment setup complete'",
    ])

    script_path.write_text("\n".join(lines))
    os.chmod(script_path, 0o755)

    return script_path


def update_reproduction_log(project_dir: Path, deps: dict) -> None:
    """Update REPRODUCTION.md with dependency info."""
    repro_file = project_dir / "REPRODUCTION.md"
    if not repro_file.exists():
        return

    content = repro_file.read_text()

    # Add dependency section if not present
    if "## Dependencies Found" not in content:
        dep_section = "\n## Dependencies Found\n\n"

        if deps["requirements_file"]:
            dep_section += f"- ✅ requirements.txt: `{deps['requirements_file']}`\n"
        if deps["conda_env"]:
            dep_section += f"- ✅ Conda env: `{deps['conda_env']}`\n"
        if deps["setup_py"]:
            dep_section += "- ✅ setup.py found\n"
        if deps["pyproject"]:
            dep_section += "- ✅ pyproject.toml found\n"
        if deps["dockerfile"]:
            dep_section += "- ✅ Dockerfile found\n"

        if deps["huggingface_models"]:
            dep_section += "\n### HuggingFace Models\n"
            for model in deps["huggingface_models"][:10]:
                dep_section += f"- `{model}`\n"

        # Insert after ## Environment section
        if "## Environment" in content:
            content = content.replace("## Environment", f"## Environment\n{dep_section}")
            repro_file.write_text(content)


def update_status(project_dir: Path, status: str) -> None:
    """Update project status in info.yaml."""
    info_file = project_dir / "info.yaml"
    if info_file.exists():
        content = info_file.read_text()
        content = re.sub(r'status:\s*"?\w+"?', f'status: "{status}"', content)
        info_file.write_text(content)


def main():
    parser = argparse.ArgumentParser(description="Reproduction helper")
    parser.add_argument("id", nargs="?", help="arXiv ID (uses context if omitted)")
    parser.add_argument("--repo", "-r", help="GitHub repo to clone (owner/repo)")
    parser.add_argument("--scan-only", "-s", action="store_true", help="Only scan, don't clone")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("❌ No project found. Specify ID or set context first.")
        sys.exit(1)

    print(f"📁 Project: {project_dir.name}")

    src_dir = project_dir / "src"
    models_dir = project_dir / "models"

    # Clone if needed
    if not args.scan_only:
        repo = args.repo or get_github_repo(project_dir)
        if repo:
            src_dir.mkdir(exist_ok=True)
            if clone_repo(repo, src_dir):
                print(f"✅ Code cloned to src/")
        else:
            print("⚠️  No GitHub repo specified. Use --repo owner/repo")

    # Scan dependencies
    if src_dir.exists() and any(src_dir.iterdir()):
        print("\n🔍 Scanning dependencies...")
        deps = scan_dependencies(src_dir)

        if args.json:
            print(json.dumps(deps, indent=2))
        else:
            print(f"   Python imports: {len(deps['python_imports'])}")
            print(f"   HuggingFace models: {len(deps['huggingface_models'])}")
            if deps["requirements_file"]:
                print(f"   ✅ requirements.txt found")
            if deps["conda_env"]:
                print(f"   ✅ Conda environment found")

        # Generate setup script
        script = generate_env_setup(project_dir, deps)
        print(f"\n📝 Generated: {script}")

        # Update REPRODUCTION.md
        update_reproduction_log(project_dir, deps)

        # Create models/ and data/ with .gitignore
        models_dir.mkdir(exist_ok=True)
        (project_dir / "data").mkdir(exist_ok=True)

        gitignore = project_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("models/\ndata/\n*.ckpt\n*.bin\n*.safetensors\n")
            print("📝 Created .gitignore for large files")

        # Update status
        update_status(project_dir, "reproduced")
        print(f"\n✅ Ready for reproduction. Next steps:")
        print(f"   1. cd {project_dir}")
        print(f"   2. ./env_setup.sh")
        print(f"   3. Create playground/inference_demo.py")
    else:
        print("⚠️  No source code found in src/")


if __name__ == "__main__":
    main()
