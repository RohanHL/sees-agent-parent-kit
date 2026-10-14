# SEES Agent Parent Kit

Give your own AI assistant this repo and it becomes your San Elijo Elementary
school assistant — triaging your school email, keeping your calendar current,
and answering school questions with sources.

## For parents: one line

> **Set me up as a SEES parent: https://github.com/RohanHL/sees-agent-parent-kit**

Paste that into your AI assistant (Muse, ChatGPT, or Claude — anything that
can read this repo and connect to your Gmail and Google Calendar). It will:

1. Create a dedicated "SEES Assistant" chat for everything school-related
2. Connect to your Gmail (read-only — it only ever searches school senders,
   which it shows you first) and Google Calendar
3. Ask two questions (your kids + what deserves a calendar event), then
   immediately triage this week's school mail and propose calendar events
4. Send you a short digest every Sunday evening, plus timely heads-ups for
   urgent items

Your family details never leave your own chat. This repo holds only shared,
public school information.

## What's in this repo

- `SETUP.md` — the onboarding script your assistant follows
- `school-facts.md` — verified SEES facts (office numbers, enrollment,
  policies), with sources
- `school-dates.md` — approved school-wide dates for 2026–27
- `senders.json` — the school email allowlist (what your assistant watches)

## For the curious

This is the parent-side companion to [Sandy](https://github.com/RohanHL/sanelijohillselementary),
built on one idea: instead of one central service holding every family's
school life, each parent's own assistant does the work — with their own
connections, their own thresholds, and their own memory. The schoolwide facts
are published once, here; everything personal stays with the parent.

Maintained by Rohan Hemani. School facts are re-verified regularly; each file
carries a generated date.
