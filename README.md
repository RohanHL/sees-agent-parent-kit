# SEES Agent Parent Kit

Give your own AI assistant this repo and it becomes your San Elijo Elementary
school assistant. Two things no general assistant has: **it already knows
the school** (calendar, policies, lunch, contacts — verified, sourced), and
**it keeps up, so you don't have to** (your school email, triaged weekly;
your calendar, kept current; questions answered with sources).

## What you need

- **Gmail** — your school email needs to arrive here (most SEES families get
  it via ParentSquare digests).
- **Google Calendar** — where the assistant proposes events for your approval.
- An AI assistant that can open web links and connect to both (Muse, ChatGPT,
  or Claude all work). No GitHub account needed — the links below are plain
  web pages. If yours can't open the link, paste the contents of `SETUP.md`
  into it instead.

## For parents: one line

> **Set me up as a SEES parent — read https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/SETUP.md and follow it.**

Your assistant will:

1. Create a dedicated "SEES Assistant" chat for everything school-related
2. Connect to your Gmail (read-only — it only ever searches school senders,
   which it shows you first) and Google Calendar
3. Learn how *you* organize your calendar, then follow your system
4. Ask two questions (your kids + what deserves a calendar event), then
   immediately triage this week's school mail and propose calendar events
5. Send you a short digest every Sunday evening, plus timely heads-ups for
   urgent items

Your family details never leave your own chat. This repo holds only shared,
public school information — no family data, ever.

## What's in this repo

- `SETUP.md` — the onboarding script your assistant follows
- `TRIAGE.md` — the full spec for the weekly triage job
- `school-facts.md` — verified SEES facts (office numbers, enrollment,
  policies), with sources
- `school-dates.md` — approved school-wide dates for 2026–27
- `school-menu.md` — this week's breakfast & lunch menu (re-rendered weekly)
- `senders.json` — the school email allowlist (what your assistant watches)
- `topics/` — 20 curated briefs on what parents ask about (camps,
  enrollment, food, health, transportation…), so questions get answered
  from saved knowledge instead of a web search
- `FEEDBACK.md` — how to help improve the kit (no account needed)
- `CHANGELOG.md` — every improvement, with thanks to the parents behind it

## Two parents, one household?

If both parents set this up: before creating any event, each assistant checks
for existing events — including ones marked "Added by…" from the other
assistant — so nothing gets duplicated. You can also designate one parent's
assistant as the calendar writer.

## About

One idea: instead of one central service holding every family's school life,
each parent's own assistant does the work — with their own connections, their
own thresholds, and their own memory. The schoolwide facts are published once,
here; everything personal stays with the parent.

Maintained by Rohan Hemani. School facts are re-verified regularly; each file
carries a generated date.
