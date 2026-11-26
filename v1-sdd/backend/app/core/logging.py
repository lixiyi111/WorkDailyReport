"""日志与敏感信息掩码。"""

import logging
import re

_SECRET_PATTERNS = (
    re.compile(r"(github_pat_[A-Za-z0-9_]+)"),
    re.compile(r"(cli_[A-Za-z0-9]+)"),
    re.compile(r"(?i)((?:app_secret|auth_code|password|token)\s*=\s*)([^\s&]+)"),
)


def mask_secret(value: str, keep: int = 4) -> str:
    """保留首尾少量字符，其余用 * 代替。"""
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "*" * len(value)
    return f"{value[:keep]}{'*' * (len(value) - keep * 2)}{value[-keep:]}"


def mask_text(text: str) -> str:
    """对日志文本中的常见凭证做掩码。"""
    masked = text
    for pattern in _SECRET_PATTERNS:
        if pattern.groups >= 2:
            masked = pattern.sub(lambda m: f"{m.group(1)}{mask_secret(m.group(2))}", masked)
        else:
            masked = pattern.sub(lambda m: mask_secret(m.group(1)), masked)
    return masked


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
