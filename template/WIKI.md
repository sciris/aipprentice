# Wiki conventions

This file defines how this apprentice's knowledge is organized. It is written for both the humans who read and edit this folder and the apprentice that maintains it. If you change a convention here, the apprentice follows the new version from its next activation.

## Layout

```
<apprentice>/
  APPRENTICE.md     # who this apprentice is and who it works for (edited by the human)
  WIKI.md           # these conventions
  Home.md           # front page: one line per page; loaded on every activation
  me/               # the mentor: role, background, working style, communication preferences
  preferences/      # how the mentor wants things done: coding-style.md, writing-style.md, git.md, ...
  domain/           # subject-matter knowledge: fields, libraries, organizations, people/roles
  tools/            # environments and tools: conda.md, quarto.md, azure.md, ...
  projects/         # one page per repo or piece of work
  skills/           # procedures, one folder each: skills/<name>/SKILL.md
  journal/          # work log, one file per month: journal/2026-09.md
  private/          # local-only knowledge, same layout and conventions; gitignored
  .state/           # machine bookkeeping (debrief queue); gitignored, never edit by hand
  .scanignore       # optional: strings the mentor has OK'd for the sensitive-data guard, one per line
```

Folders are created as needed. Don't create a new top-level folder unless no existing folder fits, and if you do, record it here.

## Pages

A page covers one **topic**, not one fact. Prefer adding a bullet to an existing page over creating a new one. Split a page when it passes about 150 lines, or when it covers two things you'd look up separately.

- Filenames are lowercase-kebab-case (`writing-style.md`); the title is the first `#` heading.
- Frontmatter is optional except on project pages:

  ```yaml
  ---
  repo: /home/user/code/myproject   # project pages only: absolute path of the repo root
  updated: 2026-09-25
  ---
  ```

- Prose is never hard-wrapped. One paragraph or bullet per line.

## Lessons

Most content consists of **lessons**: bullets that tell the apprentice what to do, with the reason and where it came from.

```markdown
- Diagnose and report the root cause before changing any code; fix only once asked. *Why:* the mentor usually knows a better fix than the obvious one. (2026-08-14, starsim)
```

- **Rule first**, stated so it can be acted on.
- ***Why:*** always include it for preferences and corrections. If it's unknown, write `*Why:* unknown — ask` rather than guessing.
- **Provenance** in parentheses: the date learned and the project or context. Add the session ID only when the source conversation is likely to be worth revisiting.
- When a lesson changes, edit it in place and update the date. Don't leave the old version beside the new one. If the history matters, add "(was: …)".
- Group bullets under `##` headings within a page (e.g. `## Plots`, `## Docstrings` on `coding-style.md`).

Facts that aren't rules (a person's role, how a system is wired, a deadline) can be written as ordinary prose or bullets, still with provenance.

## Links

- Link with `[[page]]` or `[[folder/page]]`, without the `.md`. Links to pages that don't exist yet are fine; they mark gaps.
- Link generously: project pages link to the domain, tools and skills they use, and skills link to the pages they depend on.
- Link skills as `[[skills/<name>/SKILL]]`.

## Home.md

`Home.md` is the index and is loaded into every activated session, so keep it short (under ~60 lines). It has one section per top-level folder, with one line per page: `- [[preferences/coding-style]]: style rules for Python, plots, docstrings`. Every page must be listed. Pages missing from Home.md are effectively invisible.

## Project pages

`projects/<name>.md` holds everything specific to one repo: goals, current state, decisions and their reasons, conventions that override general preferences, and known gotchas. The `repo:` frontmatter lets the apprentice load the right page automatically when a session starts in that repo. Knowledge that applies beyond the project goes in `preferences/`, `domain/`, or `tools/`, and the project page links to it.

## Skills

A skill is a repeatable procedure with several steps that the mentor has taught more than once. It's stored in the standard Claude Code format, so it can be exported unchanged:

```markdown
---
name: release-starsim
description: Steps to cut a Starsim release — when to use it, in trigger-rich wording
---

# Release Starsim
1. ...
```

While the apprentice is active, it treats these as its own skills: it knows their names and descriptions and reads the full `SKILL.md` when one applies. They are not visible to Claude Code when no apprentice is active. To make one always available, copy or symlink it into `~/.claude/skills/`.

## Journal

`journal/YYYY-MM.md` has one bullet per debrief or reflection: `- 2026-09-25 (starsim): refactored time units; learned: X, Y; skill candidates: Z`. It's a record of the work done, and reflection draws on it to spot recurring patterns.

## Private knowledge

`private/` holds knowledge that's useful to keep but shouldn't be committed. Examples: notes about specific colleagues, confidential or unpublished work, anything under embargo, and personal circumstances the mentor has shared. It uses the same conventions as the public wiki (topic pages, lesson format, links), with its own index at `private/Home.md`. It's gitignored, so it exists only on this machine and isn't backed up by git. The mentor handles backup separately if they want it.

- **One-way links.** Private pages may link to public ones (`[[../preferences/coding-style]]`). Public pages never link to, name, or hint at private pages or their content.
- **Generalize first.** If a lesson can be stated without the sensitive detail, put the general version in the public wiki and only the detail in `private/`. Example: public, "Check authorship order with the mentor before submitting"; private, the specific people and the history behind it.
- **When in doubt, private.** It's easy to move a page from `private/` to public later, and impossible to un-commit something.

## Sensitive data

- **Never store credentials** anywhere, including `private/`: API keys, tokens, passwords, private keys, connection strings. Record *where* a secret lives and how to get it instead ("the Azure key is in Key Vault `idm-kv`, secret `storage-key`").
- **Personal data** about anyone other than the mentor goes in `private/` or nowhere. This includes contact details, health, HR or performance matters, and personal opinions about people.
- **A guard hook** checks every write into this folder. If it sees something that looks like a credential (anywhere) or personal data such as an email address (outside `private/`), it stops and asks the mentor to confirm. If `private/` isn't gitignored, writes to it also require confirmation. False positives can be allowed permanently by adding the exact string to `.scanignore`.
- The guard matches patterns, so it is a backstop and doesn't replace judgment. It can't recognize a confidential fact written in plain prose. The rules above still apply.

## What doesn't belong here

- Anything that can be read from the code, git history, or a repo's own docs/`CLAUDE.md`.
- One-off task details.
- Credentials of any kind (see above).
