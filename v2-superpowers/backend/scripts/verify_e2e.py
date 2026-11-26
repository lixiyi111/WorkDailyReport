"""对本地运行中的 v2 后端做一次端到端验收。

用法：python -m scripts.verify_e2e [http://127.0.0.1:8000/api]
"""

from __future__ import annotations

import sys
import time

import httpx

from app.core.config import get_settings

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api"
REPORT_DATE = sys.argv[2] if len(sys.argv) > 2 else "2026-11-06"


def login(client: httpx.Client, username: str, password: str) -> dict[str, str]:
    response = client.post(
        f"{BASE}/auth/login", json={"username": username, "password": password}
    )
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def main() -> None:
    settings = get_settings()
    with httpx.Client(timeout=60) as client:
        admin_headers = login(
            client, settings.auth_admin_username, settings.auth_admin_password
        )
        start = time.perf_counter()
        generated = client.post(
            f"{BASE}/reports/generate",
            headers=admin_headers,
            json={"report_date": REPORT_DATE, "push": False},
        )
        generated.raise_for_status()
        elapsed = time.perf_counter() - start
        summary = generated.json()
        print(f"生成耗时: {elapsed:.3f}s")
        print(f"生成结果: {summary}")

        reports = client.get(f"{BASE}/reports", headers=admin_headers).json()
        print(f"管理员可见日报: {len(reports)} 份")
        for report in reports:
            print(
                f"  - #{report['id']} {report['report_date']} "
                f"{report['report_type']} {report.get('member_name') or ''}"
            )

        member_headers = login(
            client, settings.auth_member_username, settings.auth_member_password
        )
        mine = client.get(f"{BASE}/reports", headers=member_headers).json()
        print(f"成员可见日报: {len(mine)} 份")
        for report in mine:
            print(
                f"  - #{report['id']} {report['report_type']} "
                f"{report.get('member_name') or ''}"
            )

        attendance = client.get(
            f"{BASE}/attendance?date={REPORT_DATE}", headers=admin_headers
        ).json()
        print(f"考勤记录: {len(attendance)} 条")
        for row in attendance:
            print(
                f"  - {row['member_name']} {row['attendance_date']} "
                f"{row['status']} {row.get('check_in_at') or '—'}"
            )
        mine_attendance = client.get(
            f"{BASE}/attendance?date={REPORT_DATE}", headers=member_headers
        ).json()
        print(f"成员可见考勤: {len(mine_attendance)} 条")

        personal = next(
            (
                report
                for report in reports
                if report["report_type"] == "personal"
                and report["report_date"] == REPORT_DATE
            ),
            None,
        )
        if personal is not None:
            detail = client.get(
                f"{BASE}/reports/{personal['id']}", headers=admin_headers
            ).json()
            print("个人日报含考勤段:", "## 考勤" in detail["content_md"])

        team = next(
            (
                report
                for report in reports
                if report["report_type"] == "team"
                and report["report_date"] == REPORT_DATE
            ),
            None,
        )
        if team is not None:
            detail = client.get(
                f"{BASE}/reports/{team['id']}", headers=admin_headers
            ).json()
            print("团队日报含考勤汇总:", "考勤：" in detail["content_md"])


if __name__ == "__main__":
    main()
