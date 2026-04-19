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

    from .storage import Chunk, Entity, Item, Mention, healthcheck, init_db, session_scope

    if not healthcheck():
        click.echo("ERROR: cannot connect to the database.", err=True)
        click.echo("Hint: is Postgres running? `docker compose up -d db`", err=True)
        raise SystemExit(1)

    # Ensure the schema exists (idempotent). On fresh installs, `stats` before
    # `ingest` used to crash with "relation items does not exist".
    init_db(drop_first=False)

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
    if out["items"] == 0:
        click.echo("\n(empty — run `korely-graphrag ingest <path>` to add notes)")


@main.command()
@click.option(
    "--format", "fmt",
    type=click.Choice(["mermaid"]),
    default="mermaid",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--min-df",
    type=int,
    default=2,
    show_default=True,
    help="Skip entities mentioned in fewer than N items (noise filter).",
)
@click.option(
    "--max-df",
    type=int,
    default=None,
    help="Skip entities mentioned in more than N items (hub-node filter — defaults to no cap).",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Write to file (default: stdout).",
)
def export(fmt: str, min_df: int, max_df: int | None, output: str | None) -> None:
    """Export the knowledge graph for external visualization.

    Default format is Mermaid — paste the output into any markdown viewer
    that supports Mermaid (GitHub, Obsidian, VSCode preview). Only entities
    that connect at least `--min-df` items are drawn — single-mention
    entities are omitted as visual noise.
    """
    from sqlalchemy import bindparam, text

    from .storage import healthcheck, session_scope

    if not healthcheck():
        click.echo("ERROR: cannot connect to the database.", err=True)
        raise SystemExit(1)

    with session_scope() as s:
        entity_rows = s.execute(
            text("""
                SELECT e.id::text AS id, e.name, e.entity_type,
                       COUNT(DISTINCT c.item_id) AS df
                FROM entities e
                JOIN mentions m ON m.entity_id = e.id
                JOIN chunks c ON c.id = m.chunk_id
                GROUP BY e.id, e.name, e.entity_type
                HAVING COUNT(DISTINCT c.item_id) >= :min_df
                   AND (:max_df IS NULL OR COUNT(DISTINCT c.item_id) <= :max_df)
                ORDER BY df DESC, e.name ASC
            """),
            {"min_df": min_df, "max_df": max_df},
        ).all()

        if not entity_rows:
            click.echo(
                "No entities match the filters. "
                "Try lowering --min-df or run `korely-graphrag stats` first.",
                err=True,
            )
            raise SystemExit(1)

        entity_ids = [r.id for r in entity_rows]

        item_rows = s.execute(
            text("""
                SELECT DISTINCT i.id::text AS id, i.title
                FROM items i
                JOIN chunks c ON c.item_id = i.id
                JOIN mentions m ON m.chunk_id = c.id
                WHERE m.entity_id IN :eids
                ORDER BY i.title
            """).bindparams(bindparam("eids", expanding=True)),
            {"eids": entity_ids},
        ).all()

        edge_rows = s.execute(
            text("""
                SELECT DISTINCT c.item_id::text AS item_id,
                                m.entity_id::text AS entity_id
                FROM mentions m
                JOIN chunks c ON c.id = m.chunk_id
                WHERE m.entity_id IN :eids
            """).bindparams(bindparam("eids", expanding=True)),
            {"eids": entity_ids},
        ).all()

    mermaid = _render_mermaid(item_rows, entity_rows, edge_rows)

    summary = (
        f"# {len(item_rows)} items · {len(entity_rows)} entities · {len(edge_rows)} edges "
        f"(min_df={min_df}" + (f", max_df={max_df}" if max_df else "") + ")"
    )

    if output:
        from pathlib import Path
        Path(output).write_text(summary + "\n\n" + mermaid + "\n")
        click.echo(f"Wrote {summary.lstrip('# ')} → {output}")
    else:
        click.echo(summary)
        click.echo("")
        click.echo(mermaid)


def _render_mermaid(items, entities, edges) -> str:
    """Render a bipartite item↔entity graph as Mermaid flowchart."""
    def _nid(prefix: str, uuid_str: str) -> str:
        # Mermaid node IDs must be alphanumeric + underscore
        return f"{prefix}_{uuid_str.replace('-', '')[:10]}"

    def _label(text: str, max_len: int = 50) -> str:
        # Escape double quotes, truncate for readability
        t = (text or "").replace('"', "'").strip()
        return t[: max_len - 1] + "…" if len(t) > max_len else t

    lines: list[str] = []
    lines.append("```mermaid")
    lines.append("flowchart LR")
    lines.append("  classDef item fill:#dbeafe,stroke:#1e40af,color:#000,stroke-width:1px;")
    lines.append("  classDef entity fill:#fce7f3,stroke:#9d174d,color:#000,stroke-width:1px;")
    lines.append("")

    # Items (rectangles)
    for r in items:
        lines.append(f'  {_nid("I", r.id)}["{_label(r.title)}"]:::item')

    # Entities (rounded) — include df for quick spotting of hubs
    for r in entities:
        lines.append(f'  {_nid("E", r.id)}(("{_label(r.name)}<br/>df={r.df}")):::entity')

    lines.append("")
    for item_id, entity_id in edges:
        lines.append(f'  {_nid("I", item_id)} --- {_nid("E", entity_id)}')

    lines.append("```")
    return "\n".join(lines)


@main.command()
def banner() -> None:
    """Just print the splash banner (useful for sanity-checking colors)."""
    # Splash is already printed by the parent group; nothing else to do.


if __name__ == "__main__":
    main()
