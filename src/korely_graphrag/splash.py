"""ASCII splash banner for the CLI.

Inspired by Claude Code's blocky banner, but rendered in a calmer blue palette
and tuned for a single-line terminal width. We avoid hard ANSI 256-color codes
in favor of standard 16-color ANSI so the banner looks fine in basic terminals
(WSL default, Linux tty, CI logs).
"""

from __future__ import annotations

import sys

# Standard ANSI bright blue (works everywhere). 256-color users still get a
# pleasant blue; ttys without color silently strip it via _supports_color.
_BLUE = "\033[1;34m"
_DIM = "\033[2;37m"
_RESET = "\033[0m"

# Block-glyph rendering of "KORELY" using ▀▄█ — 5 lines tall, monospace safe.
_BANNER = r"""
██╗  ██╗  ██████╗   ██████╗   ███████╗  ██╗      ██╗   ██╗
██║ ██╔╝ ██╔═══██╗  ██╔══██╗  ██╔════╝  ██║      ╚██╗ ██╔╝
█████╔╝  ██║   ██║  ██████╔╝  █████╗    ██║       ╚████╔╝
██╔═██╗  ██║   ██║  ██╔══██╗  ██╔══╝    ██║        ╚██╔╝
██║  ██╗ ╚██████╔╝  ██║  ██║  ███████╗  ███████╗    ██║
╚═╝  ╚═╝  ╚═════╝   ╚═╝  ╚═╝  ╚══════╝  ╚══════╝    ╚═╝
"""


def _supports_color() -> bool:
    if not sys.stdout.isatty():
        return False
    import os

    if os.environ.get("NO_COLOR"):
        return False
    return os.environ.get("TERM", "") not in ("dumb", "")


def render_splash(version: str | None = None) -> str:
    color = _supports_color()
    banner = _BANNER.rstrip()
    if color:
        banner = _BLUE + banner + _RESET
    tagline = "  graph-augmented second brain  ·  MCP-native  ·  Apache 2.0"
    if version:
        tagline += f"  ·  v{version}"
    if color:
        tagline = _DIM + tagline + _RESET
    return banner + "\n" + tagline + "\n"


def print_splash(version: str | None = None) -> None:
    sys.stdout.write(render_splash(version))
    sys.stdout.flush()
