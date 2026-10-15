# Weekly Triage Job Spec

This is the spec for the scheduled job that runs the parent's weekly
school-mail triage. It is written to be implementable as-is as a scheduled
job's instructions, in any capable AI assistant (Muse, ChatGPT, Claude).

Read `PRINCIPLES.md` first — the five principles outrank everything here:
https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/PRINCIPLES.md

---

## 1. Job identity

- **What:** read this week's school mail, extract what's new, chase every
  reference, propose calendar events, and deliver the weekly digest.
- **When:** Sunday ~8pm PT — the Principal's newsletter lands every Sunday
  early evening, so 8pm gives comfortable margin; the teacher newsletter
  arrives Sundays at highly variable times (occasionally Monday), so the
  registry's missing-issue check sweeps stragglers on Monday.
- **Scope:** exactly one parent, their own Gmail + Google Calendar. It reads
  only what the sender allowlist permits. It never touches another person's
  mail, and there is no shared store.

## 2. Inputs (read at the start of every run)

0. `PRINCIPLES.md` — principles outrank procedure.
1. The sender allowlist: publisher preset (school domains) + the parent's
   personal additions. The triage query is built from this file; unlisted
   mail is never searched or read.
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
  — want me to check?" (Principle 1: never claim a quiet week when coverage
  lags; name unreadable sources instead of skipping them.)

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
(Principle 1.)

### 3.5 Match against the store: new / same / CHANGE
- Same scope + date + normalized title → no-op (add the message to sources).
- Same event, different date/time → CHANGE proposal. A *stated* change
  ("moved from Oct 7 to Nov 4") is applied; anything ambiguous is surfaced
  with "Replaces:/Cancels:" and the sources' history.
- New → new proposal. Retire = store-only (old item superseded, never deleted
  outright). Cancellation within 7 days → "CANCELLED:" in the title for a day,
  not silent deletion. (Principle 5.)
- Never treat "this week's newsletter omits the old date" as proof of a move.

### 3.6 Calendar proposals
Propose an event only if it is **schedule-changing** (no school, early
dismissal, minimum day, field trip, dress-up day), **parent-attendance**
("would a parent go to the school to see their child do this?"), or a
**learned exception** the parent explicitly wants. Everything else stays
informational.
- **Sign-up and registration deadlines are propose-worthy by default.**
  They hide in the sprawl and parents discover them too late.
- **Semantic dedup first**: same date range + same child + same event — match
  by judgment, not string ladders. Check against the kid/family calendars
  (work calendars are for conflict detection only) **including events marked
  "Added by…" from another household assistant**. Unsure → propose and let
  the parent decide. (Principle 1: when sources disagree, the item stays a
  proposal — the calendar waits.)
- Title: `"Event Name (Child)"` — always tag which kid.
- Kid's own events → **transparent/free**. Parent-attendance → **invite both
  parents** (shows busy on their calendars). Routing fallback: if the ideal
  calendar isn't writable, write to the kid's calendar and invite both parents
  instead of stopping.
- Description: source note ("from the Oct 11 Principal's Newsletter") +
  **"Added by [your assistant name]"** so the parent can distinguish
  agent-created events.
- Multi-day: collapse consecutive same-name days into one ranged event.
- Tentative blocks are fine — labeled tentative, reconciled when the official
  schedule posts; update/replace, never duplicate.

### 3.7 Gap diff (the killer section)
Diff the subscribed school calendar against the kid's calendar for the coming
weeks. Every school item missing from the kid's calendar becomes a digest line
and, where it passes the thresholds in 3.6, a calendar proposal. Gate by
calendar richness: a sparse calendar gets save-level gaps only, not a full
dump. (Principle 3.)

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

### 3.8 Compose the digest
- **To prep** (what do I DO, by day) · **Heads up on the schedule**
  (deviations only, never normal hours) · **What they're up to** (warm
  narrative + ASK-don't-ASSERT conversation starters) · **Worth flagging for
  later** (undated / looking-ahead) · plus the **gap-diff section**.
- Lead with the save: the single highest-stakes date in the next ~3 weeks
  they'd most likely miss. That's the moment they'll tell someone about.
- Composition rules: only send if something differs from normal; MAX 3 events
  per section-ish (keep it skimmable); multi-day items announced at start and
  end, never every week between; recess weeks say when school resumes.
  (Principles 1, 2, 3.)
- Show the filter, occasionally: if an item was suppressed by the
  interruption contract but sits close to the line, add one line naming it
  and why it waited. The parent can only correct the filter if they can see
  it. (Principle 3.)

### 3.9 Deliver + persist
- Deliver the digest in this chat. Calendar proposals go in as
  "tap to confirm" items. (Principle 5: propose → confirm → create, always;
  nothing is written silently.)
- Write back: new/changed items to the store (with verbatim source sentences,
  statuses, calendar event IDs on confirmation), registry last-seen bumps,
  expiry of stale items (7-day expiry on pending proposals — re-surfacing seen
  items trains the parent to ignore you). Before executing an approved
  calendar write, re-check the calendar for a matching event — the parent may
  have added it meanwhile; if present, skip the write and say so. An expired
  proposal is reported once as expired, never silently dropped and never
  re-surfaced as if new. (Principle 3.)
- **Run integrity: failure must look different from quiet.** Every run
  records its outcome (ok/failed + one line) to the run log; every run opens
  by reading the last entry. If the previous expected run didn't record ok,
  open with a plain-language note ("last Sunday's digest didn't finish —
  here's what I recovered"). (Principle 5.)

### 3.10 Notification discipline (the interruption contract)

The Sunday digest is the product; every other ping is an exception. Between
digests, the agent sends only items in the parent's chosen breakthrough
categories (set during onboarding, §8 of SETUP.md) — typically pickup/logistics
changes, cancellations, and urgent safety notices. Everything else batches
into Sunday, no matter how interesting it looks. (Principle 3: never invent a
category; batch, don't drip; a quiet week is a feature. The parent can change
the contract anytime — the change takes effect immediately.)

## 4. The closed loop

A question the store can't answer is a triage miss, and it feeds back into the
extraction profiles: "what time is the winter festival?" → add event-time
extraction to the PTO newsletter's format profile. Time-sensitive facts decay —
never store them as durable memory. Corrections are recorded as the specific
fact, not a meta-rule.

**Shared-data corrections: one-tap publisher feedback.** When the parent
corrects something that lives in the shared publisher package (a wrong school
date, a stale fact, a menu error) — as opposed to their private data — offer
once: "Want me to pass this fix along so other parents get it too?" On their
yes, pre-fill the feedback form with the correction (what was wrong, what's
right, the source), strip every family-specific detail, and submit it for
them. (Principle 3: one tap is the whole cost; never ask about the same item
twice. Never name the maintainer; the beneficiary is other parents.)

## 5. Companion jobs (not spec'd here)

- **Evening check** (daily, before the family's decision point — 5pm):
  tomorrow's deviations only — dress-up days, items to bring, early
  dismissals. A late heads-up is useless; reminders must precede the decision
  point, not the event.
- **Publisher refresh** (publisher's side): re-fetch the shared school facts +
  sender preset weekly; drift alerts.

## 6. What this spec deliberately omits

No cross-household privacy machinery, no "never open links" rule (inverted —
link-following is standing behavior), no public-calendar title hygiene (the
parent's own calendar holds full details), no text-line/SMS machinery, no
git-backed personal store, no brittle string-match dedup, no 500-line
deterministic pipelines where model judgment does the job.
