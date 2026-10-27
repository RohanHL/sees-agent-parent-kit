# School parent kit

Less school admin, more connection with your child's day. This kit teaches the AI assistant you already use how to
help with school life: answering school questions from sourced facts, reading your school email and calendars to
find what matters, and proposing calendar changes only you can approve. It is parent-made, not a school service, and
there's no app or sign-up.

Set up for **San Elijo Elementary (SEES), San Marcos, CA**. Another school can copy `schools/sees/`.

## Use it

1. **If your assistant supports skills,** add the `skill/` folder.
   **Otherwise,** give it the single file [`dist/school-parent-kit.md`](dist/school-parent-kit.md): upload it, or
   paste all of it.
2. Say: "Help me with school life using these instructions."
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
