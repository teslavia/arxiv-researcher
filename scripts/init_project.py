#!/usr/bin/env python3
"""Initialize arXiv paper project space."""

import argparse
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import sys

# Add local directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils import ARXIV_ROOT, CONTEXT_FILE, update_global_readme

def fetch_paper_info(arxiv_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    # Normalize ID (remove version if present)
    arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        xml_data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    entry = root.find("atom:entry", ns)

    if entry is None:
        raise ValueError(f"Paper not found: {arxiv_id}")

    title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
    summary = entry.find("atom:summary", ns).text.strip()
    published = entry.find("atom:published", ns).text[:10]
    authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
    categories = [c.get("term") for c in entry.findall("atom:category", ns)]

    return {
        "id": arxiv_id,
        "title": title,
        "summary": summary,
        "published": published,
        "authors": authors,
        "categories": categories,
        "primary_category": categories[0] if categories else "unknown",
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
    }

def to_snake_case(text: str) -> str:
    """Convert title to snake_case directory name."""
    # Remove special chars, keep alphanumeric and spaces
    clean = re.sub(r"[^\w\s]", "", text)
    # Replace spaces with underscores, limit length
    words = clean.split()[:6]
    return "_".join(words)

def create_project(info: dict) -> Path:
    """Create project directory structure."""
    # Format: YYMM.Category/ID_SnakeTitle
    year_month = info["published"][:7].replace("-", "")  # YYYYMM -> YYYYMM
    year_short = year_month[2:6]  # YYMM
    category = info["primary_category"].split(".")[0].upper()

    parent_dir = ARXIV_ROOT / f"{year_short}.{category}"
    project_name = f"{info['id']}_{to_snake_case(info['title'])}"
    project_dir = parent_dir / project_name

    # Create directories
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "src").mkdir(exist_ok=True)
    (project_dir / "models").mkdir(exist_ok=True)
    (project_dir / "data").mkdir(exist_ok=True)
    (project_dir / "playground").mkdir(exist_ok=True)
    (project_dir / "contribution").mkdir(exist_ok=True)

    # Create .gitignore for large files
    gitignore_content = """# Large files - do not commit
models/
data/
*.ckpt
*.bin
*.safetensors
*.pt
*.pth
__pycache__/
.ipynb_checkpoints/
"""
    (project_dir / ".gitignore").write_text(gitignore_content)

    # Generate BibTeX
    first_author = info['authors'][0].split()[-1] if info['authors'] else "Unknown"
    year = info['published'][:4]
    bibtex = f"""@article{{{first_author.lower()}{year}{info['id'].replace('.', '')},
  title={{{info['title']}}},
  author={{{' and '.join(info['authors'][:5])}}},
  journal={{arXiv preprint arXiv:{info['id']}}},
  year={{{year}}}
}}"""

    # Create info.yaml with Tags and BibTeX
    info_yaml = f"""# Paper Metadata
id: "{info['id']}"
title: "{info['title']}"
authors: {info['authors'][:5]}
published: "{info['published']}"
categories: {info['categories']}
status: "downloaded"  # downloaded -> learned -> reproduced -> optimized

# Tags for organization (edit manually)
tags: []
# Example: ["LLM", "inference", "optimization"]

# Links
pdf_url: "{info['pdf_url']}"
abs_url: "{info['abs_url']}"
github_repo: ""
huggingface_model: ""

# Metrics (filled during reproduction)
metrics:
  inference_latency_ms: null
  gpu_memory_mb: null
  accuracy: null

created_at: "{datetime.now().isoformat()}"

# BibTeX Citation
bibtex: |
{chr(10).join('  ' + line for line in bibtex.split(chr(10)))}
"""
    (project_dir / "info.yaml").write_text(info_yaml)

    # Create empty SUMMARY.md with enhanced template
    summary_template = f"""# {info['title']}

**arXiv**: [{info['id']}]({info['abs_url']})
**Authors**: {', '.join(info['authors'][:3])}{'...' if len(info['authors']) > 3 else ''}
**Status**: 📥 Downloaded

## Context
<!-- What problem does this paper solve? Why do previous methods fail? -->

## Key Insight
<!-- Core innovation in ONE sentence -->

## Method
<!-- Key equations, algorithms, or architecture diagram -->

### Architecture
<!-- Model architecture description -->

### Key Equations
<!-- Important mathematical formulations -->

```python
# Pseudo-code implementation
```

## Results
<!-- Main experimental findings, comparison with baselines -->

| Method | Metric1 | Metric2 |
|--------|---------|---------|
| Baseline | - | - |
| This Paper | - | - |

## Takeaways
<!-- What can I apply to my work? -->

## Open Questions
<!-- Unresolved mysteries, ideas to verify -->

## Related Papers
<!-- Papers cited or related work in local library -->
"""
    (project_dir / "SUMMARY.md").write_text(summary_template)

    # Create enhanced REPRODUCTION.md
    repro_template = f"""# Reproduction Log: {info['title']}

**arXiv**: [{info['id']}]({info['abs_url']})
**Status**: 🔬 Reproducing

## Environment
- **OS**:
- **Python**:
- **CUDA**:
- **GPU**:
- **Key Dependencies**:

## Setup Steps
```bash
# 1. Clone repository
git clone <repo_url> src/

# 2. Create environment
cd src && conda env create -f environment.yml
# or: pip install -r requirements.txt

# 3. Download model weights
huggingface-cli download <model_id> --local-dir models/
```

## Performance Metrics
| Metric | Paper | Reproduced | Notes |
|--------|-------|------------|-------|
| Inference Latency (ms) | - | - | |
| GPU Memory (MB) | - | - | |
| Accuracy/Score | - | - | |

## Run Log
| Date | Command | Result | Notes |
|------|---------|--------|-------|

## Issues Encountered
<!-- Document problems and solutions -->

### Issue 1:
**Problem**:
**Solution**:

## Sanity Check
- [ ] Environment setup successful
- [ ] Model weights downloaded
- [ ] inference_demo.py runs without error
- [ ] Output matches expected format
"""
    (project_dir / "REPRODUCTION.md").write_text(repro_template)

    return project_dir

def download_pdf(url: str, dest: Path) -> bool:
    """Download PDF file."""
    try:
        print(f"📥 Downloading PDF...")
        subprocess.run(["curl", "-L", "-o", str(dest), url], check=True, timeout=120)
        return dest.exists() and dest.stat().st_size > 1000
    except Exception as e:
        print(f"⚠️ PDF download failed: {e}")
        return False

def update_global_readme():
    """Update the global README.md index."""
    # This logic is now in utils.py (or should be, but let's keep it here for now if not moved)
    # Ideally, we should move update_global_readme to utils.py as well to avoid duplication
    # For now, let's just make sure it uses the dynamic ARXIV_ROOT
    readme_path = ARXIV_ROOT / "README.md"

    # Scan all projects
    projects = []
    if ARXIV_ROOT.exists():
        for category_dir in sorted(ARXIV_ROOT.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for project_dir in sorted(category_dir.iterdir()):
                    info_file = project_dir / "info.yaml"
                    if info_file.exists():
                        # Simple parse for status
                        content = info_file.read_text()
                        status_match = re.search(r'status:\s*"?(\w+)"?', content)
                        status = status_match.group(1) if status_match else "unknown"
                        title_match = re.search(r'title:\s*"([^"]+)"', content)
                        title = title_match.group(1)[:60] if title_match else project_dir.name

                        projects.append({
                            "category": category_dir.name,
                            "name": project_dir.name,
                            "path": project_dir.relative_to(ARXIV_ROOT),
                            "status": status,
                            "title": title,
                        })

    # Generate README
    status_emoji = {
        "downloaded": "📥",
        "learned": "📖",
        "reproduced": "🔬",
        "optimized": "🚀",
    }

    readme_content = f"""# arXiv Research Lab

> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Progress

| Status | Count |
|--------|-------|
"""
    # Count by status
    status_counts = {}
    for p in projects:
        status_counts[p["status"]] = status_counts.get(p["status"], 0) + 1

    for status, count in sorted(status_counts.items()):
        emoji = status_emoji.get(status, "❓")
        readme_content += f"| {emoji} {status.title()} | {count} |\n"

    readme_content += f"\n**Total**: {len(projects)} papers\n\n## Papers\n\n"

    # Group by category
    current_cat = None
    for p in projects:
        if p["category"] != current_cat:
            current_cat = p["category"]
            readme_content += f"\n### {current_cat}\n\n"

        emoji = status_emoji.get(p["status"], "❓")
        readme_content += f"- {emoji} [{p['name']}]({p['path']}) - {p['title']}\n"

    readme_path.write_text(readme_content)
    print(f"📋 Updated global index: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="Initialize arXiv paper project")
    parser.add_argument("arxiv_id", help="arXiv ID (e.g., 2401.12345) or URL")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF download")
    parser.add_argument("--update-index", action="store_true", help="Only update global README")
    args = parser.parse_args()

    if args.update_index:
        update_global_readme()
        return

    # Extract ID from URL if needed
    arxiv_id = args.arxiv_id
    if "arxiv.org" in arxiv_id:
        match = re.search(r"(\d{4}\.\d{4,5})", arxiv_id)
        if match:
            arxiv_id = match.group(1)

    print(f"🔍 Fetching metadata for {arxiv_id}...")
    info = fetch_paper_info(arxiv_id)
    print(f"📄 {info['title'][:70]}...")

    project_dir = create_project(info)
    print(f"📁 Created: {project_dir}")

    if not args.no_pdf:
        pdf_path = project_dir / "paper.pdf"
        if download_pdf(info["pdf_url"], pdf_path):
            print(f"✅ PDF saved: {pdf_path}")

    # Update context to this project
    context_file = ARXIV_ROOT / ".context"
    context_file.write_text(json.dumps({"id": info["id"], "path": str(project_dir)}, indent=2))

    # Ensure .extensions directory exists
    (ARXIV_ROOT / ".extensions").mkdir(exist_ok=True)

    update_global_readme()
    print(f"\n✅ Project ready: {project_dir}")
    print(f"📍 Context set to: {info['id']}")
    print(f"   Next: Read paper and update SUMMARY.md")

if __name__ == "__main__":
    main()
