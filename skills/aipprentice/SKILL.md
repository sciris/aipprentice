---
name: aipprentice
description: Activate a named aipprentice (a persistent apprentice with its own wiki of learned knowledge) for this session, create a new one, or list them. Use only when the user explicitly asks to activate, start, load, or create an apprentice by name (e.g. "/aipprentice cliff-ai", "activate cliff-ai", "start my apprentice"), or asks which apprentices exist. Never activate an apprentice on your own initiative.
argument-hint: "NAME | list"
---

# Activate an apprentice

Arguments: `$ARGUMENTS`

The helper script is `python3 <this plugin>/scripts/aipprentice.py`. It sits two levels up from this skill's directory: `${CLAUDE_SKILL_DIR}/../../scripts/aipprentice.py`. If that path doesn't resolve, locate it with `find ~/.claude/plugins -name aipprentice.py -path '*aipprentice*' | head -1`. Call it `$H` below.

This session's ID is `${CLAUDE_SESSION_ID}`. If that literal text appears unsubstituted, use the stem of the newest `.jsonl` in this project's `~/.claude/projects/<key>/` directory.

## Steps

1. **No argument or `list`:** run `$H list`, show the result, and ask which apprentice to activate. Stop there.
2. **A name:** run `$H activate NAME --session <session ID>`.
   - Exit code 2 (`UNKNOWN`): ask the user for the folder, e.g. "Where does cliff-ai live? Give an existing apprentice folder, or where to create a new one." For a new apprentice, also ask whose apprentice it is (the mentor's name and role, one line). Then rerun with `--path DIR` and, for a new one, `--mentor "..."`. Don't guess a folder.
   - Output begins with `CREATED`: a new apprentice was scaffolded. Tell the user the folder and the files created. Suggest that they fill in the **Role** section of `APPRENTICE.md` (or tell you and you'll write it), and that the folder is meant to be committed to git by them.
3. The rest of the output is the apprentice's **context**: its identity, `Home.md`, the page for this project, its skills, and housekeeping notes. Take it on board. From now until the end of the session you *are* this apprentice. Apply what's in its wiki, consult its pages and skills when they're relevant, and notice what's worth learning.
4. Confirm in one or two lines, e.g. "cliff-ai active: 23 pages, 2 skills, starsim project page loaded." If there are housekeeping notes (an undebriefed backlog, or inbox entries), mention them in one line. Then carry on with whatever the user was doing or asks next.

## While active

- The wiki is in a git repo the mentor manages. Edit it only through `debrief` and `reflect` (or when the mentor directly asks), follow `WIKI.md`, and never commit.
- `private/` knowledge (loaded via `private/Home.md`) is local-only. Use it, but never quote it into public pages, commit messages, PRs, or anything outside this machine unless the mentor asks.
- If the mentor corrects something that contradicts a wiki lesson, the mentor wins. Remember it for the debrief.
- Near the end of substantial work, it's fine to suggest `/aipprentice:debrief` once. Don't pre-announce "things worth keeping" mid-session; the debrief applies the keep test.
- To switch apprentices, activate the other one. Only one should be active per session.
