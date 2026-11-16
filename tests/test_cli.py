import json

from gh_profile_stats import cli
from gh_profile_stats.api import GitHubError

PROFILE = {
    "contributionsCollection": {
        "totalCommitContributions": 100,
        "totalPullRequestContributions": 20,
        "totalIssueContributions": 5,
        "totalPullRequestReviewContributions": 2,
    },
    "followers": {"totalCount": 9},
    "repositories": {"nodes": [{"stargazerCount": 1}]},
}


def test_json_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_profile", lambda username: PROFILE)
    assert cli.main(["octocat", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["username"] == "octocat"
    assert {"rank", "score", "metrics", "tips"} <= payload.keys()


def test_text_output_includes_rank_and_tips(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_profile", lambda username: PROFILE)
    assert cli.main(["octocat"]) == 0
    output = capsys.readouterr().out
    assert "Rank:" in output
    assert "How to improve:" in output


def test_api_errors_return_nonzero(monkeypatch, capsys):
    def boom(username):
        raise GitHubError("User 'nobody' was not found")

    monkeypatch.setattr(cli, "fetch_profile", boom)
    assert cli.main(["nobody"]) == 1
    assert "not found" in capsys.readouterr().err


def test_bar_falls_back_to_ascii_on_legacy_terminals(monkeypatch):
    class LegacyStdout:
        encoding = "cp1252"

    monkeypatch.setattr(cli.sys, "stdout", LegacyStdout())
    assert set(cli.render_bar(50)) <= {"#", "-"}
