"""Scoring logic: turn raw GitHub activity into percentiles, an overall score and a rank."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping

#: (median value, weight) for each metric. The median anchors the percentile curve.
METRICS: dict[str, tuple[float, int]] = {
    "commits": (250, 2),
    "prs": (50, 3),
    "issues": (25, 1),
    "reviews": (2, 1),
    "stars": (50, 4),
    "followers": (10, 1),
}

#: Rank labels with the upper bound (in percent) of the overall score that earns them.
RANKS: list[tuple[str, float]] = [
    ("S+", 1),
    ("S", 12.5),
    ("A++", 25),
    ("A+", 37.5),
    ("B+", 50),
    ("B", 62.5),
    ("C", 100),
]

TIPS: dict[str, str] = {
    "commits": "Commit regularly. Small, frequent commits to your own projects add up.",
    "prs": "Open pull requests, including to open-source projects. Docs fixes count.",
    "issues": "File clear bug reports and feature requests on projects you use.",
    "reviews": "Review other people's pull requests; reviews are rare and highly weighted.",
    "stars": "Write strong READMEs, add topics and share your best projects to earn stars.",
    "followers": "Be active in the community: contribute, comment and share your work.",
}


@dataclass(frozen=True)
class Result:
    """The outcome of scoring one GitHub profile."""

    rank: str
    score: float
    values: dict[str, int] = field(default_factory=dict)
    percentiles: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "score": round(self.score, 1),
            "metrics": {
                name: {"value": self.values[name], "top_percent": round(self.percentiles[name], 1)}
                for name in self.values
            },
        }


def percentile(value: float, median: float) -> float:
    """Return the 'top X%' position of ``value`` (lower is better) on an exponential curve."""
    if value <= 0:
        return 100.0
    k = -math.log(0.5) / median
    return max(0.0, 100 - 100 * (1 - math.exp(-k * value)))


def extract_values(profile: Mapping[str, Any]) -> dict[str, int]:
    """Pull the six scored numbers out of a GraphQL ``user`` object."""
    contributions = profile["contributionsCollection"]
    stars = sum(repo["stargazerCount"] for repo in profile["repositories"]["nodes"])
    return {
        "commits": contributions["totalCommitContributions"],
        "prs": contributions["totalPullRequestContributions"],
        "issues": contributions["totalIssueContributions"],
        "reviews": contributions["totalPullRequestReviewContributions"],
        "stars": stars,
        "followers": profile["followers"]["totalCount"],
    }


def rank_for(score: float) -> str:
    """Map an overall score (0 is best, 100 is worst) to a rank label."""
    for label, threshold in RANKS:
        if score <= threshold:
            return label
    return RANKS[-1][0]


def score_profile(profile: Mapping[str, Any]) -> Result:
    """Score a GraphQL ``user`` object."""
    values = extract_values(profile)
    percentiles = {name: percentile(values[name], METRICS[name][0]) for name in METRICS}
    total_weight = sum(weight for _, weight in METRICS.values())
    score = sum(percentiles[name] * METRICS[name][1] for name in METRICS) / total_weight
    return Result(rank=rank_for(score), score=score, values=values, percentiles=percentiles)


def improvement_tips(result: Result, count: int = 3) -> list[str]:
    """Return tips for the weakest metrics, weighted by how much each one matters."""
    ordered = sorted(
        METRICS,
        key=lambda name: result.percentiles[name] * METRICS[name][1],
        reverse=True,
    )
    return [f"{name}: {TIPS[name]}" for name in ordered[:count]]
