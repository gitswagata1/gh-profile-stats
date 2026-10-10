#!/usr/bin/env python3
"""GitHub Profile Stats Analyzer - check your rank and get tips to improve."""

import json
import math
import subprocess
import sys


def get_stats(username):
    query = '{user(login:"%s"){contributionsCollection{totalCommitContributions totalPullRequestContributions totalPullRequestReviewContributions totalIssueContributions}followers{totalCount}repositories(first:100,ownerAffiliations:OWNER){nodes{stargazerCount}}}}' % username
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", "query=" + query],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)["data"]["user"]


def calc_percentile(value, median):
    if value == 0:
        return 100.0
    k = -math.log(0.5) / median
    return max(0, 100 - 100 * (1 - math.exp(-k * value)))


def get_rank(stats):
    cc = stats["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in stats["repositories"]["nodes"])
    metrics = {
        "commits": (cc["totalCommitContributions"], 250),
        "prs": (cc["totalPullRequestContributions"], 50),
        "issues": (cc["totalIssueContributions"], 25),
        "reviews": (cc["totalPullRequestReviewContributions"], 2),
        "stars": (stars, 50),
        "followers": (stats["followers"]["totalCount"], 10),
    }
    percentiles = {k: calc_percentile(v, m) for k, (v, m) in metrics.items()}
    weights = {"commits": 2, "prs": 3, "issues": 1, "reviews": 1, "stars": 4, "followers": 1}
    total_w = sum(weights.values())
    overall = sum(percentiles[k] * weights[k] for k in percentiles) / total_w
    ranks = [("S+", 1), ("S", 12.5), ("A++", 25), ("A+", 37.5), ("B+", 50), ("B", 62.5), ("C", 100)]
    rank = "C"
    for label, threshold in ranks:
        if overall <= threshold:
            rank = label
            break
    return rank, overall, percentiles, metrics


def main():
    if len(sys.argv) < 2:
        print("Usage: python gh_profile_stats.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    print(f"\nAnalyzing GitHub profile: {username}\n")
    stats = get_stats(username)
    rank, score, percentiles, metrics = get_rank(stats)
    print("=" * 45)
    for name, (value, _) in metrics.items():
        pct = percentiles[name]
        filled = int((100 - pct) / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"  {name:>10}: {value:>6}  {bar}  top {pct:.0f}%")
    print("=" * 45)
    print(f"  Overall Score: {score:.1f}")
    print(f"  Current Rank:  {rank}")
    print()


if __name__ == "__main__":
    main()
