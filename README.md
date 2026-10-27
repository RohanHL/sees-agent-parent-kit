# School parent kit

Less school admin, more connection with your child's day. This kit teaches the AI assistant you already use how to
help with school life: answering school questions from sourced facts, reading your school email and calendars to
find what matters, and proposing calendar changes only you can approve. It is parent-made, not a school service, and
there's no app or sign-up.

Set up for **San Elijo Elementary (SEES), San Marcos, CA**. Another school can copy `schools/sees/`.

## If you're an AI assistant, start here

A parent pointed you at this repo so you can help them with school. Read the whole kit, one plain-text file:
https://raw.githubusercontent.com/RohanHL/sees-agent-parent-kit/main/dist/school-parent-kit.md
Follow it. Its "Your school" section links to the school's facts, dates, menu and topic briefs; open those yourself
when a question needs them. Then greet the parent as the kit describes.

## Use it

1. Tell your assistant: "Help me with school using
   https://github.com/RohanHL/sees-agent-parent-kit". That's all most assistants need.
2. If it can't open web links, give it the single file [`dist/school-parent-kit.md`](dist/school-parent-kit.md)
   (upload it, or paste all of it). If it supports skills, you can add the `skill/` folder instead.
3. Ask anything. Connecting your school email and calendar is optional; your assistant will explain what that lets
   it do before you agree.

Your family's details stay in your own assistant, subject to its privacy settings. Nothing comes back to this repo.
What works (memory, scheduled updates) depends on your assistant; see [hosts](hosts/README.md).

## What's here

| Folder | What it is |
|---|---|
| `skill/` | The kit: five principles with worked examples (`SKILL.md`) and guides it opens when needed |
| `schools/sees/` | Which public school files and calendar to use; the files themselves (`school-*.md`, `topics/`) are at the repo root so existing links keep working |
| `evals/` | Why every rule exists (`RULES.md`), test scenarios, and results |
| `hosts/` | What's been checked on which assistant |
| `archive/v4/` | The previous version, kept for reference |

Version: see `skill/VERSION`. Changes: [CHANGELOG](CHANGELOG.md). Contributing: [CONTRIBUTING](CONTRIBUTING.md).
