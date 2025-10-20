"""Utilities to render HTML templates for the Qt WebEngine views."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


_UI_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _UI_DIR / "templates"


class TemplateRenderer:
    """Wrapper around Jinja2 to render UI templates."""

    def __init__(self) -> None:
        loader = FileSystemLoader(str(_TEMPLATES_DIR))
        self._env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self._env.get_template(template_name)
        return template.render(**context)


# A shared renderer instance is enough for the whole application.
renderer = TemplateRenderer()

