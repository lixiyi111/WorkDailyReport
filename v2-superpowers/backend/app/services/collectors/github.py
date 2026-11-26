"""GitHub 提交采集。

- 按仓库分页拉取；
- 只保留时间窗口内的提交；
- 按 (repo, sha) 去重；
- 403/429 指数退避重试，耗尽后返回 partial；
- 无 token 抛 AuthError。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow


@dataclass(frozen=True)
class RepoSpec:
    owner: str
    name: str
    default_branch: str = "main"


@dataclass(frozen=True)
class CommitRecord:
    repo: str
    sha: str
    author_name: str
    author_email: str | None
    committed_at: datetime
    message: str
    branch: str | None = None
    url: str | None = None
    pr_number: int | None = None


class _FetchError(Exception):
    def __init__(self, code: str, message: str, retryable: bool) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def _parse_github_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).replace(tzinfo=None)


class GitHubCollector:
    source = "github"

    def __init__(
        self,
        token: str,
        repos: list[RepoSpec],
        *,
        client: httpx.AsyncClient | None = None,
        api_base: str = "https://api.github.com",
        timeout: float = 15.0,
        per_page: int = 100,
        attempts: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        self.token = token
        self.repos = repos
        self._client = client
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.per_page = per_page
        self.attempts = attempts
        self.retry_base_delay = retry_base_delay

    async def collect(self, window: TimeWindow) -> CollectionResult[CommitRecord]:
        if not self.token:
            raise AuthError("缺少 GITHUB_TOKEN，无法采集 GitHub 提交")
        if self._client is not None:
            return await self._collect(self._client, window)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._collect(client, window)

    async def _collect(
        self, client: httpx.AsyncClient, window: TimeWindow
    ) -> CollectionResult[CommitRecord]:
        items: list[CommitRecord] = []
        errors: list[SourceError] = []
        partial = False
        seen: set[tuple[str, str]] = set()

        for repo in self.repos:
            repo_key = f"{repo.owner}/{repo.name}"
            page = 1
            while True:
                try:
                    payload = await self._fetch_page(client, repo, window, page)
                except AuthError:
                    raise
                except _FetchError as exc:
                    errors.append(
                        SourceError(
                            source=self.source,
                            code=exc.code,
                            message=exc.message,
                            retryable=exc.retryable,
                        )
                    )
                    partial = True
                    break

                if not isinstance(payload, list):
                    errors.append(
                        SourceError(
                            source=self.source,
                            code="PARSE",
                            message="GitHub commits 返回不是列表",
                        )
                    )
                    partial = True
                    break
                if not payload:
                    break

                for raw in payload:
                    try:
                        item = self._parse(repo, raw)
                    except (KeyError, TypeError, ValueError) as exc:
                        errors.append(
                            SourceError(
                                source=self.source,
                                code="PARSE",
                                message=f"提交解析失败: {exc}",
                            )
                        )
                        partial = True
                        continue
                    if not window.contains(item.committed_at):
                        continue
                    key = (repo_key, item.sha)
                    if key in seen:
                        continue
                    seen.add(key)
                    items.append(item)

                if len(payload) < self.per_page:
                    break
                page += 1

        return CollectionResult(items=items, partial=partial, errors=errors)

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        repo: RepoSpec,
        window: TimeWindow,
        page: int,
    ) -> object:
        url = f"{self.api_base}/repos/{repo.owner}/{repo.name}/commits"
        params = {
            "since": window.start.isoformat(timespec="seconds") + "Z",
            "until": window.end.isoformat(timespec="seconds") + "Z",
            "per_page": self.per_page,
            "page": page,
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        for attempt in range(1, self.attempts + 1):
            try:
                response = await client.get(url, params=params, headers=headers)
            except httpx.HTTPError as exc:
                raise _FetchError("NETWORK", str(exc), retryable=True) from exc

            if response.status_code in (403, 429):
                if attempt < self.attempts:
                    delay = self.retry_base_delay * (2 ** (attempt - 1))
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                raise _FetchError("RATE_LIMIT", response.text, retryable=True)
            if response.status_code == 401:
                raise AuthError("GitHub token 无效或已过期")
            if response.status_code >= 400:
                raise _FetchError(
                    "NETWORK",
                    f"GitHub HTTP {response.status_code}: {response.text}",
                    retryable=False,
                )
            return response.json()

        raise _FetchError("RATE_LIMIT", "重试次数耗尽", retryable=True)

    def _parse(self, repo: RepoSpec, raw: dict) -> CommitRecord:
        commit = raw["commit"]
        author = commit.get("author") or {}
        committed_at = _parse_github_datetime(commit["committer"]["date"])
        return CommitRecord(
            repo=f"{repo.owner}/{repo.name}",
            sha=raw["sha"],
            author_name=author.get("name")
            or (raw.get("author") or {}).get("login")
            or "unknown",
            author_email=author.get("email"),
            committed_at=committed_at,
            message=commit.get("message", ""),
            branch=repo.default_branch,
            url=raw.get("html_url"),
            pr_number=None,
        )
