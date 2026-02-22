"""Research resource - deep research operations.

Dependencies: MCPClientManager, ResearchImportResult, ResearchTask,
BaseResource, NotebookLMTimeoutError.
"""

import asyncio
import time

from ..exceptions import NotebookLMTimeoutError
from ..models import ResearchImportResult, ResearchTask
from .base import BaseResource

_TERMINAL_STATUSES = frozenset({"completed", "success", "failed", "no_research"})


class ResearchResource(BaseResource):
    """Deep research operations."""

    async def start(
        self,
        query: str,
        *,
        source: str = "web",
        mode: str = "fast",
        notebook_id: str | None = None,
        title: str | None = None,
    ) -> ResearchTask:
        """Start deep or fast research.

        :param query: Research query.
        :param source: Source (e.g. web, drive).
        :param mode: Mode (e.g. fast, deep).
        :param notebook_id: Optional notebook to attach to.
        :param title: Optional research title.
        :return: Research task status.
        """
        result = await self._call(
            "research_start",
            query=query,
            source=source,
            mode=mode,
            notebook_id=notebook_id,
            title=title,
        )
        return ResearchTask.model_validate(result)

    async def status(
        self,
        notebook_id: str,
        *,
        poll_interval: int = 30,
        max_wait: int = 300,
        compact: bool = True,
        task_id: str | None = None,
        query: str | None = None,
    ) -> ResearchTask:
        """Poll research progress.

        :param notebook_id: Notebook ID.
        :param poll_interval: Seconds between polls.
        :param max_wait: Max seconds to wait.
        :param compact: Whether to return compact output.
        :param task_id: Optional specific task ID.
        :param query: Optional query filter.
        :return: Research task status (terminal status only).
        :raises NotebookLMTimeoutError: If elapsed time >= max_wait and status is still non-terminal
        """
        t0 = time.monotonic()
        while True:
            remaining = max(1, int(max_wait - (time.monotonic() - t0)))
            result = await self._call(
                "research_status",
                notebook_id=notebook_id,
                poll_interval=poll_interval,
                max_wait=min(poll_interval, remaining),
                compact=compact,
                task_id=task_id,
                query=query,
            )
            task = ResearchTask.model_validate(result)
            if task.status in _TERMINAL_STATUSES:
                return task
            elapsed = time.monotonic() - t0
            if elapsed >= max_wait:
                raise NotebookLMTimeoutError(
                    f"Research did not complete within {max_wait}s "
                    f"(status={task.status!r}, elapsed={elapsed:.0f}s)"
                )
            await asyncio.sleep(poll_interval)

    async def import_sources(
        self,
        notebook_id: str,
        task_id: str,
        *,
        source_indices: list[int] | None = None,
    ) -> ResearchImportResult:
        """Import discovered sources into notebook.

        :param notebook_id: Target notebook ID.
        :param task_id: Research task ID.
        :param source_indices: Optional indices of sources to import.
        :return: Import result with counts.
        """
        result = await self._call(
            "research_import",
            notebook_id=notebook_id,
            task_id=task_id,
            source_indices=source_indices,
        )
        return ResearchImportResult.model_validate(result)
