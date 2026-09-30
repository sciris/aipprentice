# AIpprentice

A Claude Code plugin for **AI apprentices** ("aipprentices"): named, persistent assistants that learn your preferences, conventions, and domain as you work together, the way a trainee employee would. Each apprentice keeps what it learns in a human-readable Markdown wiki in its own folder.

Apprentices are **opt-in per session**. Nothing loads, and nothing is recorded, unless you activate one.

## Quick start

```bash
claude plugin marketplace add /home/cliffk/idm/aipprentice
claude plugin install aipprentice@aipprentice
```

Restart Claude Code. Then, in any session:

```
/aipprentice cliff-ai          # activate (or create) the apprentice named cliff-ai
... work as usual; lessons are staged in the background ...
/aipprentice:review            # every so often: approve what it staged, and it files the lessons
```

The first time you use a name, it asks for a folder, e.g. `/home/cliffk/idm/idm-aipprentices/cliff-ai`, and creates the apprentice there. After that, the name alone is enough. If the short form `/aipprentice` doesn't resolve, use `/aipprentice:aipprentice cliff-ai`.

## Commands

| Command | What it does |
|---|---|
| `/aipprentice NAME` | Activate an apprentice for this session: loads its identity, `Home.md`, the page for the current repo, and its skills |
| `/aipprentice list` | List registered apprentices |
| `/aipprentice:review` | File staged lessons (auto mode): stages any sessions that were missed, rechecks and merges candidates across sessions, and proposes one list for you to approve |
| `/aipprentice:debrief` | Review this session like end-of-day notes with a mentor and file the lessons in the wiki. The main workflow in manual mode; available on demand in auto mode. If past activated sessions ended without a debrief, it asks whether to debrief the current session, the backlog, or the backlog then the current session |
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
  .state/         # debrief queue, staged lessons; gitignored
```

Pages are organized by topic and use `[[wikilinks]]`, so the folder opens directly as an Obsidian vault. Each lesson is a bullet with its rule, its reason, and where it came from:

```markdown
- Diagnose and report the root cause before changing code; fix only once asked. *Why:* the mentor usually knows a better fix. (2026-08-14, starsim)
```

Put the folder in git. The apprentice never commits, so `git diff` shows exactly what it learned, and you review and commit it yourself.

**Skills** in `skills/` use the standard Claude Code format. They're available only while their apprentice is active (it reads them itself when relevant). To make one always available, symlink it into `~/.claude/skills/`.

## How learning works

Each apprentice has a learning mode, set by `mode:` in `APPRENTICE.md` (`auto` if absent). Change it with `aipprentice.py mode NAME manual` (or `auto`), or by editing the file.

- **During the session**, the apprentice applies its wiki, and Claude Code's built-in auto memory keeps saving notes as usual.
- **Auto mode (default).** At natural stopping points (a piece of work done and reacted to, or the session wrapping up), the apprentice quietly launches a background subagent (a fork of the session, so it sees the whole conversation). The subagent applies the keep test and writes candidate lessons, plus any new auto-memory notes, to `.state/staged/<session>.md`. It never touches the wiki, and staging again later in the session updates the same file. You'll see at most a one-line note like "_Staged 2 lessons for review._"
- **Review** (`/aipprentice:review`, whenever convenient) first stages any sessions that ended before they could be staged. It then rechecks every candidate against the current wiki, merges ones that recur across sessions (which usually means they belong on a general page), and presents a single numbered list. Only what you approve gets written. Activation tells you how much is waiting.
- **Manual mode.** Nothing is staged; you run a debrief at the end of a session instead.
- **Debrief** extracts corrections, confirmed approaches, preferences, domain facts, procedures, and its own mistakes. It also folds in the project's auto-memory notes (the "inbox"), and ends with a few questions for you about things it couldn't interpret.
- **Automatic backlog**: when an activated session ends with ≥3 prompts that were never staged or debriefed, a hook queues it. The next activation mentions it, and the next review (auto) or debrief (manual) processes it from the saved transcript.
- **Reflect** is the periodic review that keeps the wiki coherent.

The rules for what's worth keeping and where it goes are shared by all three, in [`guides/lessons.md`](guides/lessons.md); the background stager follows [`guides/staging.md`](guides/staging.md).

In auto mode, everything goes through review. In a debrief, small changes are written directly and big ones are proposed first as a numbered list you can answer in shorthand ("1, 3; drop 2"):

| Change | Behavior |
|---|---|
| New lessons on the current project's page (or creating it) | Written directly |
| New lessons on shared pages (`me/`, `preferences/`, `domain/`, `tools/`) | Proposed |
| Editing or removing existing lessons, new folders, skills | Proposed |
| Deleting absorbed auto-memory files; anything outside the apprentice folder | Proposed |

## Private knowledge and sensitive data

- **`private/`** in each apprentice folder holds knowledge worth keeping but not committing: notes about colleagues, confidential or unpublished work, personal matters. It's gitignored, uses the same wiki conventions, and has its own `private/Home.md` that loads on activation. Public pages never link into it. Because it's gitignored, it isn't backed up by git.
- **Guard hook.** Every Write/Edit/Bash that targets an apprentice folder is scanned, whether or not an apprentice is active. Credentials (API keys, tokens, passwords, private keys, credentialed URLs, and similar) always trigger a confirmation prompt, even in `private/`. Personal data such as email addresses triggers one outside `private/`. Writes to `private/` also prompt if it isn't actually gitignored. To allow a false positive permanently, add the string to `<apprentice>/.scanignore`.
- **Debrief rules.** Credentials are never extracted, only where they live. Sensitive lessons are always proposed and marked `⚠ sensitive`, never written directly. Each debrief and review ends with a scan (`aipprentice.py scan NAME`).
- **Redaction.** Condensed transcripts used for backlog debriefs have credentials masked before any model sees them.
- **Limits.** Pattern matching catches credentials and contact details, not confidential facts written in plain prose. That part relies on the rules in `WIKI.md` and on your review of `git diff` before committing.

## Housekeeping state

Kept in `~/.claude/aipprentice/`: `registry.json` (name → folder), `aliases.json` (alias → name, e.g. `ai` → `cliff-ai`; add one with `/aipprentice alias cliff-ai ai`), and `active.json` (which sessions activated which apprentice). The debrief queue and staged lessons are stored in each apprentice's `.state/`. Environment overrides: `AIPPRENTICE_HOME` (state location) and `AIPPRENTICE_MIN_TURNS` (queue threshold, default 3).

## Notes

- Backlog debriefs and reviews need the transcripts to still exist. Claude Code deletes them after `cleanupPeriodDays` (default 30).
- `Home.md` and the project page are injected on activation, so keep them lean. `reflect` flags them when they grow too large.
- Scripts use only the Python standard library (`python3` must be on `PATH`).
