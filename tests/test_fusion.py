from core.fusion import rrf


def test_rrf_fuses_rankings() -> None:
    rankings = [["d1", "d2", "d3"], ["d2", "d4", "d1"]]
    scores = rrf(rankings, k=60)
    assert scores["d2"] > scores["d3"]
    assert scores["d1"] > 0
