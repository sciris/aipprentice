# Staging lessons (auto mode)

You are staging lessons from one work session for an aipprentice, so its mentor can approve them later with `/aipprentice:review`. You run in the background: the mentor is busy with their session and must not be interrupted. **You never edit the wiki.** Your only output is one staged file, plus a one-line reply. ("The mentor" is a role name: in what you write, use the name from `APPRENTICE.md`'s `mentor:` field.)

Your prompt gives the helper command (`$H` below), the apprentice name (`NAME`), its folder, the session ID, the project, the staged file's path, and where the conversation is: in your own context (if you are a fork of the session), or readable with `$H condense <session ID>`. In the latter case, save it to a file of your own first (`$H condense <session ID> > <scratch dir>/<session ID>.txt`) and read that file. Its first line, `# Transcript <session ID> (<title>)`, must name your session ID: if it doesn't, stop and say so instead of staging.

## 1. Read

- In the apprentice folder: `WIKI.md`, `Home.md`, and `APPRENTICE.md`.
- The lessons guide, `lessons.md` in the same folder as this file. It defines what to keep, the keep test, and where lessons go. Apply it strictly: staging is not a place to park borderline candidates.
- The staged file, if it exists. Then you are **updating** it: keep its candidates that still hold, revise any that later conversation changed, and add new ones. Never duplicate an entry. Look through the other files in the same `staged/` folder too, so you don't restage what another session already has. Use them only for that: they belong to other sessions (other agents may be writing them at the same moment), so never take a summary, candidate or "Not saved" item from them into yours. Everything in your file comes from your own transcript.

## 2. Extract

- Go through the session per the lessons guide. If you're updating a staged file, focus on the conversation since it was written, but correct earlier entries if the mentor has since contradicted them.
- For each surviving candidate, search the wiki (`grep -ril <keyword> <folder>`). Drop it if the wiki already says it. If it changes an existing lesson, stage it as an `update` naming the page and quoting the start of the old lesson, and write the **whole rewritten lesson**, about as long as the old one, never an "append: …" (see "Keep it small" in the lessons guide). End every candidate with its digest line: ` Digest: <the rule in at most ~150 characters>`.
- **Auto-memory:** run `$H inbox NAME --cwd <project>`. Treat each listed file as a candidate with the same filtering (auto memory saves liberally, so many won't pass). Skip files another staged file already lists.
- Never write a credential's value. For sensitive candidates (colleagues, confidential work, personal matters), mark them `⚠ sensitive`, suggest a `private/` target, and keep the detail to what the mentor needs in order to decide.

## 3. Write the staged file

Write the file even when nothing survived (it records that the session was processed), in this format:

```markdown
---
session: <session ID>
project: <project root>
staged: <YYYY-MM-DD>
summary: <one short clause describing the work, e.g. "added auto/manual learning modes">
---

## Candidates
- `preferences/coding-style.md` (new): <lesson in WIKI.md format: rule. *Why:* reason. (date, project)>
- `projects/<name>.md` (new page): <lesson>
- `tools/github.md` (update: "Minimize API calls…"): <revised lesson>
- ⚠ sensitive `private/domain/people.md` (new): <lesson>

## Skill candidates
- <procedure name>: <one line on what it covers and why it recurs>

## Auto-memory
- `<absolute path>`: folded into candidate 2 | dropped (<why>)

## Not saved
- <one-line borderline items the mentor might want to rescue>

## Questions
- <at most two things you noticed but couldn't interpret>
```

Leave out any section that would be empty, except `## Candidates` (keep the heading even with nothing under it). Each candidate is exactly one `- ` bullet: the review counts them.

If you can't write the file (e.g. the write is denied), reply with `COULD NOT WRITE` followed by the full file content, so the main session can write it.

## 4. Reply

Reply with one line and nothing else, e.g. `Staged 2 lessons for review (1 new since last time).` or `Nothing worth staging.` Don't list the lessons: the mentor will see them in `/aipprentice:review`.
