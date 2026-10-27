# Validation report · v4 review draft

Static checks executed 18 October 2026. No live host, parent, connector, school source, calendar write, scheduled job or delivery was tested.

## Commands and results

Commands run from the kit directory:

    python3 tools/build_bundle.py
    python3 tools/build_bundle.py --check
    python3 -m unittest discover -s tests -v

Current release: 4.0.0-draft.3. Bundle SHA-256: 3922086452d01c5ace38dabae718df49caeca1839fcf8716504c5cccdd9afb02. Results: build and freshness check PASS; 22 unittest cases PASS after the two review wording changes. The two added checks guard the optional-manifest and capability/health/consent wording; they do not test model behavior.

## Separately staged behavior tests

The independent evaluator reported all three canonical synthetic fixtures passing against frozen 4.0.0-draft.1, bundle SHA-256 4bbdbafca703298fe9f501f6ce4726fd49770cbe59fcf40b6930bb175e2ef4ef. Those fixtures covered partial connection/resume, a different school with limited host and fresh-session context loss, and behavior-version continuity with independently refreshed school evidence and staged delivery states. The evaluator used supplied synthetic connection/scheduling results, not real host operations. Optional incomplete-upgrade and uncertain-job-creation branches were not executed.

Version 4.0.0-draft.2 was reserved for the evaluator's synthetic successor only (hash b557e3f7e620398867c735564e5e6f2fd7838f4b9a986ca4e1b96f65c4740ed4). It is not this implementation release. The real wording revision is 4.0.0-draft.3; historical fixture artifacts remain unchanged.

Draft.3 has only the two documented behavioral wording changes plus version identifiers. Targeted behavioral regression on draft.3 passed in a fresh synthetic review using only the complete bundle, without an adjacent manifest. The subject retained completed permission and the calendar decline, separated a supplied temporary email timeout from previously verified capability and continuing consent, and preserved session-only/on-demand limits. All family context and tool outcomes were evaluator-supplied simulations; no real host or external action was exercised. The full three-case suite was not rerun on draft.3. The draft.1 synthetic passes are not represented as executions of draft.3. Neither release has live-host/mobile/durable-storage/scheduler/delivery proof.

## What these checks establish

- Byte-for-byte deterministic generation across copies of the source tree.
- Complete, ordered inclusion of all seven maintained modules exactly once, with per-source and bundle SHA-256 hashes and an end marker.
- Missing, empty, duplicate, unlisted, reordered and dependent-link modules fail validation.
- Generated artifacts match maintained sources; changing a source changes the bundle identity.
- All relative Markdown document links point to files included in this draft.
- Synthetic examples use a coherent behavior/schema version, valid capability states, child/occurrence/obligation references and evidenced completion.
- Example host capabilities cannot claim verification; example checkpoint cannot grant read scope or recurring access.
- The automatic SEES evidence profile is bundled; a remote behavioral instruction link in that profile is rejected.
- Mutable behavior URLs, internal workspace paths and the obsolete feedback endpoint are absent from the generated bundle.

There is no automated private-name scanner. The proposed changes were manually reviewed for family-data privacy; test fixtures use fictional data. Source/link checks are conservative static checks, not a complete Markdown parser or security verifier. Hashes prove consistency of supplied bytes, not publisher authenticity. Example validation is not a universal host-state validator. The script does not execute migrations or enforce semantic behavior.

## Acceptance scenario inventory

1. Connected parent gets a useful personal result before setup questions.
2. No connectors/no school evidence: honest useful response, no invented school fact.
3. Email-only parent declines calendar and returns: retain completed permission, recheck already-authorized trip details without repeated read permission.
4. Wrong account: resolve ambiguity without whole-inbox expansion or false “nothing outstanding.”
5. Same-class twins: separate permissions, shared occurrence without duplicate calendar events.
6. Ordinary schedule plus new classroom learning: useful agreed brief; no unapproved between-brief ping.
7. Missing late newsletter: observed arrival window governs gap, no permission theater.
8. No persistent state or scheduler: session-only/on-demand finish, no remembered or monitoring claims.
9. Complete bundle unavailable: bounded help, no claimed full-kit load or scheduled activation.
10. New behavior version: completion/corrections survive, old uncertain writes are not replayed, permissions not expanded.
11. First scheduled send accepted but not delivered: do not claim first_delivery_verified.
12. Previously delivered job stops starting: meaningful failure disclosure when observable, no self-log watchdog guarantee.
13. Second caregiver or existing writer: no extra setup until action matters, no silent private sharing or duplicate writer.

This inventory is not a claim that all scenarios have been executed. Only the separately staged draft.1 fixtures described above have recorded synthetic passes; draft.3 also has the narrower single-file/temporary-failure targeted synthetic pass described above, not a rerun of the full three-case suite. Static tests cannot establish model adherence, actual host setup, mobile usability, memory continuity, scheduler reliability or a parent's experience over weeks.

