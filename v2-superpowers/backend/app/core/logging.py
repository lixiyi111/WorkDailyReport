"""日志与凭证脱敏。"""

from __future__ import annotations


def mask_secret(value: str | None) -> str:
    """保留首尾各 2 位，其余掩码；短值全部掩码。"""
    if not value or len(value) <= 4:
        return "****"
    return f"{value[:2]}****{value[-2:]}"
