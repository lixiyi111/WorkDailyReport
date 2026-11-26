"""按配置装配采集器、推送器与编排器。"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.services.collectors import (
    FeishuClient,
    FeishuMessageCollector,
    FeishuTaskCollector,
    GitHubCollector,
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.orchestrator import DailyReportOrchestrator
from app.services.pushers import ConsolePusher, EmailPusher, FeishuBotPusher


def build_collectors(settings: Settings, *, demo: bool = False) -> list:
    emails = settings.mock_member_email_list or None
    if demo:
        return [
            MockGitHubCollector(emails),
            MockFeishuTaskCollector(emails),
            MockFeishuMessageCollector(emails),
        ]

    collectors: list = [
        GitHubCollector(settings.github_token, settings.github_api_base, settings.github_repo_list)
    ]
    if settings.feishu_use_mock:
        collectors.extend(
            [MockFeishuTaskCollector(emails), MockFeishuMessageCollector(emails)]
        )
    else:
        feishu = FeishuClient(
            settings.feishu_app_id,
            settings.feishu_app_secret,
            settings.feishu_base_url,
        )
        collectors.extend(
            [
                FeishuTaskCollector(feishu),
                FeishuMessageCollector(feishu, settings.feishu_chat_id_list),
            ]
        )
    return collectors


def build_pushers(settings: Settings, *, demo: bool = False) -> list:
    pushers = [ConsolePusher()]
    if not demo:
        pushers.append(
            EmailPusher(
                settings.smtp_host,
                settings.smtp_port,
                settings.smtp_user,
                settings.smtp_auth_code,
                settings.smtp_from_name,
            )
        )
        if not settings.feishu_use_mock:
            pushers.append(
                FeishuBotPusher(
                    settings.feishu_app_id,
                    settings.feishu_app_secret,
                    settings.feishu_base_url,
                )
            )
    return pushers


def build_orchestrator(
    session: AsyncSession, settings: Settings, *, demo: bool = False
) -> DailyReportOrchestrator:
    return DailyReportOrchestrator(
        session=session,
        collectors=build_collectors(settings, demo=demo),
        pushers=build_pushers(settings, demo=demo),
        settings=settings,
    )
