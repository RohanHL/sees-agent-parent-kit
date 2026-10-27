# Maintaining the review draft

This is a prompt-native kit with one generated handoff. No app, backend, runtime package dependencies, accounts or jobs are installed. Python 3 standard library is used only by maintainers to package/test it. Parents use the generated text file, not Python.

## Maintained sources

- core/PRINCIPLES.md: common judgment and safeguards.
- core/SETUP.md: next-useful-step decision table.
- core/TRIAGE.md: evidence reconciliation, calendar proposals and family briefs.
- contracts/SCHOOL-PACK.md: public evidence/freshness boundary.
- contracts/HOST.md: optional observed capabilities and readiness.
- contracts/HOUSEHOLD.md: minimum private continuity state.
- contracts/VERSIONING.md: complete loading and safe upgrades.

manifest.json fixes the draft behavior version and complete ordered module set. Do not edit dist by hand. Behavior modules must be self-contained, without links to external behavioral dependencies. The school contract includes the default SEES public evidence entrypoints; the builder allows only those exact evidence URLs. The facts themselves remain independently maintained outside the bundle, never inline private school data. The illustrative examples are not loaded into the bundle and grant no capabilities or access.

## Build and check

From this directory:

    python3 tools/build_bundle.py
    python3 tools/build_bundle.py --check
    python3 -m unittest discover -s tests -v

The builder emits dist/PARENT-KIT.md and dist/bundle-manifest.json deterministically, without timestamps or network access. It refuses missing, duplicate, unlisted or reordered modules and dependent behavioral links. --check detects changed/stale output. Tests also verify fixture references, version coherence, synthetic-only permissions, hashes and local document links. These are static guarantees, not proof that an AI follows instructions.

When behavioral sources change, bump the manifest behavior_version and the illustrative checkpoint's matching version, review the changes and rebuild. A source change without a version bump still changes the hash; the tool cannot determine whether a maintainer reused a previously released version. Enforce release immutability in human release review. This branch is published for review only. Merging or deploying it requires a separate release decision.

No formal JSON Schema or runtime state engine is required. Example validation is deliberately narrow and documented in the script. Actual hosts may use ordinary private notes with the same conceptual fields.

## Required evidence before live claims

1. Independently review the complete bundle, migration map and synthetic scenarios.
2. Select one actual host and verify current setup instructions, account identity/read scope, private state recovery and approval verification. Do not claim other hosts from prompt portability.
3. With explicit authorization, test necessary scheduling and actual first scheduled delivery in the intended destination. Test failure recovery and interruption boundaries. Avoid artificial production calendar edits merely to pass a test.
4. Observe an unfamiliar parent's unassisted mobile start and interrupted resume, with consent. Measure confusion and time to useful help rather than promise one minute.
5. Observe real weeks of completion/correction retention, useful classroom connection and decreasing repeated administration. A second host needs its own operational proof.

See [migration mapping](MIGRATION.md), [validation report](VALIDATION.md). Publishing this review branch changes no existing pilot and grants no account access, communication, schedules or calendar actions.
