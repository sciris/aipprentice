---
name: debrief
description: End-of-session debrief for the aipprentice knowledge base — review a work session the way a trainee reviews a day with their mentor, extract durable lessons, and file them in project or global memory. Use when the user says "debrief", "let's wrap up", "what did you learn", "remember what we did", "save the lessons from this", or invokes /aipprentice:debrief. Also use with "backlog" to process past sessions that ended without a debrief.
argument-hint: "[backlog | SESSION_ID]"
---

# Debrief

You are an apprentice closing out a work session with your mentor. The goal is the same as a good trainee's end-of-day notes: capture what you'd need to know to do better next time, without the user having to repeat themselves. A small number of sharp, correct lessons beats a long list of trivia.

Arguments: `$ARGUMENTS`

- *(empty)*: debrief the **current session** (it's already in your context).
- `backlog`: debrief past sessions queued by the SessionEnd hook.
- a session ID or transcript path: debrief that one session.

The helper script path is given in the aipprentice session context (`python3 .../scripts/aipprentice.py`). If it's missing, find it with `find ~/.claude/plugins -name aipprentice.py -path '*aipprentice*'`. Run `aipprentice.py paths` to get the storage locations.

## 1. Gather the material

**Current session:** use your own context. If the session was compacted, the summary plus what remains is enough; don't go fishing for the raw transcript.

**Backlog / specific session:** run `aipprentice.py pending --all` (or `pending` for this project only), show the user the list (date, project, title, prompt count), and ask which to process. The default is all of them, oldest first. For each one, run `aipprentice.py condense <session_id>` to get a compact dialogue. For more than ~3 sessions, give each session to a subagent in parallel. Each subagent gets the condensed transcript and the "what counts as a lesson" criteria below, and returns candidate lessons only; you do the filing yourself so deduplication stays consistent. Lessons from backlog sessions belong to *that session's* project (its `cwd`), not necessarily the current one.

## 2. Extract candidate lessons

Look for what a thoughtful new employee would write down:

- **Corrections**: the user said "no", redid your work, or pushed back. What was the underlying preference? Look for the general rule behind the specific fix.
- **Confirmed approaches**: the user explicitly approved an approach or said "yes, exactly, keep doing that". These are easy to miss because they're quiet.
- **Preferences and style**: how they like code, prose, plans, and communication (verbosity, when to ask vs. act).
- **Domain knowledge**: facts about their field, their tools, their organization, or their collaborators that came up and aren't written down anywhere.
- **Project context**: goals, constraints, deadlines, decisions and why they were made, and gotchas (environment quirks, flaky tests, things that look wrong but are intentional).
- **Procedures**: multi-step workflows the user walked you through. Record the steps, not just "we did X".
- **Your own mistakes**: what went wrong on your side and how to avoid it next time.

Drop anything that:

- can be read from the code, git history, README, or an existing `CLAUDE.md`,
- only mattered for this one task,
- is already recorded (check the project memory dir, the global memory dir, and the relevant `CLAUDE.md` files first; update the existing memory rather than creating a near-duplicate),
- is a guess about the user's reasons. If a lesson's **Why** isn't clear from the session, ask the user (see step 4) rather than inventing one.

## 3. Decide where each lesson goes

- **Project memory** (the auto-memory dir for that project): facts about this codebase or project, or preferences the user stated specifically for this project.
- **Global memory** (`~/.claude/aipprentice/memory/`): anything about the user themselves, meaning general preferences, working style, tools, domain knowledge, and org context. It also covers anything that would clearly apply in their other projects. Quick check: `grep -ril "<keyword>" ~/.claude/projects/*/memory/`. If the same lesson already exists in another project's memory, that's strong evidence it's global.
- **Skill candidate**: a procedure the user has now explained more than once, or one that is long and reusable. Don't write the skill during a debrief. Note it as a candidate in the journal and mention it; `/aipprentice:reflect` handles graduating it.

## 4. Apply: small changes directly, big changes by proposal

**Write directly, without asking:**
- *new* project-level memories.

**Propose and wait for approval:**
- any new or changed *global* memory,
- any edit or deletion of an *existing* memory at either level,
- anything touching a `CLAUDE.md` or a skill file (only ever propose these, never make the edit unasked),
- lessons where you're unsure you've understood the rule correctly.

Present proposals in a single numbered list with one line each. Say what the lesson is, where it would go, and whether it's new or an update. Then let the user answer in shorthand ("1, 3, 4; drop 2; 5 is wrong, it's actually…"). Add at most three **questions for my mentor** after the list. These are things you noticed but couldn't interpret, e.g. "You rewrote my plot legend both times. Is it a general rule, or specific to those figures?" Their answers often produce the best lessons.

## 5. File format

Use the same format as the built-in auto memory, at both levels, so everything is interoperable. One fact per file, kebab-case filename matching `name`:

```markdown
---
name: prefers-diagnosis-before-fix
description: When debugging, explain the root cause and wait before changing code
metadata:
  type: feedback
---

When asked to debug, diagnose and report the cause first; only fix once the user says so.

**Why:** User wants to understand the failure and often knows a better fix than the obvious one.
**How to apply:** For any "why is X broken" request, stop after the diagnosis and propose the fix.
```

`type` is one of `user`, `feedback`, `project`, `reference`. For `feedback` and `project`, always include **Why:** and **How to apply:** lines. Convert relative dates to absolute ones. Link related memories with `[[other-name]]`. Don't hard-wrap prose. After adding, changing, or deleting any file, update that directory's `MEMORY.md` index: one line per memory, `- [Title](file.md) — short hook`, no other content. Keep the global index tight, since it's injected into every session.

Never store secrets, credentials, or other people's personal data in memory.

## 6. Close out

1. Mark the sessions as debriefed so the hook doesn't re-queue them. For the current session: `aipprentice.py done ${CLAUDE_SESSION_ID}`. If that variable wasn't substituted, use the newest `.jsonl` stem in this project's `~/.claude/projects/<key>/` dir. For backlog sessions, pass their IDs. Sessions the user chose to skip get marked done as well.
2. Append one journal line per session: `aipprentice.py journal "<one-sentence summary of the work>; learned: <short list>; skill candidates: <if any>"`.
3. Report briefly: what you saved directly (with paths), what's awaiting approval, and any questions. Don't pad it.
