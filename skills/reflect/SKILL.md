---
name: reflect
description: Periodic review of everything the aipprentice has learned — consolidate duplicate memories, promote lessons that recur across projects to global memory, retire stale or contradictory ones, and graduate repeated procedures into new skills. Use when the user says "reflect", "review what you've learned", "clean up your memory", "consolidate the knowledge base", "what have you learned about me", or invokes /aipprentice:reflect.
argument-hint: "[deep]"
---

# Reflect

A debrief captures lessons from one session. Reflection is the less frequent step back, like a quarterly review of your own notes: look across everything you've learned, make it coherent, and turn what's become routine into proper procedure. Everything in a reflection changes existing knowledge, so **every change is proposed first and only applied once the user approves it**.

Arguments: `$ARGUMENTS`. With `deep`, also mine recent transcripts for lessons that never got saved (step 2).

The helper script path is given in the aipprentice session context. Run `aipprentice.py paths` for locations.

## 1. Take inventory

Read, don't edit:

- global memory: `~/.claude/aipprentice/memory/*.md`
- every project's auto memory: `~/.claude/projects/*/memory/*.md`
- the journal: `~/.claude/aipprentice/journal.md`
- `~/.claude/CLAUDE.md` and personal skills in `~/.claude/skills/`, so you don't duplicate what's already a firm rule or an existing skill

With many projects, have subagents summarize each project's memories in parallel (name, type, one-line gist) and work from those summaries.

## 2. (deep only) Mine unsaved lessons

Look at transcripts from roughly the last month that were never debriefed (`aipprentice.py pending --all`, plus a sample of other recent `~/.claude/projects/*/*.jsonl`). Use `aipprentice.py condense <id>` and fan out to subagents. Look for things the user had to say **more than once** across sessions: repeated corrections, repeated explanations, repeated instructions. Those are the costliest gaps in the knowledge base. Mark any sessions you process with `aipprentice.py done`.

## 3. Find what needs attention

- **Promote**: the same lesson appears in two or more projects' memories, or it's clearly about the user rather than the project. Propose one global memory and removal of the project copies.
- **Merge**: near-duplicates within a level. Propose a single combined memory.
- **Contradict**: two memories that disagree. Propose a resolution, or ask which is current.
- **Stale**: memories that name files, functions, flags, branches, or deadlines. Spot-check whether those still exist or still apply, and propose updating or deleting the ones that don't.
- **Sharpen**: vague memories with no actionable **How to apply**, or no **Why**. Propose a rewrite, or ask the user for the missing reason.
- **Elevate**: a global lesson that is firm, important, and often relevant may belong in `~/.claude/CLAUDE.md`. Only suggest it; the user maintains that file.
- **Graduate to a skill**: a procedure that recurs in memories, journal skill candidates, or transcripts, and has several steps someone could follow. Draft the skill: a `SKILL.md` with `name`, a trigger-rich `description`, and the steps. It goes in `~/.claude/skills/<name>/` for a personal skill, or `<repo>/.claude/skills/<name>/` if it's specific to one project. Once it's approved, the memories it replaces can be deleted.
- **Gaps**: areas where you keep working with the user but have almost no knowledge recorded. List one or two as questions for the user.

## 4. Propose

Present a single report, grouped by the categories above, with every item numbered. For each: a one-line description, the affected file paths, and the proposed action. Lead with the highest-value items; skip categories that have nothing. For skill drafts, show the full proposed `SKILL.md` only when the user asks. List the name, description, and steps in brief first. Let the user approve in shorthand ("do 1–6, 8; skip 7; show me 9").

## 5. Apply what's approved

Use the memory file format from the `debrief` skill. Update every affected `MEMORY.md` index when files are added, merged, or deleted. Before deleting or overwriting a memory, re-read it so you're sure it's the one you mean. Don't edit `CLAUDE.md` files or existing skills unless the user approved that specific item. Finish with `aipprentice.py journal "reflection: <what changed>"` and a short summary of what changed and what was deferred.
