# Changelog

## [Unreleased]

### Added
- Codex as an assigned AI tool, with `AGENTS.md` as its entry point
- Markdown section-heading language check (`scripts/check-markdown-heading-language.sh`) to pre-commit

### Changed
- Updated dev-charter to 2026-08-08
- Bumped pinned versions in `.pre-commit-config.yaml` (gitleaks, pre-commit-hooks, shellcheck-py) and CI actions (`actions/checkout`, `astral-sh/setup-uv`)
- Reformatted `AI Tool Assignments` in `AI_CONTEXT.md` to reference the charter's standard role definitions instead of duplicating them

### Fixed
- Non-English section headings in `AI_CONTEXT.md` and `docs/file-map.md`

<!-- ci gate pilot test: docs-only commit -->
