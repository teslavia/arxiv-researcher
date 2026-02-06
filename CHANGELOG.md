# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-06

### Major Changes
- **Generic Scaffolding**: Refactored all `/arxiv-lab` templates (`assets/*.py`) to be model-agnostic.
  - Previous templates were hardcoded for Transformers.
  - New templates act as generic deep learning scaffolds (CV/NLP/RL ready) designed for AI in-filling.

### Added
- **New Templates**: `train` (Training Loop), `viz` (Visualization Hook), `benchmark` (Performance), `api` (FastAPI), `onnx` (Dynamic Export).
- **Shared Utils**: Created `scripts/utils.py` to centralize context management and info parsing.

### Changed
- **Refactored Lab Script**: `scripts/lab.py` now uses a unified template-based generation logic.
- **Improved Type Safety**: Updated all scripts to use Python 3.10+ type hints.
- **Code Deduplication**: Removed redundant logic from `read.py` and `contrib.py`.

## [1.0.0] - 2026-01-XX

### Added
- Initial release of arXiv Researcher skill
- `/arxiv-search` - Search arXiv papers with GitHub Stars annotation
- `/arxiv-init` - Initialize paper project space with standardized structure
- `/arxiv-daily` - Daily digest of new papers by topic
- `/arxiv-context` - View/switch active paper context
- `/arxiv-read` - Deep reading with structured notes generation
- `/arxiv-repro` - One-click code reproduction workflow
- `/arxiv-lab` - Engineering experiments (API, ONNX, benchmark)
- `/arxiv-contrib` - Generate open source contribution materials
- `/arxiv-extend` - Custom workflow extensions
- Auto-install script for Claude Code integration
