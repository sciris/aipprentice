---
name: reflect
description: Periodic review of everything the active aipprentice has learned — tidy the wiki, promote lessons that recur across projects to general pages, retire stale or contradictory ones, and graduate repeated procedures into skills. Use when an apprentice is active and the user says "reflect", "review what you've learned", "clean up the wiki", "what have you learned about me", or invokes /aipprentice:reflect.
argument-hint: "[deep]"
---

# Reflect

A debrief captures one session. Reflection is the less frequent step back, like a quarterly review of your own notes: make the wiki coherent, and turn what has become routine into procedure. Reflection mostly changes existing knowledge, so **every change is proposed first and only applied once the mentor approves it**.

Arguments: `$ARGUMENTS`. With `deep`, also mine transcripts for lessons that were never saved (step 2).

Requires an active apprentice (see step 0 of the `debrief` skill). If none is active, stop and ask the user to activate one. `$H` and `NAME` mean the same as there. Read `WIKI.md` first.

## 1. Take inventory

Read without editing: every wiki page (including `private/`), `skills/*/SKILL.md`, and the recent journal pages. Also read the auto-memory inbox for each project that has a project page (`$H inbox NAME`, run from that repo, or read `~/.claude/projects/<key>/memory/` directly), plus `~/.claude/CLAUDE.md` and `~/.claude/skills/`, so you don't duplicate what's already a firm rule or an installed skill. If the wiki is large, have subagents summarize sections in parallel.

## 2. (deep only) Mine unsaved lessons

Run `$H pending NAME` and process those sessions with `$H condense <id>`, fanning out to subagents. Look for anything the mentor had to say **more than once**, across sessions: repeated corrections, explanations, or instructions. These are the costliest gaps. Mark processed sessions with `$H done NAME ...`.

## 3. Find what needs attention

- **Promote**: the same lesson appears on several project pages, or a project-page lesson is really about the mentor. Propose moving it to the right general page and linking back.
- **Merge / split**: near-duplicate lessons, overlapping pages, or pages past ~150 lines.
- **Contradict**: lessons that disagree. Propose a resolution, or ask which one is current.
- **Stale**: lessons that name files, functions, flags, branches, people's roles, or deadlines. Spot-check that these still exist or still apply.
- **Sharpen**: lessons with no actionable rule, or with `*Why:* unknown`. Propose a rewrite, or ask for the reason.
- **Structure**: pages missing from `Home.md`, a `Home.md` that has grown past ~60 lines, broken or missing `[[links]]`, and pages in the wrong folder under `WIKI.md`.
- **Graduate to a skill**: skill candidates from the journal, and procedures that recur across pages or sessions. Draft `skills/<name>/SKILL.md` in the format given in `WIKI.md`, with a trigger-rich `description`. Link it from the pages it relates to, and remove the procedure text it replaces.
- **Elevate**: a firm, frequently relevant rule might also belong in a repo's `CLAUDE.md` or in `~/.claude/CLAUDE.md`, or a skill might be worth making always-on in `~/.claude/skills/`. Suggest these only; the mentor maintains those locations.
- **Sensitive**: run `$H scan NAME`, and also read for sensitive prose the scanner can't catch. Propose moving it to `private/`, generalizing it, or deleting it. Check that no public page links to or names a private page.
- **Gaps**: areas where you work with the mentor a lot but know little. Turn one or two into questions.

## 4. Propose

Give one report, grouped by the categories above and numbered throughout. Each item gets one line: what, which pages, and the proposed action. Lead with the highest-value items and skip empty categories. For skill drafts, give the name, description, and outline, and show the full text only if asked. The mentor approves in shorthand ("do 1–6, 8; skip 7; show me 9").

## 5. Apply what's approved

Edit according to `WIKI.md`, and keep `Home.md` in sync. Re-read a page before rewriting or deleting it. Finish with `$H journal NAME "reflection: <what changed>"` and a short summary of what changed and what was deferred. Point out that everything can be reviewed with `git diff` in the apprentice folder. Never commit.
