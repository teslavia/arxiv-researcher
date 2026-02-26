from setuptools import find_packages, setup


setup(
    name="arxiv-engine",
    version="0.2.0",
    description="CLI toolkit for arXiv paper research workflows",
    packages=find_packages(include=["arxiv_engine", "arxiv_engine.*"]),
    include_package_data=True,
    install_requires=["click>=8.1,<9"],
    entry_points={"console_scripts": ["arxiv=arxiv_engine.cli:cli"]},
    python_requires=">=3.10",
)
