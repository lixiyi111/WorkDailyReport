"""V2-003：日志脱敏。"""

from app.core.logging import mask_secret


def test_mask_secret_keeps_edges() -> None:
    assert mask_secret("abcdefgh") == "ab****gh"


def test_mask_secret_short_values_fully_masked() -> None:
    assert mask_secret("abc") == "****"
    assert mask_secret("") == "****"
    assert mask_secret(None) == "****"
