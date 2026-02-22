#!/usr/bin/env python3
"""Test utility: paste cookie → save_tokens → list notebooks (optional: research).

Use a file for the cookie string (recommended for long strings). Then:

    python scripts/test_cookie_list_notebooks.py --cookie-file cookies.txt
    python scripts/test_cookie_list_notebooks.py --cookie-file cookies.txt --research

With --research: creates a new notebook first, then starts research using that
notebook_id (avoids notebook_id=None which can cause "no confirmation from API").
"""

import argparse
import asyncio
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _ensure_src_on_path() -> None:
    sys.path.insert(0, str(_project_root() / "src"))


DEFAULT_RESEARCH_QUERY = "What are the top three risks for a small software project? One sentence each."
DEFAULT_RESEARCH_TITLE = "Cookie test research"
DEFAULT_RESEARCH_TIMEOUT = 300


async def _save_tokens_and_list_notebooks(
    config_dir: Path,
    cookies: str,
    *,
    run_research: bool = False,
    research_query: str = DEFAULT_RESEARCH_QUERY,
    research_title: str = DEFAULT_RESEARCH_TITLE,
    research_timeout: int = DEFAULT_RESEARCH_TIMEOUT,
) -> None:
    """Save cookies via wrapper, list notebooks, and optionally run research in a new notebook."""
    _ensure_src_on_path()
    from notebooklm_wrapper import AsyncNotebookLMClient, NotebookLMTimeoutError

    config_dir.mkdir(parents=True, exist_ok=True)
    client = AsyncNotebookLMClient(config_dir=str(config_dir))
    try:
        await client.auth.save_tokens(cookies=cookies)
        notebooks = await client.notebook.list()
        print(f"\nNotebooks ({len(notebooks)}):")
        for nb in notebooks:
            print(f"  - {nb.title!r} (id={nb.id})")
        if not notebooks:
            print("  (none)")

        if run_research:
            existing = next((nb for nb in notebooks if nb.title == research_title), None)
            created_new = False
            if existing is not None:
                notebook_id = existing.id
                print(f"\nUsing existing notebook for research: {research_title!r}")
                print(f"  notebook_id={notebook_id}")
            else:
                print(f"\nCreating a new notebook for research: {research_title!r}")
                notebook = await client.notebook.create(title=research_title)
                notebook_id = notebook.id
                print(f"  notebook_id={notebook_id}")
                created_new = True

            print(f"Starting research (timeout={research_timeout}s): {research_query!r}")
            try:
                task = await client.research.start(
                    research_query,
                    notebook_id=notebook_id,
                    title=research_title,
                    source="web",
                    mode="fast",
                )
                task_id = getattr(task, "task_id", None)
                print(f"  task_id={task_id}, polling up to {research_timeout}s...")
                result = await client.research.status(
                    notebook_id,
                    max_wait=research_timeout,
                    poll_interval=15,
                    compact=True,
                    task_id=task_id,
                    query=research_query,
                )
                status = getattr(result, "status", None)
                report = getattr(result, "report", None)
                sources = getattr(result, "sources", None) or []
                message = getattr(result, "message", None)
                if report:
                    print(f"  report length={len(report)} chars")
                if status in ("completed", "success"):
                    print("  Research completed successfully.")
                    if not report:
                        # compact=True may omit report; fetch once with compact=False
                        full = await client.research.status(
                            notebook_id,
                            max_wait=10,
                            poll_interval=15,
                            compact=False,
                            task_id=task_id,
                            query=research_query,
                        )
                        report = getattr(full, "report", None)
                        if not sources:
                            sources = getattr(full, "sources", None) or []
                    if report:
                        print("\n--- Research report ---")
                        print(report)
                        print("---")
                    elif sources:
                        print("\n--- Research sources ---")
                        for i, s in enumerate(sources, 1):
                            title = s.get("title") or s.get("name") or "(no title)"
                            url = s.get("url") or s.get("link") or ""
                            snippet = s.get("snippet") or s.get("summary") or s.get("description") or ""
                            print(f"  {i}. {title}")
                            if url:
                                print(f"     {url}")
                            if snippet:
                                print(f"     {snippet[:200]}{'...' if len(snippet) > 200 else ''}")
                        print("---")
                    else:
                        print("  (No report or sources returned; check notebook in NotebookLM.)")
                else:
                    print(f"  Research ended with status: {status}", file=sys.stderr)
                    if message:
                        print(f"  message: {message}", file=sys.stderr)
                suffix = " (will appear in list on next run)" if created_new else ""
                print(f"  Notebook id: {notebook_id}{suffix}")
            except NotebookLMTimeoutError as e:
                print(f"  Research timed out after {research_timeout}s.", file=sys.stderr)
                raise
            except Exception as e:
                print(f"Research error: {e}", file=sys.stderr)
                raise
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        await client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Paste cookie → save_tokens → list notebooks (optional: research in new notebook)."
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Directory for credentials (default: temporary directory).",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cookie",
        type=str,
        default=None,
        help="Cookie string (e.g. from browser).",
    )
    group.add_argument(
        "--cookie-file",
        type=Path,
        default=None,
        help="Read cookie string from file (recommended for long strings).",
    )
    group.add_argument(
        "--stdin",
        action="store_true",
        help="Read cookie string from stdin.",
    )
    parser.add_argument(
        "--research",
        action="store_true",
        help="After listing, create a new notebook and run a fast research job (uses notebook_id to avoid API issues).",
    )
    parser.add_argument(
        "--research-query",
        type=str,
        default=DEFAULT_RESEARCH_QUERY,
        help="Research query (default: short risk question).",
    )
    parser.add_argument(
        "--research-title",
        type=str,
        default=DEFAULT_RESEARCH_TITLE,
        help="Title for the new notebook used by research (default: Cookie test research).",
    )
    parser.add_argument(
        "--research-timeout",
        type=int,
        default=DEFAULT_RESEARCH_TIMEOUT,
        help="Max seconds to wait for research (default: 300).",
    )
    args = parser.parse_args()

    if args.cookie is not None:
        cookies = args.cookie.strip()
    elif args.cookie_file is not None:
        path = args.cookie_file.resolve()
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1
        cookies = path.read_text().strip()
    elif args.stdin:
        cookies = sys.stdin.read().strip()
    else:
        print(
            "Paste your NotebookLM cookie string (e.g. from Application → Cookies "
            "after logging in at notebooklm.google.com), then press Enter:"
        )
        try:
            cookies = input().strip()
        except EOFError:
            print("Error: no input (use --cookie, --cookie-file, or --stdin).", file=sys.stderr)
            return 1

    if not cookies:
        print("Error: cookie string is empty.", file=sys.stderr)
        return 1

    if args.config_dir is not None:
        config_dir = args.config_dir.resolve()
    else:
        import tempfile

        config_dir = Path(tempfile.mkdtemp(prefix="notebooklm_wrapper_cookie_"))
        print(f"Using temporary config dir: {config_dir}")

    print("Saving tokens and listing notebooks...")
    asyncio.run(
        _save_tokens_and_list_notebooks(
            config_dir,
            cookies,
            run_research=args.research,
            research_query=args.research_query,
            research_title=args.research_title,
            research_timeout=args.research_timeout,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
