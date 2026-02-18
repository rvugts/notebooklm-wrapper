"""Studio resource - artifact creation and management.

Dependencies: typing, MCPClientManager, ValidationError, StudioStatus,
BaseResource.
"""

from typing import Any

from ..exceptions import ValidationError
from ..models import StudioStatus
from .base import BaseResource


def _studio_create_args(
    notebook_id: str,
    artifact_type: str,
    *,
    source_ids: list[str] | None = None,
    audio_format: str = "deep_dive",
    audio_length: str = "default",
    video_format: str = "explainer",
    visual_style: str = "auto_select",
    orientation: str = "landscape",
    detail_level: str = "standard",
    slide_format: str = "detailed_deck",
    slide_length: str = "default",
    report_format: str = "Briefing Doc",
    custom_prompt: str = "",
    question_count: int = 2,
    difficulty: str = "medium",
    language: str = "en",
    focus_prompt: str = "",
    title: str = "Mind Map",
    description: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Build studio_create tool arguments."""
    return {
        "notebook_id": notebook_id,
        "artifact_type": artifact_type,
        "source_ids": source_ids,
        "confirm": True,
        "audio_format": audio_format,
        "audio_length": audio_length,
        "video_format": video_format,
        "visual_style": visual_style,
        "orientation": orientation,
        "detail_level": detail_level,
        "slide_format": slide_format,
        "slide_length": slide_length,
        "report_format": report_format,
        "custom_prompt": custom_prompt,
        "question_count": question_count,
        "difficulty": difficulty,
        "language": language,
        "focus_prompt": focus_prompt,
        "title": title,
        "description": description,
        **kwargs,
    }


class StudioResource(BaseResource):
    """Studio artifact creation and management."""

    async def create(
        self,
        notebook_id: str,
        artifact_type: str,
        *,
        source_ids: list[str] | None = None,
        confirm: bool = False,
        audio_format: str = "deep_dive",
        audio_length: str = "default",
        video_format: str = "explainer",
        visual_style: str = "auto_select",
        orientation: str = "landscape",
        detail_level: str = "standard",
        slide_format: str = "detailed_deck",
        slide_length: str = "default",
        report_format: str = "Briefing Doc",
        custom_prompt: str = "",
        question_count: int = 2,
        difficulty: str = "medium",
        language: str = "en",
        focus_prompt: str = "",
        title: str = "Mind Map",
        description: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create any studio artifact.

        :param notebook_id: Notebook ID.
        :param artifact_type: Type (e.g. report, slide_deck, audio).
        :param source_ids: Optional source IDs to use.
        :param confirm: Must be True to trigger generation.
        :param audio_format: Audio format (e.g. deep_dive, brief).
        :param audio_length: short, default, long.
        :param video_format: explainer, brief.
        :param visual_style: Video/style option.
        :param orientation: Infographic orientation.
        :param detail_level: Infographic detail.
        :param slide_format: Slide deck format.
        :param slide_length: Slide deck length.
        :param report_format: Report format name.
        :param custom_prompt: Custom prompt for artifact.
        :param question_count: Quiz/flashcard count.
        :param difficulty: Quiz difficulty.
        :param language: Language code.
        :param focus_prompt: Mind map focus.
        :param title: Artifact title.
        :param description: Artifact description.
        :return: Create result (e.g. artifact_id).
        :raises ValidationError: If confirm is not True.
        """
        if not confirm:
            raise ValidationError(
                "Must set confirm=True to create studio artifact. This triggers content generation."
            )
        args = _studio_create_args(
            notebook_id,
            artifact_type,
            source_ids=source_ids,
            audio_format=audio_format,
            audio_length=audio_length,
            video_format=video_format,
            visual_style=visual_style,
            orientation=orientation,
            detail_level=detail_level,
            slide_format=slide_format,
            slide_length=slide_length,
            report_format=report_format,
            custom_prompt=custom_prompt,
            question_count=question_count,
            difficulty=difficulty,
            language=language,
            focus_prompt=focus_prompt,
            title=title,
            description=description,
            **kwargs,
        )
        return await self._call("studio_create", **args)

    async def status(
        self,
        notebook_id: str,
        *,
        action: str = "status",
        artifact_id: str | None = None,
        new_title: str | None = None,
    ) -> StudioStatus:
        """Check studio artifact status or rename an artifact.

        :param notebook_id: Notebook ID.
        :param action: status or rename.
        :param artifact_id: Optional artifact ID.
        :param new_title: New title when action is rename.
        :return: Studio status with artifact list.
        """
        result = await self._call(
            "studio_status",
            notebook_id=notebook_id,
            action=action,
            artifact_id=artifact_id,
            new_title=new_title,
        )
        return StudioStatus.model_validate(result)

    async def delete(
        self,
        notebook_id: str,
        artifact_id: str,
        *,
        confirm: bool = False,
    ) -> None:
        """Delete a studio artifact.

        :param notebook_id: Notebook ID.
        :param artifact_id: Artifact to delete.
        :param confirm: Must be True to perform delete.
        :raises ValidationError: If confirm is not True.
        """
        if not confirm:
            raise ValidationError("Must set confirm=True to delete artifact. This is irreversible.")
        await self._call(
            "studio_delete",
            notebook_id=notebook_id,
            artifact_id=artifact_id,
            confirm=True,
        )
