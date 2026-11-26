"""对本地运行中的 v2 后端做一次端到端验收。

用法：python -m scripts.verify_e2e [http://127.0.0.1:8000/api]
"""

from __future__ import annotations

import sys
import time

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api"


def login(client: httpx.Client, username: str, password: str) -> dict[str, str]:
    response = client.post(
        f"{BASE}/auth/login", json={"username": username, "password": password}
    )
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def main() -> None:
    with httpx.Client(timeout=60) as client:
        admin_headers = login(client, "admin", "admin123")
        start = time.perf_counter()
        generated = client.post(
            f"{BASE}/reports/generate",
            headers=admin_headers,
            json={"report_date": "2026-11-06", "push": False},
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

        member_headers = login(client, "member", "member123")
        mine = client.get(f"{BASE}/reports", headers=member_headers).json()
        print(f"成员可见日报: {len(mine)} 份")
        for report in mine:
            print(
                f"  - #{report['id']} {report['report_type']} "
                f"{report.get('member_name') or ''}"
            )


if __name__ == "__main__":
    main()
