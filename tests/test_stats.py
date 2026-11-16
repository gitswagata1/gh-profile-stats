import pytest

from gh_profile_stats.stats import (
    improvement_tips,
    percentile,
    rank_for,
    score_profile,
)


def make_profile(commits=0, prs=0, issues=0, reviews=0, stars=0, followers=0):
    return {
        "contributionsCollection": {
            "totalCommitContributions": commits,
            "totalPullRequestContributions": prs,
            "totalIssueContributions": issues,
            "totalPullRequestReviewContributions": reviews,
        },
        "followers": {"totalCount": followers},
        "repositories": {"nodes": [{"stargazerCount": stars}]},
    }


def test_zero_activity_is_worst_percentile():
    assert percentile(0, 50) == 100.0


def test_median_value_is_fiftieth_percentile():
    assert percentile(250, 250) == pytest.approx(50.0)


def test_more_activity_gives_better_percentile():
    assert percentile(1000, 250) < percentile(100, 250)


@pytest.mark.parametrize(
    "score, expected",
    [(0.5, "S+"), (10, "S"), (30, "A+"), (50, "B+"), (62.5, "B"), (99, "C")],
)
def test_rank_thresholds(score, expected):
    assert rank_for(score) == expected


def test_empty_profile_ranks_c():
    result = score_profile(make_profile())
    assert result.rank == "C"
    assert result.score == pytest.approx(100.0)


def test_strong_profile_ranks_better_than_empty():
    strong = score_profile(make_profile(2000, 500, 300, 100, 1000, 500))
    assert strong.score < 10
    assert strong.rank in {"S+", "S"}


def test_stars_are_summed_across_repositories():
    profile = make_profile()
    profile["repositories"]["nodes"] = [{"stargazerCount": 3}, {"stargazerCount": 4}]
    assert score_profile(profile).values["stars"] == 7


def test_tips_target_the_weakest_weighted_metrics():
    result = score_profile(make_profile(commits=5000, followers=1000))
    tips = improvement_tips(result, count=2)
    assert len(tips) == 2
    assert not any(tip.startswith("commits") for tip in tips)


def test_to_dict_is_json_serialisable():
    import json

    json.dumps(score_profile(make_profile(10, 2, 1, 0, 3, 4)).to_dict())
