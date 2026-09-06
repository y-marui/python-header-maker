# Changelog

## [Unreleased]

### Added
- Codex as an assigned AI tool, with `AGENTS.md` as its entry point
- Markdown section-heading language check (`scripts/check-markdown-heading-language.sh`) to pre-commit
- `--version`/`-V` and shell completion (`--install-completion`/`--show-completion`) to the `header-maker` CLI

### Changed
- Migrated `header-maker` CLI from `argparse` to `typer` to satisfy dev-charter's CLI Usability requirements (#19)
- Updated dev-charter to 2026-08-08
- Bumped pinned versions in `.pre-commit-config.yaml` (gitleaks, pre-commit-hooks, shellcheck-py) and CI actions (`actions/checkout`, `astral-sh/setup-uv`)
- Reformatted `AI Tool Assignments` in `AI_CONTEXT.md` to reference the charter's standard role definitions instead of duplicating them

### Removed
- `[[tool.mypy.overrides]]` for `PIL.*`: Pillow 12.3.0 ships `py.typed` with sufficient coverage for the API surface this repo uses, and `make type` passes without it (#17)

### Fixed
- Non-English section headings in `AI_CONTEXT.md` and `docs/file-map.md`
