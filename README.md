<div align="center">

# gh-profile-stats

A command-line tool that scores your GitHub profile, estimates your rank and tells you
exactly what to improve.

[![CI](https://github.com/gitswagata1/gh-profile-stats/actions/workflows/ci.yml/badge.svg)](https://github.com/gitswagata1/gh-profile-stats/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/runtime_dependencies-0-success)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

## Table of contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example output](#example-output)
- [How scoring works](#how-scoring-works)
- [Development](#development)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- Pulls commits, pull requests, issues, reviews, stars and followers from the GitHub GraphQL API
- Converts each metric into a "top X%" position, then an overall score and rank
- **Actionable tips** targeting your weakest, highest-weighted metrics
- `--json` output for dashboards, scripts and README automation
- Zero runtime dependencies; uses the GitHub CLI for authentication
- Safe by design: the username is passed as a GraphQL variable, never interpolated into the query

## Installation

**Prerequisites:** Python 3.9+ and the [GitHub CLI](https://cli.github.com), signed in with
`gh auth login`.

```bash
pip install git+https://github.com/gitswagata1/gh-profile-stats.git
```

## Usage

```bash
gh-profile-stats <username>              # human-readable report
gh-profile-stats <username> --json       # machine-readable output
gh-profile-stats <username> --no-tips    # hide the improvement tips
```

You can also run it as a module: `python -m gh_profile_stats <username>`.

## Example output

```
GitHub profile: gitswagata1

=============================================
     commits:    822  #################---  top 10%
         prs:    190  ##################--  top 7%
      issues:    138  ###################-  top 2%
     reviews:     18  ###################-  top 0%
       stars:      1  --------------------  top 99%
   followers:      9  #########-----------  top 54%
=============================================
  Overall score: 41.0
  Rank:          B+

How to improve:
  - stars: Write strong READMEs, add topics and share your best projects to earn stars.
  - followers: Be active in the community: contribute, comment and share your work.
  - prs: Open pull requests, including to open-source projects. Docs fixes count.
```

On terminals that cannot display block characters (for example older Windows consoles) the
bars fall back to plain ASCII.

## How scoring works

Each metric is compared against a median value on an exponential curve, giving a "top X%"
position (lower is better). The overall score is the weighted average of those positions.

| Metric    | Median | Weight |
| --------- | ------ | ------ |
| Commits   | 250    | 2      |
| Pull requests | 50 | 3      |
| Issues    | 25     | 1      |
| Reviews   | 2      | 1      |
| Stars     | 50     | 4      |
| Followers | 10     | 1      |

| Score (top %) | Rank |
| ------------- | ---- |
| up to 1       | S+   |
| up to 12.5    | S    |
| up to 25      | A++  |
| up to 37.5    | A+   |
| up to 50      | B+   |
| up to 62.5    | B    |
| above that    | C    |

The approach is inspired by [github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
but is an independent implementation, so ranks will not match it exactly.

## Development

```bash
git clone https://github.com/gitswagata1/gh-profile-stats.git
cd gh-profile-stats
pip install -e ".[dev]"
python -m pytest -q
```

Project layout:

```
gh-profile-stats/
├── src/gh_profile_stats/
│   ├── api.py        GitHub GraphQL access through the gh CLI
│   ├── stats.py      Percentiles, scoring, ranks and tips
│   └── cli.py        Argument parsing and output
├── tests/            Unit tests for scoring and the CLI
├── pyproject.toml    Packaging and the gh-profile-stats entry point
└── .github/          CI, issue and pull request templates
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned work, including a hosted badge service and a
GitHub Action.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md) first.

## License

Released under the [MIT License](LICENSE).

---

Built by **Swagata Banerjee** · [GitHub](https://github.com/gitswagata1)
