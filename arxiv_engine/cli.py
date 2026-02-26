"""Unified CLI entry point for arxiv-engine."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterator
import sys

import click

from arxiv_engine.pipelines import (
    brain as brain_pipeline,
    context as context_pipeline,
    contrib as contrib_pipeline,
    daily as daily_pipeline,
    dataset as dataset_pipeline,
    deploy as deploy_pipeline,
    extend as extend_pipeline,
    fix as fix_pipeline,
    init_project as init_pipeline,
    lab as lab_pipeline,
    read as read_pipeline,
    repro as repro_pipeline,
    search as search_pipeline,
)

PipelineMain = Callable[[], None]
PASSTHROUGH_SETTINGS = {"ignore_unknown_options": True, "allow_extra_args": True}


@contextmanager
def _patched_argv(argv: list[str]) -> Iterator[None]:
    old_argv = sys.argv
    sys.argv = argv
    try:
        yield
    finally:
        sys.argv = old_argv


def _run_pipeline(main_fn: PipelineMain, argv: list[str]) -> None:
    with _patched_argv(argv):
        try:
            main_fn()
        except SystemExit as exc:
            code = exc.code
            if code in (None, 0):
                return
            if isinstance(code, int):
                raise click.exceptions.Exit(code) from exc
            raise click.ClickException(str(code)) from exc


@click.group()
def cli() -> None:
    """arXiv research toolkit CLI."""


@cli.command("search", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def search_cmd(ctx: click.Context) -> None:
    """Search arXiv papers."""
    _run_pipeline(search_pipeline.main, ["arxiv search", *ctx.args])


@cli.command("fetch", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def fetch_cmd(ctx: click.Context) -> None:
    """Backward-compatible alias of search."""
    _run_pipeline(search_pipeline.main, ["arxiv fetch", *ctx.args])


@cli.command("daily", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def daily_cmd(ctx: click.Context) -> None:
    """Generate daily arXiv digest."""
    _run_pipeline(daily_pipeline.main, ["arxiv daily", *ctx.args])


@cli.command("init", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def init_cmd(ctx: click.Context) -> None:
    """Initialize a paper project."""
    _run_pipeline(init_pipeline.main, ["arxiv init", *ctx.args])


@cli.command("context", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def context_cmd(ctx: click.Context) -> None:
    """Get or set active context."""
    _run_pipeline(context_pipeline.main, ["arxiv context", *ctx.args])


@cli.command("read", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def read_cmd(ctx: click.Context) -> None:
    """Prepare and track reading workflow."""
    _run_pipeline(read_pipeline.main, ["arxiv read", *ctx.args])


@cli.command("repro", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def repro_cmd(ctx: click.Context) -> None:
    """Run reproduction helper workflow."""
    _run_pipeline(repro_pipeline.main, ["arxiv repro", *ctx.args])


@cli.command("lab", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def lab_cmd(ctx: click.Context) -> None:
    """Create experiment playground scaffold."""
    _run_pipeline(lab_pipeline.main, ["arxiv lab", *ctx.args])


@cli.command("contrib", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def contrib_cmd(ctx: click.Context) -> None:
    """Generate open-source contribution materials."""
    _run_pipeline(contrib_pipeline.main, ["arxiv contrib", *ctx.args])


@cli.command("extend", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def extend_cmd(ctx: click.Context) -> None:
    """Manage custom extension workflows."""
    _run_pipeline(extend_pipeline.main, ["arxiv extend", *ctx.args])


@cli.command("brain", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def brain_cmd(ctx: click.Context) -> None:
    """Use local semantic knowledge search."""
    _run_pipeline(brain_pipeline.main, ["arxiv brain", *ctx.args])


@cli.command("dataset", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def dataset_cmd(ctx: click.Context) -> None:
    """Generate SFT dataset scaffold."""
    _run_pipeline(dataset_pipeline.main, ["arxiv dataset", *ctx.args])


@cli.command("deploy", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def deploy_cmd(ctx: click.Context) -> None:
    """Create deployment scaffold."""
    _run_pipeline(deploy_pipeline.main, ["arxiv deploy", *ctx.args])


@cli.command("fix", context_settings=PASSTHROUGH_SETTINGS, add_help_option=False)
@click.pass_context
def fix_cmd(ctx: click.Context) -> None:
    """Generate diagnostic fix prompts."""
    _run_pipeline(fix_pipeline.main, ["arxiv fix", *ctx.args])


if __name__ == "__main__":
    cli()
