#!/usr/bin/env python3
"""Test utility: OAuth (browser login) + list notebooks via the wrapper.

Uses an isolated config directory so it does not touch your default nlm login.
Run from project root with venv active:

    python scripts/test_oauth_list_notebooks.py

Or with a specific directory (e.g. for reusing credentials):

    python scripts/test_oauth_list_notebooks.py --config-dir ./tmp_oauth_test

Step 1: Runs `nlm login` with HOME set to the config directory (browser opens;
        complete Google/NotebookLM login there).
Step 2: Uses AsyncNotebookLMClient(config_dir=...) and lists all notebooks.
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_nlm_login(config_dir: Path) -> bool:
    """Run nlm login with HOME=config_dir. Returns True if login succeeded."""
    env = os.environ.copy()
    env["HOME"] = str(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    print(f"Config directory: {config_dir}")
    print("Launching browser login (nlm login). Complete sign-in in the browser...")
    try:
        result = subprocess.run(
            ["nlm", "login"],
            env=env,
            cwd=str(_project_root()),
            check=False,
        )
        if result.returncode != 0:
            print("nlm login exited with code", result.returncode, file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print(
            "Error: 'nlm' not found. Install notebooklm-mcp-cli and ensure it's on PATH.",
            file=sys.stderr,
        )
        print("  pip install notebooklm-mcp-cli", file=sys.stderr)
        return False


async def _list_notebooks(config_dir: Path) -> None:
    """Use the wrapper with config_dir to list notebooks."""
    # Import here so the script can be run without installing the package in dev
    sys.path.insert(0, str(_project_root() / "src"))
    from notebooklm_wrapper import AsyncNotebookLMClient

    client = AsyncNotebookLMClient(config_dir=str(config_dir))
    try:
        notebooks = await client.notebook.list()
        print(f"\nNotebooks ({len(notebooks)}):")
        for nb in notebooks:
            print(f"  - {nb.title!r} (id={nb.id})")
        if not notebooks:
            print("  (none)")
    except Exception as e:
        print(f"Error listing notebooks: {e}", file=sys.stderr)
        raise
    finally:
        await client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test OAuth + wrapper: run nlm login then list notebooks."
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Directory for credentials (default: temporary directory).",
    )
    parser.add_argument(
        "--skip-login",
        action="store_true",
        help="Skip nlm login; use existing credentials in --config-dir.",
    )
    args = parser.parse_args()

    if args.config_dir is not None:
        config_dir = args.config_dir.resolve()
    else:
        import tempfile

        config_dir = Path(tempfile.mkdtemp(prefix="notebooklm_wrapper_oauth_"))
        print(f"Using temporary config dir: {config_dir}")

    if not args.skip_login:
        if not _run_nlm_login(config_dir):
            return 1
    else:
        if not config_dir.is_dir():
            print(f"Error: --config-dir {config_dir} does not exist.", file=sys.stderr)
            return 1
        print(f"Using existing config dir: {config_dir}")

    print("\nListing notebooks via wrapper...")
    asyncio.run(_list_notebooks(config_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
