"""Fetch profile data from the GitHub GraphQL API through the GitHub CLI."""

from __future__ import annotations

import json
import subprocess
from typing import Any

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
    }
    followers { totalCount }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER) {
      nodes { stargazerCount }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""


class GitHubError(RuntimeError):
    """Raised when the GitHub API call fails or the user does not exist."""


def _run_query(username: str, after: str | None = None) -> dict[str, Any]:
    """Run one GraphQL query page and return the parsed payload."""
    cmd = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={username}"]
    if after is not None:
        cmd.extend(["-F", f"after={after}"])
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise GitHubError("The GitHub CLI ('gh') is required. Install it from https://cli.github.com") from error

    if completed.returncode != 0:
        raise GitHubError(completed.stderr.strip() or "GitHub API request failed")

    return json.loads(completed.stdout)


def fetch_profile(username: str) -> dict[str, Any]:
    """Return the GraphQL ``user`` object for ``username``.

    Requires the GitHub CLI (``gh``) to be installed and authenticated.
    The username is passed as a GraphQL variable, never interpolated into the query.
    Repositories are fully paginated so star counts are not limited to the first 100.
    """
    all_nodes: list[dict[str, Any]] = []
    after: str | None = None
    user: dict[str, Any] | None = None

    while True:
        payload = _run_query(username, after)
        current_user = (payload.get("data") or {}).get("user")
        if current_user is None:
            raise GitHubError(f"User '{username}' was not found")

        if user is None:
            # Keep the non-paginated fields from the first page.
            user = {
                "contributionsCollection": current_user["contributionsCollection"],
                "followers": current_user["followers"],
                "repositories": {"nodes": []},
            }

        repos = current_user["repositories"]
        all_nodes.extend(repos.get("nodes") or [])
        page_info = repos.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break

    assert user is not None
    user["repositories"]["nodes"] = all_nodes
    return user
