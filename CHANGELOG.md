# Changelog

Every improvement to this kit, with thanks to the parents who made it happen.

## 2026-10-14 — Launch

- Initial kit: setup script, school facts, school-wide dates, sender
  allowlist, triage spec.
- Distribution needs no GitHub account (plain web links).
- Feedback loop: parents contribute through their assistant, no account needed.

## 2026-10-18 — 4.0.0-draft.3 review proposal

- Introduce a shared behavioral core, separate school/host/household/version contracts and a deterministic complete single-file handoff.
- Keep school evidence independent of behavior versions; preserve existing school files, sender suggestions, topics and feedback.
- Replace legacy behavior entrypoints with redirects to the complete bundle; document maintainer migration and safe run-boundary upgrades.
- Add synthetic examples, standard-library packaging and 22 static tests. See [validation](VALIDATION.md) for version-specific synthetic results and untested live-host limits.
- Draft.3 clarifies optional manifest use and separates capability availability, operational health and consent. Draft.2 is a synthetic evaluation successor only.
- Review only: no main-branch deployment, live-pilot migration, host-support guarantee or new recurring jobs.
