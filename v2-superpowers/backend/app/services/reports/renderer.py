"""Markdown 文档渲染：标题 + 二级小节，空小节统一输出「- 无」。"""

from __future__ import annotations


def render_document(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    for heading, body in sections:
        lines.append(f"## {heading}")
        lines.extend(body if body else ["- 无"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
