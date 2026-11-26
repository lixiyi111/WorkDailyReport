"""协作成果归属：把原始记录转成带成员与角色的条目。"""

from dataclasses import dataclass

from app.services.collectors.base import RawCommitData, RawMessageData, RawTaskData


@dataclass
class AttributedItem:
    member_id: int
    category: str
    title: str
    detail: str
    source_type: str
    source_id: str
    role: str
    sort_order: int = 0


class AttributionEngine:
    def attribute_commits(
        self, entries: list[tuple[int, RawCommitData]]
    ) -> list[AttributedItem]:
        items: list[AttributedItem] = []
        for member_id, data in entries:
            title = (data.message.splitlines() or ["(无提交说明)"])[0][:200]
            items.append(
                AttributedItem(
                    member_id=member_id,
                    category="commit",
                    title=title,
                    detail=f"{data.repo_full_name}@{data.sha[:7]}",
                    source_type="commit",
                    source_id=data.sha,
                    role="author",
                )
            )
        return items

    def attribute_tasks(
        self, entries: list[tuple[int, RawTaskData]]
    ) -> list[AttributedItem]:
        return [
            AttributedItem(
                member_id=member_id,
                category="task",
                title=data.title,
                detail=f"状态：{data.status}",
                source_type="task",
                source_id=data.task_id,
                role="owner",
            )
            for member_id, data in entries
        ]

    def attribute_messages(
        self, entries: list[tuple[int, RawMessageData]]
    ) -> list[AttributedItem]:
        return [
            AttributedItem(
                member_id=member_id,
                category="message",
                title="群消息",
                detail=(data.content or "")[:200],
                source_type="message",
                source_id=data.message_id,
                role="participant",
            )
            for member_id, data in entries
        ]

    @staticmethod
    def dedupe(items: list[AttributedItem]) -> list[AttributedItem]:
        seen: set[tuple[str, str, int, str]] = set()
        unique: list[AttributedItem] = []
        for item in items:
            key = (item.source_type, item.source_id, item.member_id, item.role)
            if key in seen:
                continue
            seen.add(key)
            item.sort_order = len(unique)
            unique.append(item)
        return unique
