#!/usr/bin/env python3
"""Generate a static HTML page showing the repository's file layout."""

import argparse
import html
import os
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE = {".git", "__pycache__", ".venv", "venv", "node_modules", "_site"}


def build_tree(path: Path, root: Path) -> str:
    """Return nested <ul> markup for the directory at `path`."""
    entries = sorted(
        (p for p in path.iterdir() if p.name not in EXCLUDE),
        key=lambda p: (p.is_file(), p.name.lower()),
    )
    items = []
    for entry in entries:
        name = html.escape(entry.name)
        if entry.is_dir():
            items.append(
                f'<li><details open><summary class="dir">{name}/</summary>'
                f"{build_tree(entry, root)}</details></li>"
            )
        else:
            size = entry.stat().st_size
            items.append(f'<li class="file">{name} <span class="size">{size} B</span></li>')
    return f"<ul>{''.join(items)}</ul>"


def render(root: Path) -> str:
    repo_name = html.escape(os.environ.get("GITHUB_REPOSITORY", root.resolve().name))
    commit = html.escape(os.environ.get("GITHUB_SHA", "local")[:7])
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{repo_name} – file layout</title>
<style>
  :root {{ --bg: #fff; --fg: #1f2328; --muted: #656d76; --accent: #0969da; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #0d1117; --fg: #e6edf3; --muted: #8d96a0; --accent: #4493f8; }}
  }}
  body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, sans-serif;
         max-width: 900px; margin: 2rem auto; padding: 0 16px; }}
  h1 {{ margin-bottom: .25rem; }}
  .meta {{ color: var(--muted); margin-top: 0; }}
  ul {{ list-style: none; padding-left: 1.25rem; font-family: ui-monospace, monospace; }}
  .dir {{ color: var(--accent); cursor: pointer; font-weight: 600; }}
  .size {{ color: var(--muted); font-size: .85em; }}
</style>
</head>
<body>
<h1>{repo_name}</h1>
<p class="meta">Commit {commit} · generated {generated}</p>
{build_tree(root, root)}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--out", default="_site", help="output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render(Path(args.root)), encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
