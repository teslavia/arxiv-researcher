# Contributing to arXiv Researcher

Thank you for your interest in contributing to arXiv Researcher!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Include your environment details (OS, Python version, Claude Code version)
- Provide clear reproduction steps for bugs

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test your changes locally
5. Commit with clear messages: `git commit -m "Add: description"`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Keep functions focused and well-documented
- Prefer standard library over external dependencies

### Skill Development

Current architecture uses a consolidated skill + unified CLI.

When adding new capabilities:

1. Add or update pipeline code under `arxiv_engine/pipelines/`
2. Wire the command in `arxiv_engine/cli.py` (`@cli.command()`)
3. Update `skills/arxiv-cli/SKILL.md` command docs
4. Update root `SKILL.md` and `README.md` examples
5. Run local sanity checks (`python3 -m compileall arxiv_engine`)

### Commit Message Convention

```
Add: new feature description
Fix: bug fix description
Update: enhancement to existing feature
Docs: documentation changes
Refactor: code refactoring
```

## Questions?

Open an issue with the `question` label.
