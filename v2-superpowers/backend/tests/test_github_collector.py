"""V2-010：GitHub 提交采集（分页、窗口、幂等、限流降级）。"""

from datetime import date, datetime

import httpx
import pytest

from app.core.contracts import AuthError
from app.core.timeutil import day_window
from app.services.collectors.github import GitHubCollector, RepoSpec

WINDOW = day_window(date(2026, 11, 6))


def _commit(sha: str, when: str, message: str = "feat: work") -> dict:
    return {
        "sha": sha,
        "commit": {
            "author": {"name": "王芳", "email": "wang@example.com"},
            "committer": {"date": when},
            "message": message,
        },
        "html_url": f"https://github.com/lixiyi111/WorkDailyReport/commit/{sha}",
    }


async def test_github_collect_window() -> None:
    """只保留窗口内的提交，并解析出关键字段。"""
    inside = _commit("a" * 40, "2026-11-06T01:00:00Z")
    outside = _commit("b" * 40, "2026-11-06T17:00:00Z")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["since"] == "2026-11-05T16:00:00Z"
        assert request.url.params["until"] == "2026-11-06T16:00:00Z"
        assert request.url.params["page"] == "1"
        return httpx.Response(200, json=[inside, outside])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = GitHubCollector(
            token="test-token",
            repos=[RepoSpec("lixiyi111", "WorkDailyReport")],
            client=client,
        )
        result = await collector.collect(WINDOW)

    assert result.partial is False
    assert len(result.items) == 1
    item = result.items[0]
    assert item.sha == "a" * 40
    assert item.repo == "lixiyi111/WorkDailyReport"
    assert item.committed_at == datetime(2026, 11, 6, 1, 0)
    assert item.author_name == "王芳"


async def test_github_dedup_by_sha() -> None:
    """同一 SHA 在同一结果中只保留一次。"""
    same = _commit("c" * 40, "2026-11-06T02:00:00Z")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["page"] == "1":
            return httpx.Response(200, json=[same, same])
        return httpx.Response(200, json=[])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = GitHubCollector(
            token="test-token",
            repos=[RepoSpec("lixiyi111", "WorkDailyReport")],
            client=client,
            per_page=2,
        )
        result = await collector.collect(WINDOW)

    assert result.partial is False
    assert [item.sha for item in result.items] == ["c" * 40]


async def test_github_rate_limit_partial() -> None:
    """403/429 重试耗尽后返回 partial，不抛异常。"""
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429, json={"message": "API rate limit exceeded"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = GitHubCollector(
            token="test-token",
            repos=[RepoSpec("lixiyi111", "WorkDailyReport")],
            client=client,
            retry_base_delay=0,
        )
        result = await collector.collect(WINDOW)

    assert calls == 3
    assert result.partial is True
    assert result.items == []
    assert result.errors[0].code == "RATE_LIMIT"
    assert result.errors[0].retryable is True


async def test_github_missing_token_raises_auth_error() -> None:
    """完全没有凭证时抛出 AuthError，而不是静默返回空结果。"""
    collector = GitHubCollector(
        token="", repos=[RepoSpec("lixiyi111", "WorkDailyReport")]
    )
    with pytest.raises(AuthError):
        await collector.collect(WINDOW)
