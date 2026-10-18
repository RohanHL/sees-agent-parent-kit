# Private minimal household/checkpoint contract

Use the host's existing private state, if available; no database or new service is required. Keep only useful evidence and decisions, not a complete family dossier. Same-session context is not durable storage. If later-execution recovery is unverified, keep this session-scoped and disclose that before promising memory or scheduling.

Maintain the following conceptual fields only as known or needed (empty/unknown is valid):
- behavior_version and bundle identity; schema_version; session-only or verified-private persistence;
- intended/verified accounts, approved sender/search scope and permission evidence; calendar windows and incomplete reads; capability observations;
- child/class associations with source, time, uncertainty and corrections; no compulsory allergies, phone number, age or caregiver inventory;
- relevant occurrences, separate child-specific obligations/completions, superseded records and evidence;
- useful findings already delivered, declined offers, pending proposals, exact approvals and verified execution outcomes;
- optional calendar conventions and designated writer, learned only when a write matters;
- checkpoint: current question/unresolved useful step, source gaps and last actual check, not a completed-setup boolean;
- recurring approval (scope, content, recipient, cadence/timezone and interruption categories), job identity/next run, readiness, health, run and delivery evidence only if applicable.

The illustrative JSON example is a synthetic session-only snapshot, not an installation schema, authorization or real family record. Implementations may use natural-language notes; do not force parents to fill JSON or migrate a database.

Keep corrections and completion history while relevant; record why an association changed instead of silently reusing an old teacher/year. At school-year transitions verify current associations rather than carrying last year's profile forward. Do not automatically reset based on an assumed global August start date.

Permissions are explicit evidence, not inferred from a source list, family relationship or saved suggestion. Read scope may be reused while valid; unknown approval is not approval. A school/host change does not expand it. Shared household decisions stay only in the destinations already authorized; private chat notes are not automatically shared with another caregiver. Resolve conflicting instructions and ownership at the consequential action, not through an upfront household interview.

If durable state is missing/corrupt/incompatible, don't recreate it from public data or pretend continuity. Retain available source-backed session knowledge, explain the relevant limit, recover minimum needed authorized history and request only the unresolved decision. Never re-execute a prior uncertain action as recovery.
