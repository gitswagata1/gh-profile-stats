"""Fetch profile data from the GitHub GraphQL API through the GitHub CLI."""

from __future__ import annotations

import json
import subprocess
from typing import Any

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
    }
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER) {
      nodes { stargazerCount }
    }
  }
}
"""


class GitHubError(RuntimeError):
    """Raised when the GitHub API call fails or the user does not exist."""


def fetch_profile(username: str) -> dict[str, Any]:
    """Return the GraphQL ``user`` object for ``username``.

    Requires the GitHub CLI (``gh``) to be installed and authenticated.
    The username is passed as a GraphQL variable, never interpolated into the query.
    """
    try:
        completed = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={username}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise GitHubError("The GitHub CLI ('gh') is required. Install it from https://cli.github.com") from error

    if completed.returncode != 0:
        raise GitHubError(completed.stderr.strip() or "GitHub API request failed")

    payload = json.loads(completed.stdout)
    user = (payload.get("data") or {}).get("user")
    if user is None:
        raise GitHubError(f"User '{username}' was not found")
    return user
