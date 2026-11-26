"""考勤采集：飞书真实模式 + 无凭证 Mock，按「成员 + 日期」聚合。"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import httpx

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow
from app.services.collectors.common import FetchError
from app.services.collectors.feishu_base import FeishuBase

_SHANGHAI = ZoneInfo("Asia/Shanghai")
_STATUS_PRIORITY = {
    "normal": 0,
    "early": 1,
    "late": 2,
    "leave": 3,
    "absent": 4,
    "holiday": 5,
}


@dataclass(frozen=True)
class AttendanceRecord:
    member_external_id: str
    attendance_date: date
    status: str
    check_in_at: datetime | None
    check_out_at: datetime | None
    source_id: str | None = None


def _local_to_utc(day: date, hour: int, minute: int = 0) -> datetime:
    local = datetime.combine(day, time(hour, minute), tzinfo=_SHANGHAI)
    return local.astimezone(UTC).replace(tzinfo=None)


def _parse_date(value: object) -> date:
    if isinstance(value, int) or (
        isinstance(value, str) and value.isdigit() and len(value) == 8
    ):
        number = int(value)
        return date(number // 10000, number // 100 % 100, number % 100)
    return date.fromisoformat(str(value))


def _parse_dt(value: object) -> datetime | None:
    if value is None or value == "":
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_SHANGHAI)
    return parsed.astimezone(UTC).replace(tzinfo=None)


class MockAttendanceCollector:
    source = "feishu_attendance"

    def __init__(self, member_emails: list[str]) -> None:
        self.member_emails = member_emails

    async def collect(self, window: TimeWindow) -> CollectionResult[AttendanceRecord]:
        report_day = (window.start + timedelta(hours=8)).date()
        statuses = ["normal", "late", "leave"]
        items: list[AttendanceRecord] = []
        for index, email in enumerate(self.member_emails):
            status = statuses[index % len(statuses)]
            if status == "leave":
                check_in = check_out = None
            else:
                offset = 30 if status == "late" else 0
                check_in = _local_to_utc(report_day, 9, offset)
                check_out = _local_to_utc(report_day, 18)
            items.append(
                AttendanceRecord(
                    member_external_id=f"mock-{email.split('@', 1)[0]}",
                    attendance_date=report_day,
                    status=status,
                    check_in_at=check_in,
                    check_out_at=check_out,
                    source_id=f"mock-att-{report_day.isoformat()}-{index}",
                )
            )
        return CollectionResult(items=items)


class FeishuAttendanceCollector(FeishuBase):
    source = "feishu_attendance"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        member_external_ids: list[str],
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout: float = 15.0,
        attempts: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        super().__init__(
            app_id,
            app_secret,
            client=client,
            base_url=base_url,
            timeout=timeout,
            attempts=attempts,
            retry_base_delay=retry_base_delay,
        )
        self.member_external_ids = member_external_ids

    async def collect(self, window: TimeWindow) -> CollectionResult[AttendanceRecord]:
        if not self.app_id or not self.app_secret:
            raise AuthError("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")
        if not self.member_external_ids:
            return CollectionResult(items=[])
        if self._client is not None:
            return await self._collect(self._client, window)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._collect(client, window)

    async def _collect(
        self, client: httpx.AsyncClient, window: TimeWindow
    ) -> CollectionResult[AttendanceRecord]:
        try:
            token = await self._get_token(client)
        except FetchError as exc:
            return CollectionResult(
                items=[],
                partial=True,
                errors=[
                    SourceError(
                        source=self.source,
                        code=exc.code,
                        message=exc.message,
                        retryable=exc.retryable,
                    )
                ],
            )

        report_day = (window.start + timedelta(hours=8)).date()
        day_number = int(report_day.strftime("%Y%m%d"))
        try:
            payload = await self._request_json(
                client,
                "POST",
                "/open-apis/attendance/v1/user_tasks/query",
                token=token,
                json_body={
                    "user_ids": self.member_external_ids,
                    "check_date_from": day_number,
                    "check_date_to": day_number,
                },
            )
        except FetchError as exc:
            return CollectionResult(
                items=[],
                partial=True,
                errors=[
                    SourceError(
                        source=self.source,
                        code=exc.code,
                        message=exc.message,
                        retryable=exc.retryable,
                    )
                ],
            )

        raw_items = (payload.get("data") or {}).get("items") or []
        records: list[AttendanceRecord] = []
        errors: list[SourceError] = []
        partial = False
        for raw in raw_items:
            try:
                records.append(self._parse(raw))
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(
                    SourceError(
                        source=self.source,
                        code="PARSE",
                        message=f"考勤解析失败: {exc}",
                    )
                )
                partial = True

        return CollectionResult(
            items=self._aggregate(records), partial=partial, errors=errors
        )

    def _parse(self, raw: dict) -> AttendanceRecord:
        return AttendanceRecord(
            member_external_id=str(raw["user_id"]),
            attendance_date=_parse_date(raw["check_date"]),
            status=str(raw.get("status") or "normal"),
            check_in_at=_parse_dt(raw.get("check_in")),
            check_out_at=_parse_dt(raw.get("check_out")),
            source_id=str(raw["id"]) if raw.get("id") else None,
        )

    def _aggregate(
        self, records: list[AttendanceRecord]
    ) -> list[AttendanceRecord]:
        grouped: dict[tuple[str, date], list[AttendanceRecord]] = defaultdict(list)
        for record in records:
            grouped[(record.member_external_id, record.attendance_date)].append(
                record
            )

        merged: list[AttendanceRecord] = []
        for (member_external_id, attendance_date), rows in grouped.items():
            check_ins = [row.check_in_at for row in rows if row.check_in_at]
            check_outs = [row.check_out_at for row in rows if row.check_out_at]
            status = max(
                (row.status for row in rows),
                key=lambda value: _STATUS_PRIORITY.get(value, 0),
            )
            merged.append(
                AttendanceRecord(
                    member_external_id=member_external_id,
                    attendance_date=attendance_date,
                    status=status,
                    check_in_at=min(check_ins) if check_ins else None,
                    check_out_at=max(check_outs) if check_outs else None,
                    source_id=rows[0].source_id,
                )
            )
        return sorted(merged, key=lambda row: (row.member_external_id, row.attendance_date))
