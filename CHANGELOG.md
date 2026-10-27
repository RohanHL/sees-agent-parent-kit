# Changelog

## 2026-10-27 — 5.0.0-draft.1

- Rebuilt around five principles (fit their system; infer, don't interrogate; every claim has a source and every gap
  a name; reading is free, changing is theirs; earn every interruption), each with worked examples from testing.
- Skill folder format: a short core always loaded, six guides opened only when needed; `dist/school-parent-kit.md`
  is the same content as one file. 3,698 words, down from 4,630.
- Every rule from v1-v4 is recorded with its reason and a test scenario in `evals/RULES.md`. Restored three v3
  behaviors that v4 dropped: lead with the one date most likely missed, a "since you asked" line, the school calendar.
- Scenario results against v4: 43/43 vs 36/43 (`evals/RESULTS.md`).
- School data described in `schools/sees/school.json`; no route back to a maintainer (corrections are drafted by the
  parent's own assistant). v4 kept in `archive/v4/`.
- History rewritten to remove family details from earlier examples.

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
