"""GitHub 提交采集。"""

from datetime import UTC, datetime

import httpx

from app.core.retry import retry_async
from app.services.collectors.base import (
    AuthError,
    CollectionResult,
    RawCommitData,
    SourceError,
    TimeWindow,
)


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC).replace(tzinfo=None)


class GitHubCollector:
    source = "github"

    def __init__(self, token: str, api_base: str, repos: list[str]) -> None:
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.repos = repos

    async def collect(self, window: TimeWindow) -> CollectionResult[RawCommitData]:
        if not self.token:
            raise AuthError("GITHUB_TOKEN 未配置")
        if not self.repos:
            return CollectionResult(
                partial=True,
                errors=[SourceError(self.source, "CONFIG", "GITHUB_REPOS 未配置")],
            )

        result: CollectionResult[RawCommitData] = CollectionResult()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            for repo in self.repos:
                try:
                    items = await retry_async(
                        lambda repo=repo: self._fetch_repo(client, repo, window, headers),
                        attempts=3,
                    )
                    result.items.extend(items)
                except httpx.HTTPStatusError as exc:
                    code = "RATE_LIMIT" if exc.response.status_code in (403, 429) else "AUTH"
                    result.partial = True
                    result.errors.append(
                        SourceError(
                            self.source,
                            code,
                            f"{repo}: HTTP {exc.response.status_code}",
                            retryable=code == "RATE_LIMIT",
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    result.partial = True
                    result.errors.append(
                        SourceError(self.source, "NETWORK", f"{repo}: {type(exc).__name__}")
                    )
        return result

    async def _fetch_repo(
        self,
        client: httpx.AsyncClient,
        repo: str,
        window: TimeWindow,
        headers: dict[str, str],
    ) -> list[RawCommitData]:
        commits: dict[str, RawCommitData] = {}
        for page in range(1, 11):
            response = await client.get(
                f"{self.api_base}/repos/{repo}/commits",
                headers=headers,
                params={
                    "since": window.start.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z"),
                    "until": window.end.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z"),
                    "per_page": 100,
                    "page": page,
                },
            )
            response.raise_for_status()
            batch = response.json()
            if not isinstance(batch, list) or not batch:
                break
            for item in batch:
                commit = item.get("commit", {})
                author = commit.get("author") or {}
                committer = commit.get("committer") or author
                date_value = committer.get("date") or author.get("date")
                if not date_value:
                    continue
                commits[item["sha"]] = RawCommitData(
                    repo_full_name=repo,
                    sha=item["sha"],
                    author_name=author.get("name") or "unknown",
                    author_email=author.get("email"),
                    committed_at=_parse_iso(date_value),
                    message=commit.get("message") or "",
                    url=item.get("html_url"),
                )
            if len(batch) < 100:
                break
        return list(commits.values())
