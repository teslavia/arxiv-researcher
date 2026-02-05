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

When adding new skills:

1. Create a new directory under `skills/`
2. Add `SKILL.md` with proper trigger phrases
3. Add corresponding script in `scripts/`
4. Update main `SKILL.md` to include the new sub-skill
5. Update `README.md` with usage examples

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
