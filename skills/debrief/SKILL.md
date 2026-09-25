---
name: debrief
description: End-of-session debrief for the active aipprentice — review a work session the way a trainee reviews a day with their mentor, extract durable lessons, and file them in the apprentice's wiki. Use when an apprentice is active and the user says "debrief", "let's wrap up", "what did you learn", "save the lessons from this", or invokes /aipprentice:debrief. Also use with "backlog" to process past sessions that ended without a debrief.
argument-hint: "[backlog | SESSION_ID]"
---

# Debrief

You are an apprentice closing out a work session with your mentor. The goal is the same as a good trainee's end-of-day notes: capture what you'd need to know to do better next time, so the mentor never has to repeat themselves. A few sharp, correct lessons beat a long list of trivia.

Arguments: `$ARGUMENTS`

- *(empty)*: debrief the **current session** (already in your context).
- `backlog`: debrief past sessions this apprentice queued.
- a session ID or transcript path: debrief that one session.

## 0. Which apprentice

This only works with an active apprentice. The context will contain `# aipprentice: "<name>" is active`, along with its folder, the helper script path, and the session ID. If no apprentice is active, stop and tell the user to activate one with the `aipprentice` skill (e.g. `/aipprentice <name>`). Don't pick one yourself.

Below, `$H` stands for `python3 <helper path> ` and `NAME` for the apprentice name. **Read the apprentice's `WIKI.md` before writing anything.** It defines the layout, the page and lesson format, and the linking rules, and it may have been edited since you last saw it.

## 1. Gather the material

- **Current session:** use your own context. If the session was compacted, the summary plus what remains is enough.
- **Inbox:** run `$H inbox NAME`. Any files it lists are notes Claude Code's built-in auto memory saved for this project, and they haven't been folded into the wiki yet. Read them and treat each one as a candidate lesson. They get the same filtering as everything else (step 2): auto memory saves liberally, and many entries won't pass. Mark the ones you drop as absorbed as well.
- **Backlog / specific session:** run `$H pending NAME`, show the user the list (date, project, title, prompt count), and ask which to process. The default is all of them, oldest first. Run `$H condense <session_id>` on each for a compact dialogue. For more than ~3 sessions, hand each condensed transcript to a subagent in parallel, along with the criteria in step 2. Have the subagents return candidate lessons only, and do all the filing yourself so deduplication stays consistent. Lessons from a backlog session belong to *that session's* project (its `cwd`).

## 2. Extract candidate lessons, then cut most of them

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

Never extract credentials (keys, tokens, passwords). If the session involved one, the lesson is at most *where it lives*, never the value. Also drop anything the wiki already says. Before adding, search the wiki (`grep -ril <keyword> <folder>`), and update the existing lesson rather than writing a near-duplicate. If a lesson's reason isn't clear from the session, ask (step 4) rather than inventing one.

## 3. Decide where each lesson goes

Follow the layout in `WIKI.md`. In brief:

- Specific to this repo → `projects/<name>.md`. Create the page if needed, with `repo:` frontmatter set to the repo root. A project page holds durable context (purpose, constraints, gotchas, conventions that override general preferences). It is not a changelog or a decision log; that's what git history is for.
- About the mentor, or true across their work → `me/`, `preferences/`, `domain/`, or `tools/`. A good test: would this still apply in a different repo? Also check whether the same lesson already appears on another project's page. If it does, that's a sign it belongs on a general page.
- Sensitive but worth keeping → `private/`, following the same layout (e.g. `private/domain/people.md`). "Sensitive" means information about specific colleagues, confidential or unpublished work, or personal matters. Generalize first: when a lesson can be stated without the sensitive detail, put the general version in the public wiki as well. See "Private knowledge" in `WIKI.md`.
- A procedure taught more than once, or long and clearly reusable → a **skill candidate**. Don't write the skill during a debrief; record it in the journal line and mention it. `/aipprentice:reflect` graduates candidates into `skills/`.

## 4. Apply: small changes directly, big changes by proposal

**Write directly** (report afterwards):
- new lessons on the current project's page, including creating that page,
- the matching `Home.md` line when you create a page.

**Propose, then wait for approval:**
- new lessons on shared pages (`me/`, `preferences/`, `domain/`, `tools/`),
- editing or removing any existing lesson,
- new pages outside `projects/`, new folders, and anything in `skills/`,
- deleting absorbed auto-memory files (see step 5),
- anything outside the apprentice folder (e.g. a repo's `CLAUDE.md`). Only ever propose these.
- **anything sensitive, public or private.** Mark it `⚠ sensitive` in the list and say where you'd put it. The mentor decides whether it's kept at all, and whether it goes in `private/`.

If the guard hook asks the mentor to confirm a write, don't try to get around it (e.g. by rewording to dodge the pattern, or by writing through a different tool). The prompt is the mentor's decision point.

Present proposals as a single numbered list, one line each: the lesson, the target page, and whether it's new or an update. The mentor can then answer in shorthand ("1, 3, 4; drop 2; 5 is wrong, it's actually…"). After the list, add at most three **questions for my mentor**. These are things you noticed but couldn't interpret, e.g. "You rewrote my plot legend both times. Is that a general rule or specific to those figures?"

Write in the lesson format from `WIKI.md`: rule first, then *Why:*, then provenance.

## 5. Close out

1. **Inbox:** once an auto-memory file's content is in the wiki (or deliberately dropped), run `$H absorbed NAME <file> ...`. Then offer to delete the absorbed files and their `MEMORY.md` lines so the harness stops loading duplicates. Only delete once the mentor agrees.
2. **Sessions:** mark each debriefed session so the hook doesn't re-queue it: `$H done NAME <session_id> ...`. Use the session ID from the activation context for the current session, and include backlog sessions the mentor chose to skip.
3. **Scan:** run `$H scan NAME`. If it reports anything, show the findings to the mentor and fix or remove them before reporting. Don't add strings to `.scanignore` yourself; only the mentor does that.
4. **Journal:** add one line per session with `$H journal NAME "<one-sentence summary of the work>; learned: <short list>; skill candidates: <if any>"`.
5. **Report briefly:** pages changed (list `private/` pages separately), what's awaiting approval, and questions. Mention that public changes are visible with `git diff` in the apprentice folder (private ones aren't, since they're gitignored). Never commit.
