# aipprentice

A Claude Code plugin for **apprentices**: named, persistent assistants that learn your preferences, conventions, and domain as you work together, the way a trainee employee would. Each apprentice keeps what it learns in a human-readable Markdown wiki in its own folder.

Apprentices are **opt-in per session**. Nothing loads, and nothing is recorded, unless you activate one.

## Quick start

```bash
claude plugin marketplace add /home/cliffk/idm/aipprentice
claude plugin install aipprentice@aipprentice
```

Restart Claude Code. Then, in any session:

```
/aipprentice cliff-ai          # activate (or create) the apprentice named cliff-ai
... work as usual ...
/aipprentice:debrief           # capture what it learned from this session
```

The first time you use a name, it asks for a folder, e.g. `/home/cliffk/idm/idm-aipprentices/cliff-ai`, and creates the apprentice there. After that, the name alone is enough. If the short form `/aipprentice` doesn't resolve, use `/aipprentice:aipprentice cliff-ai`.

## Commands

| Command | What it does |
|---|---|
| `/aipprentice NAME` | Activate an apprentice for this session: loads its identity, `Home.md`, the page for the current repo, and its skills |
| `/aipprentice list` | List registered apprentices |
| `/aipprentice:debrief` | Review this session like end-of-day notes with a mentor and file the lessons in the wiki |
| `/aipprentice:debrief backlog` | Debrief past activated sessions that ended without one |
| `/aipprentice:reflect [deep]` | Tidy the wiki: promote, merge, retire stale lessons, and graduate repeated procedures into skills. `deep` also mines transcripts for things you had to say more than once |

## An apprentice's folder

The structure is specified in [`template/WIKI.md`](template/WIKI.md), which is copied into each apprentice. Edit that copy to change the conventions for that apprentice.

```
cliff-ai/
  APPRENTICE.md   # identity and role (you edit this)
  WIKI.md         # conventions: layout, page and lesson format, linking
  Home.md         # index of every page; loaded on activation
  me/ preferences/ domain/ tools/ projects/
  skills/<name>/SKILL.md
  journal/YYYY-MM.md
  .state/         # debrief queue; gitignored
```

Pages are organized by topic and use `[[wikilinks]]`, so the folder opens directly as an Obsidian vault. Each lesson is a bullet with its rule, its reason, and where it came from:

```markdown
- Diagnose and report the root cause before changing code; fix only once asked. *Why:* the mentor usually knows a better fix. (2026-08-14, starsim)
```

Put the folder in git. The apprentice never commits, so `git diff` shows exactly what it learned, and you review and commit it yourself.

**Skills** in `skills/` use the standard Claude Code format. They're available only while their apprentice is active (it reads them itself when relevant). To make one always available, symlink it into `~/.claude/skills/`.

## How learning works

- **During the session**, the apprentice applies its wiki, and Claude Code's built-in auto memory keeps saving notes as usual.
- **Debrief** extracts corrections, confirmed approaches, preferences, domain facts, procedures, and its own mistakes. It also folds in the project's auto-memory notes (the "inbox"), and ends with a few questions for you about things it couldn't interpret.
- **Automatic backlog**: when an activated session with ≥3 prompts ends without a debrief, a hook queues it. The next activation mentions it, and `debrief backlog` processes it from the saved transcript.
- **Reflect** is the periodic review that keeps the wiki coherent.

Small changes are written directly; big ones are proposed first as a numbered list you can answer in shorthand ("1, 3; drop 2"):

| Change | Behavior |
|---|---|
| New lessons on the current project's page (or creating it) | Written directly |
| New lessons on shared pages (`me/`, `preferences/`, `domain/`, `tools/`) | Proposed |
| Editing or removing existing lessons, new folders, skills | Proposed |
| Deleting absorbed auto-memory files; anything outside the apprentice folder | Proposed |

## Housekeeping state

Kept in `~/.claude/aipprentice/`: `registry.json` (name → folder) and `active.json` (which sessions activated which apprentice). The debrief queue is stored in each apprentice's `.state/`. Environment overrides: `AIPPRENTICE_HOME` (state location) and `AIPPRENTICE_MIN_TURNS` (queue threshold, default 3).

## Notes

- Backlog debriefs need the transcripts to still exist. Claude Code deletes them after `cleanupPeriodDays` (default 30).
- `Home.md` and the project page are injected on activation, so keep them lean. `reflect` flags them when they grow too large.
- Scripts use only the Python standard library (`python3` must be on `PATH`).
