# aipprentice

A Claude Code plugin that makes Claude behave like an apprentice: it learns your preferences, conventions, and domain as you work together, and it gets better over time the way a trainee employee would.

Claude Code's built-in auto memory already saves lessons per project as it works. aipprentice adds what's missing:

- **Cross-project knowledge.** A global knowledge base (`~/.claude/aipprentice/memory/`) for lessons about *you* rather than one repo. It's loaded into every session, so you only have to teach something once.
- **Deliberate debriefs.** `/aipprentice:debrief` reviews a session like end-of-day notes with a mentor: corrections, confirmed approaches, domain facts, procedures, and its own mistakes. It files each lesson at the right level and asks you about anything it couldn't interpret.
- **Nothing slips through.** A SessionEnd hook queues every substantive session (≥3 prompts) that ended without a debrief. The next session mentions the backlog, and `/aipprentice:debrief backlog` processes it after the fact from the saved transcripts.
- **Periodic reflection.** `/aipprentice:reflect` consolidates everything: it promotes lessons that recur across projects, merges duplicates, retires stale memories, and graduates repeated procedures into real skills.

## How approval works

Small changes are written directly; big ones are proposed and wait for your OK.

| Change | Behavior |
|---|---|
| New project-level memory | Written directly, reported afterwards |
| New or changed global memory | Proposed |
| Editing or deleting any existing memory | Proposed |
| New skill, or any `CLAUDE.md` change | Proposed (never edited unasked) |

Proposals come as a numbered list, so you can answer in shorthand ("1, 3, 4; drop 2").

## Install

```bash
claude plugin marketplace add /home/cliffk/idm/aipprentice
claude plugin install aipprentice@aipprentice
```

Restart Claude Code afterwards so the hooks load.

## Usage

- `/aipprentice:debrief`: debrief the current session (run it near the end of anything worth learning from).
- `/aipprentice:debrief backlog`: debrief queued past sessions.
- `/aipprentice:reflect`: consolidate the knowledge base. `/aipprentice:reflect deep` also mines recent transcripts for lessons that never got saved, especially things you had to say more than once.

You can also just say "let's debrief" or "what have you learned about me?".

## Storage

| Path | Contents |
|---|---|
| `~/.claude/aipprentice/memory/` | Global memories (same file format as auto memory) plus the `MEMORY.md` index |
| `~/.claude/projects/<project>/memory/` | Built-in per-project auto memory, which aipprentice also writes to |
| `~/.claude/aipprentice/journal.md` | One line per debrief/reflection: a running work log |
| `~/.claude/aipprentice/pending.jsonl`, `debriefed.txt` | Debrief queue bookkeeping |

Everything is plain Markdown that you can read and edit by hand. Environment overrides: `AIPPRENTICE_HOME` (store location) and `AIPPRENTICE_MIN_TURNS` (queue threshold, default 3).

## Notes

- Backlog debriefs depend on transcripts still existing. Claude Code deletes them after `cleanupPeriodDays` (default 30).
- The global index is injected into every session, so keep it lean. `reflect` will flag it when it grows too large (it's truncated at 8,000 characters).
- Scripts use only the Python standard library (`python3` must be on `PATH`).
