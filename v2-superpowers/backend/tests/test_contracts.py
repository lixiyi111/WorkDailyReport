"""V2-003：采集结果与错误契约。"""

from app.core.contracts import CollectionResult, SourceError


def test_collection_result_partial() -> None:
    """单数据源失败时，结果仍可携带部分数据与错误。"""
    error = SourceError(
        source="github", code="RATE_LIMIT", message="limited", retryable=True
    )
    result = CollectionResult(items=[1, 2], partial=True, errors=[error])
    assert result.partial is True
    assert result.items == [1, 2]
    assert result.errors[0].code == "RATE_LIMIT"
    assert result.errors[0].retryable is True


def test_collection_result_defaults() -> None:
    """默认非降级、无错误、无游标。"""
    result = CollectionResult(items=[])
    assert result.partial is False
    assert result.errors == []
    assert result.cursor is None
