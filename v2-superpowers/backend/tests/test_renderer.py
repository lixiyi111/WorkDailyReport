"""V2-024：Markdown 渲染器（稳定输出、空段兜底）。"""

from app.services.reports.renderer import render_document


def test_render_document_stable_output() -> None:
    sections = [
        ("今日完成", ["- 修复登录接口", "- 完成登录联调"]),
        ("协作贡献", []),
    ]
    first = render_document("王芳 · 个人日报（2026-11-06）", sections)
    second = render_document("王芳 · 个人日报（2026-11-06）", sections)

    assert first == second
    assert first.startswith("# 王芳 · 个人日报（2026-11-06）")
    assert "## 今日完成" in first
    assert "- 修复登录接口" in first
    assert "## 协作贡献\n- 无" in first
    assert first.endswith("\n")
