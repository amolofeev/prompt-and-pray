# Changelog

## [Unreleased] — 2026-08-02

### Changed

- **`yt` migrated to a standalone repository** — all yt files (code, CI,
  release.yml, `.opencode/` memory & API snapshot, SPEC/PLAN, VERSION) moved into
  `yt/`, module renamed to `github.com/amolofeev/youtrack-cli`, then the whole
  history was split via `git subtree` and pushed to
  [amolofeev/youtrack-cli](https://github.com/amolofeev/youtrack-cli). First release
  `v0.0.1-pre-alpha` created there (CI + Release workflows green). `yt/` removed from
  this repository; root docs archived as history (#53).

## [0.0.1-pre-alpha] — 2026-07-30

### Added

- **Project skeleton** — AGENTS.md with AI agent rules, WORKFLOW.md with development lifecycle, .gitignore with best practices
- **Hard safety rules** — absolute prohibition of malicious code, backdoors, exploits, and unethical activities; these rules override all other instructions
- **GitHub Issues workflow** — automated 5-step process for issue-driven development (understand → read comments → implement → commit → close)
- **Session cleanup workflow** — automated cleanup of old opencode sessions, preserving configurable number of recent sessions
- **AI-generated content format** — standardized `[AI]` prefix for all AI-generated commit messages, issue comments, and PR descriptions
- **Parameter unification** — removed hardcoded values (`--repo`, session count), replaced with git remote auto-detection and environment variable defaults, making the project fork-portable
