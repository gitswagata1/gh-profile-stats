# gh-profile-stats

> CLI tool to analyze your GitHub profile stats, contribution rank, and get actionable tips to improve your GitHub presence.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Analyze your GitHub contribution stats (commits, PRs, issues, reviews, stars)
- Calculate your github-readme-stats rank
- Get personalized tips to improve your rank
- Beautiful terminal output with progress bars

## Installation

```bash
pip install gh-profile-stats
```

## Usage

```bash
# Analyze your profile
python gh_profile_stats.py <username>
```

## Example Output

```
Analyzing GitHub profile: gitswagata1

========================================
     commits:    411  ████████████████░░░░  top 19%
         prs:    162  ██████████████████░░  top 7%
      issues:     52  ███████████████░░░░░  top 22%
     reviews:     17  ████████████████████  top 0%
       stars:      0  ░░░░░░░░░░░░░░░░░░░░  top 100%
   followers:      6  ████████░░░░░░░░░░░░  top 58%
========================================
  Overall Score: 45.2
  Current Rank:  B
```

## How It Works

Uses the GitHub GraphQL API to fetch your contribution data and calculates rank using the same algorithm as [github-readme-stats](https://github.com/anuraghazra/github-readme-stats).

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
