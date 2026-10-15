# Weekly Triage Job Spec

Drafted 2026-10-14. Assembled from the repo harvest (`repo-harvest.md`):
Kyle's calendar rules spec (§2.1–2.8), Sandy's extraction schema + code checks
(mail-extract SKILL.md), the digest composition rules (digest.py + Kyle's
4-section format), and the Oct 14 dogfood additions (gap diff, "Added by [your assistant name]",
routing fallback, link-following as standing behavior).

This is the spec for the scheduled job that runs the parent's weekly
school-mail triage. It is written to be implementable as-is as a scheduled
job's instructions, in any capable AI assistant (Muse, ChatGPT, Claude).

---

## 1. Job identity

- **What:** read this week's school mail, extract what's new, chase every
  reference, propose calendar events, and deliver the weekly digest.
- **When:** Sunday ~8pm PT — verified against Rohan's mail (Oct 14, 2026): the
  Principal's Newsletter lands every Sunday ~6:15–6:20pm PT like clockwork, so
  8pm gives comfortable margin; the teacher newsletter (Stremel Scoop) also
  arrives Sundays but at highly variable times (7am–6pm, occasionally Monday),
  so the registry's missing-issue check sweeps stragglers on Monday. Anchored
  to source-publish + the family's planning point (Kyle's timing logic).
- **Scope:** exactly one parent, their own Gmail + Google Calendar. It reads
  only what `mail-scope.md` (the allowlist) permits. It never touches another
  person's mail, and there is no shared store.

## 2. Inputs (read at the start of every run)

1. `mail-scope.md` — the sender allowlist: publisher preset (school domains)
   + the parent's personal additions. The triage query is built from this file;
   unlisted mail is never searched or read.
2. The **newsletter registry** — expected streams, cadence, format, last-seen:
   Principal's Newsletter (weekly, Sunday, ParentSquare digest), teacher
   newsletter(s) (weekly, Smore), PTO newsletter (linked from the Principal's
   digest, Smore), district comms (as-needed).
3. The **kid profile** — name, grade, teacher, room (+ allergies/diet if given).
4. **Thresholds** — the surface/skip lists, confirmed conversationally.
   Defaults: surface = schedule changes, parent-attendance, deadlines, dress-up
   days, items to bring; skip = PTO meetings, donation appeals, volunteer
   paperwork (unless the parent said otherwise).
5. The parent's **knowledge store** — previously extracted items with sources,
   statuses, and calendar event IDs. (Per-parent, deletable — never git.)

## 3. Steps

### 3.1 Coverage check
- For each registry stream: did the expected issue arrive? If a weekly is
  missing, that is itself a digest line: "No Principal's newsletter this week
  — want me to check?" Never claim a week is event-free when coverage lags.

### 3.2 Fetch
- One query from the allowlist, `newer_than:7d`. Read-only. Fingerprint-dedup
  against the store (ParentSquare post id, else poster + day + time + digest
  slot); re-seen posts are dropped silently.

### 3.3 Extract (per new message)
For each message, list dated items as structured lines — the mail-extract schema:
- `what`, `date` / `end_date`, `time` (only if stated), `scope` (which kid /
  class), `type` (no-school | minimum-day | school-event | deadline | outside),
  `change` (moved | cancelled | postponed), `was_date`, and `sentence` — the
  exact words from the text, copied character for character.
- **Follow every link out**: the PTO newsletter (Smore), flyers, signup forms;
  read attached PDFs. Tracker hygiene: never click tracking links that record
  against the parent; no OCR on image-only flyers (a misread date could pass
  the checks — flag for human eyes instead).
- Recurring elements are checklist items, not discoveries: "Principal's digest
  → follow the PTO newsletter link" happens every week, unprompted.

### 3.4 Code checks (every extracted item, no exceptions)
- The source sentence appears word-for-word in the email.
- The date appears in that sentence.
- **Weekday must match the date** — mismatch → surface as a conflict, never
  silently resolve.
- Date within the school year and not in the past.
- **Time stored only if written in the date's sentence.** A time not proven is
  left off with a note — never stored unproven, never invented.
- Priority: time stated in source → known recurring default (only when actually
  known) → all-day. Timezone America/Los_Angeles. (Google quirk: all-day end
  date is exclusive.)

### 3.5 Match against the store: new / same / CHANGE
- Same scope + date + normalized title → no-op (add the message to sources).
- Same event, different date/time → CHANGE proposal. A *stated* change
  ("moved from Oct 7 to Nov 4") is applied; anything ambiguous is surfaced
  with "Replaces:/Cancels:" and the sources' history.
- New → new proposal. Retire = store-only (old item superseded, never deleted
  outright). Cancellation within 7 days → "CANCELLED:" in the title for a day,
  not silent deletion.
- Never treat "this week's newsletter omits the old date" as proof of a move.

### 3.6 Calendar proposals (Kyle's rules, verbatim)
Propose an event only if it is **schedule-changing** (no school, early
dismissal, minimum day, field trip, dress-up day), **parent-attendance**
("would a parent go to the school to see their child do this?"), or a
**learned exception** the parent explicitly wants. Everything else stays
informational.
- **Semantic dedup first**: same date range + same child + same event — match
  by judgment, not string ladders. Check against the kid/family calendars
  (work calendars are for conflict detection only) **including events marked
  "Added by…" from another household assistant**. Unsure → propose and let
  the parent decide. Contradictory sources → latest wins, conflict surfaced.
- Title: `"Event Name (Child)"` — always tag which kid.
- Kid's own events → **transparent/free**. Parent-attendance → **invite both
  parents** (shows busy on their calendars). Routing fallback: if the ideal
  calendar isn't writable, write to the kid's calendar and invite both parents
  instead of stopping.
- Description: source note ("from the Oct 11 Principal's Newsletter") +
  **"Added by [your assistant name]"** so the parent can distinguish agent-created events.
- Multi-day: collapse consecutive same-name days into one ranged event.
- Tentative blocks are fine — labeled tentative, reconciled when the official
  schedule posts; update/replace, never duplicate.

### 3.7 Gap diff (the killer section)
Diff the subscribed school calendar against the kid's calendar for the coming
weeks. Every school item missing from the kid's calendar becomes a digest line
and, where it passes the thresholds in 3.6, a calendar proposal. (Dogfood,
Oct 14: closures make it; spirit days, deadlines, and fundraisers are what
fall through.)

### 3.7b Activities: the second stream (and the intersection)

Activities (soccer, gymnastics, music) are a second schedule-stream for the
same kid, triaged with the same pipeline: same extraction schema, same
calendar rules, same propose → confirm → create. Their senders live in the
parent's personal mail scope (found during onboarding).

The unique value isn't watching activities — it's the **intersection**.
The school doesn't know about soccer; the league doesn't know about
school. This agent is the only thing that sees both. When a school schedule
change collides with an activity (minimum-day 12:30 pickup + gymnastics at
1pm across town; field trip day + game day), surface the conflict in the
digest — don't resolve it, don't stay silent. Activity items belong in
"Heads up on the schedule"; the conflicts they create with school items get
their own callout.

### 3.8 Compose the digest (Kyle's 4-section format)
- **To prep** (what do I DO, by day) · **Heads up on the schedule**
  (deviations only, never normal hours) · **What they're up to** (warm
  narrative + ASK-don't-ASSERT conversation starters) · **Worth flagging for
  later** (undated / looking-ahead) · plus the **gap-diff section**.
- Composition rules: `worth_sending` — only send if something differs from
  normal; MAX 3 events per section-ish (keep it skimmable); multi-day items
  announced at start and end, never every week between; recess weeks say when
  school resumes; **never claim a week is event-free** (coverage caveat).
- Every date/number traceable to a source line, cited per item. "I don't know
  yet" beats a guess — a wrong date kills trust forever. No bookkeeping terms
  leak into parent-facing text.

### 3.9 Deliver + persist
- Deliver the digest in the parent's chat. Calendar proposals go in as
  "tap to confirm" items — **propose → confirm → create, always**; nothing is
  written silently.
- Write back: new/changed items to the store (with verbatim source sentences,
  statuses, calendar event IDs on confirmation), registry last-seen bumps,
  expiry of stale items (7-day expiry on pending proposals — re-surfacing seen
  items trains the parent to ignore you).

## 4. The closed loop

A question the store can't answer is a triage miss, and it feeds back into the
extraction profiles: "what time is the winter festival?" → add event-time
extraction to the PTO newsletter's format profile. Time-sensitive facts decay —
never store them as durable memory. Corrections are recorded as the specific
fact, not a meta-rule.

## 5. Companion jobs (not spec'd here)

- **Night-before reminder** (daily, before the family's decision point — 5pm
  for the Hemanis): tomorrow's deviations only — dress-up days, items to
  bring, early dismissals. An 8pm heads-up is useless; reminders must precede
  the decision point, not the event.
- **Publisher refresh** (Rohan's side): re-fetch the shared school facts +
  sender preset weekly; drift alerts.

## 6. What this spec deliberately omits

Per the harvest's DO-NOT-COPY list: no cross-household privacy machinery, no
"never open links" rule (inverted — link-following is standing behavior), no
public-calendar title hygiene (the parent's own calendar holds full details),
no text-line/SMS machinery, no git-backed personal store, no brittle
string-match dedup, no 500-line deterministic pipelines where model judgment
does the job.
