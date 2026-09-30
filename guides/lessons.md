# Lessons: what to keep and where it goes

Shared by `debrief`, the background stager, and `review`. "The mentor" is a role name: in everything you write, use the name from `APPRENTICE.md`'s `mentor:` field.

## Extract candidate lessons, then cut most of them

The wiki's value depends on what's left out. Every lesson is loaded or searched in future sessions, so a lesson that won't change future behavior costs attention and dilutes the ones that matter. A good employee's notebook has "the build server rate-limits us, so batch requests", not "on Tuesday we decided the dropdown shows counts". **Zero lessons is a normal and good outcome for a session.** Most sessions yield zero to two.

Look for what a thoughtful new employee would write down:

- **Corrections**: the mentor said no, redid your work, or pushed back. What general rule lies behind the specific fix?
- **Confirmed approaches**: explicit approval ("yes, exactly", "keep doing that"). These are quiet and easy to miss.
- **Preferences and style**: how they like code, prose, plans, and communication, and when they want you to ask versus act.
- **Domain knowledge**: facts about their field, tools, organization, or collaborators that came up and aren't written anywhere.
- **Project context**: lasting goals, constraints, and gotchas (environment quirks, things that look wrong but are intentional), not the design decisions made while doing the task.
- **Procedures**: multi-step workflows they walked you through. Record the steps.
- **Your own mistakes**: what went wrong on your side and how to avoid it next time.

### The keep test

A candidate is kept only if **all** of these hold:

1. **It changes future behavior.** Picture a *different* task a month from now. Would knowing this make you act differently there? If it only describes what was decided or built in this task, drop it.
2. **It isn't recorded somewhere better.** If it's implemented in the code, written in a commit, a config, or the repo's docs, then the code is the record. Drop it.
3. **It's a rule or constraint, not a choice.** "Show counts in the filter dropdowns" is a choice about one feature. "The mentor likes UIs to show counts wherever there's filtering" would be a preference, but only if they *said* it generally or it has come up across tasks. Don't promote one choice into a general preference yourself.
4. **It has a reason that outlasts the task.** Keepers usually come with a durable *why*: an external limit (rate limits, quotas, licensing), a repeated pain point, a stated principle. A why that only makes sense inside this task ("because this scan only needs public repos") means drop it.
5. **It's stated at the level the evidence supports, and that level is general.** Before keeping a lesson, strip the task out of it: remove this project's names, files, features, libraries, and values from the rule. If what remains is still true and useful, that's the lesson (the specific case can survive as a short *e.g.*). If nothing useful remains, it was a task detail, so drop it. For example, "use a `set` for `PUBLIC_ONLY_ORGS`" is a task detail; "give parallel config values the same type" is the lesson. Conversely, don't inflate: a lesson can't be broader than what was actually said or shown.

Typically **dropped**, even though they felt important in the moment:
- scoping and design decisions for the feature being built ("scan only public repos", "put the button on the left", "use a dict here"),
- task status and progress ("the migration is half done"); that's for a handoff note, not a lesson,
- a preference the mentor showed once, for one artifact, with no general statement. If it matters, it will come up again, and `reflect deep` finds things said more than once,
- facts you can re-derive in a minute (file locations, function names, command flags).

Typically **kept**:
- external constraints that bite repeatedly ("GitHub API rate limits are real: minimize calls, batch, cache, prefer local clones"),
- corrections of *how you work* ("diagnose before fixing"),
- general preferences the mentor stated as general ("never hard-wrap Markdown"),
- non-obvious gotchas that cost time and will recur ("tests must run in the base conda env").

When unsure, drop it. The next session will bring it back if it matters, and a sparse wiki recovers more easily than a bloated one. Don't bring borderline candidates to the mentor as proposals, since that just hands them the filtering work; at most, name them in one line at the end: "Not saved: X, Y (one-off)." Then the mentor can rescue one.

Never extract credentials (keys, tokens, passwords). If the session involved one, the lesson is at most *where it lives*, never the value. Also drop anything the wiki already says. Before adding, search the wiki (`grep -ril <keyword> <folder>`), and update the existing lesson rather than writing a near-duplicate. If a lesson's reason isn't clear from the session, ask rather than inventing one.

## Decide where each lesson goes

Follow the layout in `WIKI.md`. In brief:

- Specific to this repo → `projects/<name>.md`. Create the page if needed, with `repo:` frontmatter set to the repo root. A project page holds durable context (purpose, constraints, gotchas, conventions that override general preferences). It is not a changelog or a decision log; that's what git history is for.
- About the mentor, or true across their work → `me/`, `preferences/`, `domain/`, or `tools/`. A good test: would this still apply in a different repo? Also check whether the same lesson already appears on another project's page. If it does, that's a sign it belongs on a general page.
- Sensitive but worth keeping → `private/`, following the same layout (e.g. `private/domain/people.md`). "Sensitive" means information about specific colleagues, confidential or unpublished work, or personal matters. Generalize first: when a lesson can be stated without the sensitive detail, put the general version in the public wiki as well. See "Private knowledge" in `WIKI.md`. Sensitive lessons are always proposed to the mentor, marked `⚠ sensitive`, never written directly.
- A procedure taught more than once, or long and clearly reusable → a **skill candidate**. Don't write the skill during a debrief or review; record it in the journal line and mention it. `/aipprentice:reflect` graduates candidates into `skills/`.

Write lessons in the format from `WIKI.md`: rule first, then *Why:*, then provenance.
