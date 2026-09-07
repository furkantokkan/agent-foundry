# Contributing

Prefer one focused improvement per pull request: a clearer skill, a corrected reference, a reproducible workflow case, or a portability fix.

1. Explain the user-visible problem and the intended result.
2. Edit the canonical skill under `plugins/agent-foundry/skills/`. Keep commands as thin adapters.
3. Preserve upstream attribution. Add source and license information for new third-party material.
4. Never include credentials, private project details, account configuration, or conversation history.
5. Run `python scripts/validate.py`. If exported files intentionally changed, refresh their hashes with `python scripts/validate.py --refresh`, then review the diff and validate again.
6. State what you tested. Distinguish Markdown/manifest checks from a real workflow run.

For bug reports, include the skill name, host/CLI version, a minimal sanitized request, expected behavior, and observed behavior. Keep private projects and secrets out of public issues.

The export utility is for maintainers creating a fresh snapshot from their own reviewed local sources. It refuses to overwrite an existing skill export. Contributors normally edit the repository directly.
