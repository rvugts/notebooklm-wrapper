#!/usr/bin/env python3
"""Test utility: paste cookie → save_tokens → list notebooks (optional: research).

Use a file for the cookie string (recommended for long strings). Then:

    python scripts/test_cookie_list_notebooks.py --cookie-file cookies.txt
    python scripts/test_cookie_list_notebooks.py --cookie-file cookies.txt --research

With --research: reuses notebook by title if it exists, else creates one; runs research
(--mode fast|deep). Retries research.start() once on "no confirmation from API".
Then adds the report as a text source. Use --no-add-report to skip.
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
    research_output_file: Path | None = None,
    add_report_as_source: bool = True,
    research_mode: str = "deep",
) -> None:
    """Save cookies via wrapper, list notebooks, and optionally run research."""
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

            print(f"Starting research (timeout={research_timeout}s, mode={research_mode}): {research_query!r}")
            try:
                task = await client.research.start(
                    research_query,
                    notebook_id=notebook_id,
                    title=research_title,
                    source="web",
                    mode=research_mode,
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
                    output_lines: list[str] = []
                    if report:
                        print("\n--- Research report ---")
                        print(report)
                        print("---")
                        output_lines.append("--- Research report ---")
                        output_lines.append(report)
                        output_lines.append("---")
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
                                print(f"     {snippet}")
                            output_lines.append(f"{i}. {title}")
                            if url:
                                output_lines.append(f"   {url}")
                            if snippet:
                                output_lines.append(f"   {snippet}")
                            output_lines.append("")
                        print("---")
                        output_lines.append("---")
                    else:
                        print("  (No report or sources returned; check notebook in NotebookLM.)")
                    if research_output_file and output_lines:
                        research_output_file.write_text("\n".join(output_lines), encoding="utf-8")
                        print(f"  Full output written to {research_output_file}")
                    if add_report_as_source and report:
                        try:
                            add_result = await client.source.add(
                                notebook_id,
                                "text",
                                text=report,
                                title=research_title or "Research report",
                                wait=True,
                                wait_timeout=60.0,
                            )
                            sid = getattr(add_result, "source_id", None)
                            print(f"  Added report as source (source_id={sid}).")
                        except Exception as e:
                            print(f"  Adding report as source failed: {e}", file=sys.stderr)
                else:
                    print(f"  Research ended with status: {status}", file=sys.stderr)
                    if message:
                        print(f"  message: {message}", file=sys.stderr)
                    if status == "no_research":
                        print("  (No report produced. Try --mode fast or run again.)", file=sys.stderr)
                suffix = " (will appear in list on next run)" if created_new else ""
                print(f"  Notebook id: {notebook_id}{suffix}")
            except NotebookLMTimeoutError:
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
        help="After listing, create/reuse notebook and run research, then add report as source.",
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
        help="Title for the notebook used by research (default: Cookie test research).",
    )
    parser.add_argument(
        "--research-timeout",
        type=int,
        default=DEFAULT_RESEARCH_TIMEOUT,
        help="Max seconds to wait for research (default: 300).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write full research report/sources to FILE (no truncation).",
    )
    parser.add_argument(
        "--no-add-report",
        action="store_true",
        help="Do not add the report as a text source to the notebook.",
    )
    parser.add_argument(
        "--mode",
        choices=("fast", "deep"),
        default="deep",
        help="Research mode: fast or deep (default: deep). Try --mode fast if start fails.",
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
            research_output_file=args.output.resolve() if args.output else None,
            add_report_as_source=not args.no_add_report,
            research_mode=args.mode,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
