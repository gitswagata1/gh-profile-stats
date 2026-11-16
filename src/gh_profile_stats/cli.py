"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from . import __version__
from .api import GitHubError, fetch_profile
from .stats import Result, improvement_tips, score_profile

BAR_WIDTH = 20


def _bar_characters() -> tuple[str, str]:
    """Use block characters when the terminal can show them, plain ASCII otherwise."""
    encoding = sys.stdout.encoding or "ascii"
    try:
        "█░".encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return "#", "-"
    return "█", "░"


def render_bar(top_percent: float) -> str:
    full, empty = _bar_characters()
    filled = int((100 - top_percent) / (100 / BAR_WIDTH))
    return full * filled + empty * (BAR_WIDTH - filled)


def render(username: str, result: Result, tips: list[str]) -> str:
    rule = "=" * 45
    lines = [f"\nGitHub profile: {username}\n", rule]
    for name, value in result.values.items():
        top = result.percentiles[name]
        lines.append(f"  {name:>10}: {value:>6}  {render_bar(top)}  top {top:.0f}%")
    lines += [rule, f"  Overall score: {result.score:.1f}", f"  Rank:          {result.rank}", ""]
    if tips:
        lines.append("How to improve:")
        lines += [f"  - {tip}" for tip in tips]
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gh-profile-stats",
        description="Analyse a GitHub profile, estimate its rank and get tips to improve it.",
    )
    parser.add_argument("username", help="GitHub username to analyse")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print machine-readable JSON")
    parser.add_argument("--no-tips", action="store_true", help="hide improvement tips")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = score_profile(fetch_profile(args.username))
    except GitHubError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.as_json:
        payload = result.to_dict()
        payload["username"] = args.username
        payload["tips"] = improvement_tips(result)
        print(json.dumps(payload, indent=2))
    else:
        tips = [] if args.no_tips else improvement_tips(result)
        print(render(args.username, result, tips))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
