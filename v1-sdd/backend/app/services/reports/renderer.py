"""Markdown 渲染辅助。"""


def render_section(title: str, lines: list[str]) -> str:
    body = "\n".join(lines) if lines else "- 无"
    return f"## {title}\n\n{body}\n"


def render_document(title: str, sections: list[tuple[str, list[str]]]) -> str:
    parts = [f"# {title}\n"]
    parts.extend(render_section(section_title, lines) for section_title, lines in sections)
    return "\n".join(parts)
