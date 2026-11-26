"""根据配置装配采集器与推送器。"""

from __future__ import annotations

from app.core.config import Settings
from app.services.collectors.feishu_messages import FeishuMessageCollector
from app.services.collectors.feishu_tasks import FeishuTaskCollector
from app.services.collectors.github import GitHubCollector, RepoSpec
from app.services.collectors.mock import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.orchestrator import CollectorSet
from app.services.pushers.console import ConsolePusher
from app.services.pushers.email import EmailPusher
from app.services.pushers.feishu_bot import FeishuBotPusher


def _csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def build_collectors(settings: Settings) -> CollectorSet:
    repos: list[RepoSpec] = []
    for item in _csv(settings.github_repos):
        if "/" in item:
            owner, name = item.split("/", 1)
            repos.append(RepoSpec(owner=owner, name=name))
    emails = _csv(settings.mock_member_emails)
    chat_ids = _csv(settings.feishu_chat_ids)

    if settings.feishu_use_mock or not (
        settings.feishu_app_id and settings.feishu_app_secret
    ):
        tasks = MockFeishuTaskCollector(emails)
        messages = MockFeishuMessageCollector(
            emails, chat_id=chat_ids[0] if chat_ids else "oc_mock"
        )
    else:
        tasks = FeishuTaskCollector(
            settings.feishu_app_id,
            settings.feishu_app_secret,
            base_url=settings.feishu_base_url,
        )
        messages = FeishuMessageCollector(
            settings.feishu_app_id,
            settings.feishu_app_secret,
            chat_ids=chat_ids,
            base_url=settings.feishu_base_url,
        )

    if settings.github_token and repos:
        github = GitHubCollector(
            settings.github_token,
            repos,
            api_base=settings.github_api_base,
        )
    else:
        github = MockGitHubCollector(repos, emails)

    return CollectorSet(github=github, tasks=tasks, messages=messages)


def build_pushers(settings: Settings) -> list:
    pushers: list = []
    if settings.smtp_user and settings.smtp_auth_code:
        pushers.append(
            EmailPusher(
                host=settings.smtp_host,
                port=settings.smtp_port,
                user=settings.smtp_user,
                auth_code=settings.smtp_auth_code,
                from_name=settings.smtp_from_name,
            )
        )
    pushers.append(
        FeishuBotPusher(
            settings.feishu_app_id,
            settings.feishu_app_secret,
            use_mock=settings.feishu_use_mock
            or not (settings.feishu_app_id and settings.feishu_app_secret),
            base_url=settings.feishu_base_url,
        )
    )
    pushers.append(ConsolePusher())
    return pushers
