"""Server-side Markdown → HTML rendering.

Single source of truth for the rendered HTML stored in body_html_cache.
The frontend's react-markdown renders the editor preview only — final view
uses this output to keep parity.
"""
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin


def _build_renderer() -> MarkdownIt:
    md = MarkdownIt("gfm-like", {"html": False, "linkify": False, "typographer": True})
    md.use(tasklists_plugin, enabled=True)
    md.enable("table")
    md.enable("strikethrough")
    return md


_RENDERER = _build_renderer()


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return _RENDERER.render(text)
