---
name: debrief
description: End-of-session debrief for the active aipprentice — review a work session the way a trainee reviews a day with their mentor, extract durable lessons, and file them in the apprentice's wiki. Use when an apprentice is active and the user says "debrief" or invokes /aipprentice:debrief. When the apprentice is in manual mode, also use it for "let's wrap up", "what did you learn", or "save the lessons from this" (in auto mode those mean background staging instead; see the activation context). If past sessions ended without a debrief, it offers to process those too.
argument-hint: "[SESSION_ID]"
---

# Debrief

You are an apprentice closing out a work session with your mentor. ("The mentor" here is a role name: in everything you say and write, use the name from `APPRENTICE.md`'s `mentor:` field.) The goal is the same as a good trainee's end-of-day notes: capture what you'd need to know to do better next time, so the mentor never has to repeat themselves. A few sharp, correct lessons beat a long list of trivia.

Arguments: `$ARGUMENTS`

- *(empty)*: debrief the **current session** (already in your context), plus any backlogged sessions the mentor chooses (step 1).
- a session ID or transcript path: debrief that one session.

## 0. Which apprentice

This only works with an active apprentice. The context will contain `# aipprentice: "<name>" is active`, along with its folder, the helper script path, and the session ID. If no apprentice is active, stop and tell the user to activate one with the `aipprentice` skill (e.g. `/aipprentice <name>`). Don't pick one yourself.

Below, `$H` stands for `python3 <helper path> ` and `NAME` for the apprentice name. **Read the apprentice's `WIKI.md` before writing anything.** It defines the layout, the page and lesson format, and the linking rules, and it may have been edited since you last saw it.

## 1. Gather the material

First, check the backlog: run `$H pending NAME` (ignore the current session if it appears). If it lists any sessions, show them (date, project, title, prompt count) and ask the mentor which to debrief:

1. **the current session** only,
2. **the backlog** only (all listed sessions by default, oldest first; the mentor can pick a subset),
3. **the backlog, then the current session**.

If nothing is pending, skip the question and debrief the current session.

- **Current session:** use your own context. If the session was compacted, the summary plus what remains is enough.
- **Inbox:** run `$H inbox NAME`. Any files it lists are notes Claude Code's built-in auto memory saved for this project, and they haven't been folded into the wiki yet. Read them and treat each one as a candidate lesson. They get the same filtering as everything else (step 2): auto memory saves liberally, and many entries won't pass. Mark the ones you drop as absorbed as well.
- **Backlog / specific session:** run `$H condense <session_id>` on each for a compact dialogue. For more than ~3 sessions, hand each condensed transcript to a subagent in parallel, along with the lessons guide's path (step 2). Have the subagents return candidate lessons only, and do all the filing yourself so deduplication stays consistent. Lessons from a backlog session belong to *that session's* project (its `cwd`).

## 2. Extract lessons and place them

Read the lessons guide, `${CLAUDE_SKILL_DIR}/../../guides/lessons.md`, and apply it to the material: extract candidates, cut most of them with the keep test, and decide which page each survivor goes on. When a lesson's reason isn't clear from the session, ask (step 4) rather than inventing one.

## 3. Staged lessons

If the apprentice is in auto mode, this session may already have a staged file (`$H staged NAME` lists them). Treat its candidates as part of this debrief's material. Leave other sessions' staged files for `/aipprentice:review`.

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

Present proposals as a single numbered list, one line each: the lesson, the target page, and whether it's new or an update. The mentor can then answer in shorthand ("1, 3, 4; drop 2; 5 is wrong, it's actually…"). After the list, add at most three **questions for <mentor's name>**. These are things you noticed but couldn't interpret, e.g. "You rewrote my plot legend both times. Is that a general rule or specific to those figures?"

Write in the lesson format from `WIKI.md`: rule first, then *Why:*, then provenance.

## 5. Close out

1. **Inbox:** once an auto-memory file's content is in the wiki (or deliberately dropped), run `$H absorbed NAME <file> ...`. Then offer to delete the absorbed files and their `MEMORY.md` lines so the harness stops loading duplicates. Only delete once the mentor agrees.
2. **Sessions:** mark each debriefed session so the hook doesn't re-queue it: `$H done NAME <session_id> ...`. Use the session ID from the activation context for the current session, and include backlog sessions the mentor chose to skip. If the current session had a staged file, clear it with `$H unstage NAME <session_id>`.
3. **Scan:** run `$H scan NAME`. If it reports anything, show the findings to the mentor and fix or remove them before reporting. Don't add strings to `.scanignore` yourself; only the mentor does that.
4. **Journal:** add one line per session with `$H journal NAME "<one-sentence summary of the work>; learned: <short list>; skill candidates: <if any>"`. Keep the summary to one short clause ("restyled the dashboard"), not a changelog; the repo's git history has the details.
5. **Report briefly:** pages changed (list `private/` pages separately), what's awaiting approval, and questions. Mention that public changes are visible with `git diff` in the apprentice folder (private ones aren't, since they're gitignored). Never commit.
