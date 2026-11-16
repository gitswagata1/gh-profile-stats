import pytest

from gh_profile_stats.api import GitHubError, fetch_profile


def test_pagination_collects_all_repositories(monkeypatch):
    pages = [
        {
            "data": {
                "user": {
                    "contributionsCollection": {"totalCommitContributions": 1},
                    "followers": {"totalCount": 2},
                    "repositories": {
                        "nodes": [{"stargazerCount": 1}, {"stargazerCount": 2}],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    },
                }
            }
        },
        {
            "data": {
                "user": {
                    "contributionsCollection": {"totalCommitContributions": 1},
                    "followers": {"totalCount": 2},
                    "repositories": {
                        "nodes": [{"stargazerCount": 3}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    },
                }
            }
        },
    ]

    def fake_run(username, after=None):
        if after is None:
            return pages[0]
        if after == "cursor1":
            return pages[1]
        raise AssertionError(f"unexpected cursor {after}")

    monkeypatch.setattr("gh_profile_stats.api._run_query", fake_run)
    result = fetch_profile("octocat")
    assert len(result["repositories"]["nodes"]) == 3
    assert sum(n["stargazerCount"] for n in result["repositories"]["nodes"]) == 6
    assert result["followers"]["totalCount"] == 2


def test_missing_user_raises(monkeypatch):
    monkeypatch.setattr(
        "gh_profile_stats.api._run_query",
        lambda username, after=None: {"data": {"user": None}},
    )
    with pytest.raises(GitHubError, match="not found"):
        fetch_profile("nobody")
