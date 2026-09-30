---
name: review
description: Review the lessons the active aipprentice has staged in the background (auto mode) across recent sessions, and file the ones the mentor approves into its wiki. Sits between a debrief (one session) and reflect (the whole wiki). Use when an apprentice is active and the user says "review", "review the staged lessons", "what have you staged", "file the lessons", or invokes /aipprentice:review.
---

# Review staged lessons

In auto mode, a background agent stages candidate lessons from each session into the apprentice's `.state/staged/` folder without touching the wiki. A review is where the mentor decides what's kept: you look across everything staged, weed it out once more with the benefit of seeing several sessions side by side, present one list, and file what's approved. ("The mentor" is a role name: address them, and write about them, using the name in `APPRENTICE.md`'s `mentor:` field.)

Requires an active apprentice (see step 0 of the `debrief` skill). If none is active, stop and ask the user to activate one. `$H` and `NAME` mean the same as there. Read `WIKI.md` and the lessons guide (`${CLAUDE_SKILL_DIR}/../../guides/lessons.md`) first.

## 1. Stage what's missing

- **Backlog:** run `$H pending NAME`. These sessions ended with work that was never staged (e.g. they ended before a staging point). Stage each one with a `general-purpose` subagent, in parallel, with this prompt: "Stage lessons for aipprentice NAME: read `${CLAUDE_SKILL_DIR}/../../guides/staging.md` and follow it. Helper: `$H`. Apprentice folder: `<folder>`. Session: `<id>`. Project: `<its cwd>`. Staged file: `<folder>/.state/staged/<id>.md`. Read the conversation with `$H condense <id>`." Wait for them all. Skip any whose transcript is missing and mention it.
- **Current session:** if it has had substantial work since it was last staged (or was never staged), stage it yourself now by following the staging guide. You have the conversation in context.

## 2. Gather

Run `$H staged NAME` and read every file it lists. Then, across all of them:

- **Recheck each candidate** against the keep test and the current wiki. Staging was done one session at a time, and the wiki may have changed since. Drop what the wiki now covers, and anything that looks weaker on a second read.
- **Merge** candidates that say the same thing across sessions into one. The same lesson appearing in several sessions or projects is strong evidence: prefer a general page (`preferences/`, `tools/`, …) over a project page for it, and say "seen in N sessions".
- **Contradictions:** a candidate that conflicts with an existing lesson, or with another candidate. Propose which one is current, or ask.
- **Rescue:** skim the `Not saved` sections. If an item recurs across sessions, it has now earned a place: promote it to a candidate.
- **Auto-memory:** collect the files listed under `Auto-memory`, plus anything `$H inbox NAME` still lists for this project.

## 3. Propose

Give one numbered list, grouped by target page, one line each: the lesson, the target, and whether it's new, an update (quote the start of the old lesson), or a new page. Mark sensitive items `⚠ sensitive` with the suggested `private/` target. Then:

- skill candidates, if any, in one line each (reflect graduates them; don't write skills here),
- "Not saved: …" in one line, for the borderline items the mentor might want to rescue,
- at most three **questions for <mentor's name>**, drawn from the staged `Questions` and your own cross-session view.

If nothing survives, say so in one line and skip to step 5. Zero is a normal outcome. The mentor approves in shorthand ("1, 3, 4; drop 2; 5 is wrong, it's actually…"). Wait for the answer before writing anything.

## 4. Apply

File what's approved in the lesson format from `WIKI.md`, and keep `Home.md` in sync (and `private/Home.md` for private pages). Re-read a page before editing an existing lesson. If the guard hook asks the mentor to confirm a write, don't try to get around it.

## 5. Close out

1. **Staged files:** clear every session you reviewed, approved or not, with `$H unstage NAME <session_id> ...`. This deletes their staged files and removes them from the backlog. A session that's resumed later only gets restaged for work done after this point.
2. **Inbox:** run `$H absorbed NAME <file> ...` for each auto-memory file that's now in the wiki or was deliberately dropped. Then offer to delete those files and their `MEMORY.md` lines so the harness stops loading duplicates. Only delete once the mentor agrees.
3. **Scan:** run `$H scan NAME`. If it reports anything, show the findings to the mentor and fix or remove them before reporting. Don't add strings to `.scanignore` yourself.
4. **Journal:** one line with `$H journal NAME "review of N session(s) (<their summaries, briefly>); learned: <short list>; skill candidates: <if any>"`.
5. **Report briefly:** pages changed (list `private/` pages separately) and anything deferred. Mention that public changes are visible with `git diff` in the apprentice folder. Never commit.
