# Contributing

## A wrong school fact
Send it through the contact form in the [README](README.md#who-made-this) (your assistant can pre-fill it), or open
an issue or pull request if you use GitHub. Say what's wrong, what's right, and the source (a newsletter, the school
or district site). Leave out anything about your family. Corrections need a source.

## A behavior lesson
When an assistant using this kit gets something wrong:
1. Write the situation as a scenario in `evals/scenarios/` (made-up names, bracketed or simulated facts) with its
   must / must-not checks in `evals/checks/`.
2. Add the lesson to `evals/RULES.md` under the principle it violates, with why.
3. Change `skill/` only as much as the scenario needs: usually a worked example, rarely a sentence in a principle.
   A sixth principle only if the lesson fits none of the five.
4. Rerun the scenarios (old and new kit) and record the result in `evals/RESULTS.md`.

## Building and checking

    python3 tools/build_skill.py          # rebuild dist/school-parent-kit.md from skill/
    python3 tools/build_skill.py --check  # fail if dist/ is stale
    python3 -m unittest discover -s tests

Bump `skill/VERSION` and the version line at the end of `SKILL.md` together for any behavior change, and add a
CHANGELOG entry. School files refresh independently of the version.

## Never
Family names, emails, phone numbers, addresses or anything about a real child, in any file or commit message. Git
history is public and permanent.

## Another school
Copy `schools/sees/` to `schools/<your-school>/`, point it at your school's public sources, and keep `skill/` as is.
