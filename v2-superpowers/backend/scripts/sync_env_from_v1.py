"""把 v1 的凭证配置同步到 v2 的 .env（不打印任何值）。

用法（在 v2-superpowers/backend 下）：
    python -m scripts.sync_env_from_v1 ../../v1-sdd/backend/.env .env

只同步凭证与连接配置；以下键保持 v2 自己的值：
DB_NAME、AUTH_SECRET、AUTH_MEMBER_ID、MOCK_MEMBER_EMAILS、AUTO_CREATE_TABLES。
"""

from __future__ import annotations

import sys
from pathlib import Path

COPY_KEYS = [
    "GITHUB_TOKEN",
    "GITHUB_API_BASE",
    "GITHUB_REPOS",
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_BASE_URL",
    "FEISHU_USE_MOCK",
    "FEISHU_CHAT_IDS",
    "FEISHU_REPORT_CHAT_ID",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_AUTH_CODE",
    "SMTP_FROM_NAME",
    "REPORT_RECIPIENTS",
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "AUTH_ADMIN_USERNAME",
    "AUTH_ADMIN_PASSWORD",
    "AUTH_LEADER_USERNAME",
    "AUTH_LEADER_PASSWORD",
    "AUTH_MEMBER_USERNAME",
    "AUTH_MEMBER_PASSWORD",
    "AUTH_TOKEN_EXPIRE_MINUTES",
]

RENAME = {"AUTH_TOKEN_EXPIRE_MINUTES": "ACCESS_TOKEN_EXPIRE_MINUTES"}


def parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value
    return values


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("用法: python -m scripts.sync_env_from_v1 <source> <target>")
    source = parse_env(Path(sys.argv[1]).read_text(encoding="utf-8"))
    target_path = Path(sys.argv[2])
    lines = target_path.read_text(encoding="utf-8").splitlines()

    positions: dict[str, int] = {}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        positions[stripped.split("=", 1)[0].strip()] = index

    updated: list[str] = []
    for source_key in COPY_KEYS:
        if source_key not in source or source[source_key] == "":
            continue
        target_key = RENAME.get(source_key, source_key)
        line = f"{target_key}={source[source_key]}"
        if target_key in positions:
            lines[positions[target_key]] = line
        else:
            lines.append(line)
        updated.append(target_key)

    target_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("synced keys:", ", ".join(updated))


if __name__ == "__main__":
    main()
