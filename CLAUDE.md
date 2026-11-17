# credit-risk-mlops

Start every session by reading `docs/ROADMAP.md` (approved design + progress tracker, milestones M0–M5)
and the current milestone plan in `docs/plans/` (now: `docs/plans/M0-foundation.md`).

- **Learning project:** Diego must understand everything, but Claude writes the code. Explain the concept
  before each task, then walk through the important code (what, why, what breaks otherwise); small steps.
- Code, docs, guide pages (`docs/guide/NN-<topic>.md`) and notebooks in English; chat with Diego in pt-BR.
- Commit messages in English (overrides the global pt-BR rule): `type: message`, no scope, no co-author lines.
- Public repo: never commit data (`data/`), credentials or `kaggle.json`; notebooks without outputs.
- Commands: `uv sync --all-groups` · `uv run pytest` · `uv run pre-commit run --all-files`.
- Schedule reminders live in the `today` MCP (`source_key` `roadmap:...`); update or delete items, never duplicate them.
  Dates are soft targets: follow the task order.
