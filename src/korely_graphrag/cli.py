"""Command-line entry point for korely-graphrag."""

from __future__ import annotations

import json
import logging

import click

from . import __version__
from .splash import print_splash


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.option("--no-splash", is_flag=True, help="Suppress the startup banner.")
@click.pass_context
def main(ctx: click.Context, verbose: bool, no_splash: bool) -> None:
    """korely-graphrag — MCP-native second brain over your markdown notes."""
    _configure_logging(verbose)
    if not no_splash and ctx.invoked_subcommand is not None:
        print_splash(version=__version__)


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--reset", is_flag=True, help="Drop and recreate all data before ingesting.")
def ingest(path: str, reset: bool) -> None:
    """Ingest a directory of markdown files into the knowledge base."""
    from .ingest import ingest_directory

    click.echo(f"Ingesting from: {path} (reset={reset})\n")
    stats = ingest_directory(path, reset=reset)
    click.echo("\n--- ingest complete ---")
    for k, v in stats.as_dict().items():
        click.echo(f"  {k:<28} {v}")


@main.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8080, show_default=True, type=int)
def serve(host: str, port: int) -> None:
    """Start the MCP server (SSE transport)."""
    from .mcp_server.server import run

    click.echo(f"MCP server starting on http://{host}:{port}/sse")
    run(host=host, port=port)


@main.command()
def stats() -> None:
    """Print stats about the current knowledge base."""
    from sqlalchemy import func, select

    from .storage import Chunk, Entity, Item, Mention, healthcheck, session_scope

    if not healthcheck():
        click.echo("ERROR: cannot connect to the database.", err=True)
        raise SystemExit(1)

    with session_scope() as s:
        out = {
            "items": s.execute(select(func.count(Item.id))).scalar_one(),
            "chunks": s.execute(select(func.count(Chunk.id))).scalar_one(),
            "entities": s.execute(select(func.count(Entity.id))).scalar_one(),
            "mentions": s.execute(
                select(func.count()).select_from(Mention)
            ).scalar_one(),
            "folders": s.execute(
                select(func.count(func.distinct(Item.folder))).where(Item.folder.is_not(None))
            ).scalar_one(),
        }
    click.echo(json.dumps(out, indent=2))


@main.command()
def banner() -> None:
    """Just print the splash banner (useful for sanity-checking colors)."""
    # Splash is already printed by the parent group; nothing else to do.


if __name__ == "__main__":
    main()
