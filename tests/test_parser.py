from core.parser import parse_query


def test_parse_platform_and_text() -> None:
    parsed = parse_query("platform:reddit AI engineer")
    assert parsed.platform == "reddit"
    assert parsed.text == "AI engineer"


def test_parse_tag_query() -> None:
    parsed = parse_query("tag:python internship")
    assert parsed.tag == "python"
    assert parsed.text == "internship"


def test_parse_phrase() -> None:
    parsed = parse_query('"computer vision"')
    assert parsed.phrases == ["computer vision"]


def test_parse_exclusion() -> None:
    parsed = parse_query("AI -senior")
    assert parsed.text == "AI"
    assert parsed.excluded_terms == ["senior"]


def test_parse_date_filter() -> None:
    parsed = parse_query("after:2026-08-01 AI")
    assert parsed.after is not None
