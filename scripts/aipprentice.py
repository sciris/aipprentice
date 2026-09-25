#!/usr/bin/env python3
"""
aipprentice helper: hook entry points and utilities for the debrief/reflect skills.

Usage:
    aipprentice.py session-start          # SessionStart hook: prints context to inject
    aipprentice.py session-end            # SessionEnd hook: queues substantive sessions for debrief
    aipprentice.py pending [--all]        # list sessions awaiting debrief (this project, or all)
    aipprentice.py condense PATH_OR_ID    # print a transcript as compact user/assistant dialogue
    aipprentice.py done SESSION_ID ...    # mark sessions as debriefed (or dismissed)
    aipprentice.py journal TEXT           # append a line to the work journal
    aipprentice.py paths                  # print knowledge-base locations for this project

Stdlib only; hooks must be fast and never fail loudly.
"""

import os
import re
import sys
import json
import datetime
import subprocess
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))
PROJECTS_DIR = CLAUDE_DIR / 'projects'
STORE = Path(os.environ.get('AIPPRENTICE_HOME', CLAUDE_DIR / 'aipprentice'))
GLOBAL_MEM = STORE / 'memory'
PENDING = STORE / 'pending.jsonl'
DEBRIEFED = STORE / 'debriefed.txt'
JOURNAL = STORE / 'journal.md'
SCRIPT = Path(__file__).resolve()

MIN_TURNS = int(os.environ.get('AIPPRENTICE_MIN_TURNS', 3)) # Sessions with fewer real user prompts aren't queued
MAX_INDEX_CHARS = 8000 # Cap on how much of the global index is injected at session start


def now():
    return datetime.datetime.now().isoformat(timespec='seconds')


def read_stdin_json():
    try:
        return json.loads(sys.stdin.read() or '{}')
    except json.JSONDecodeError:
        return {}


def project_root(cwd):
    """ Git toplevel if available (matches how auto memory keys projects), else cwd """
    try:
        out = subprocess.run(['git', '-C', cwd, 'rev-parse', '--show-toplevel'], capture_output=True, text=True, timeout=2)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return cwd


def project_key(path):
    return re.sub(r'[^A-Za-z0-9]', '-', path)


def project_memory_dir(cwd):
    return PROJECTS_DIR / project_key(project_root(cwd)) / 'memory'


def load_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def debriefed_ids():
    return set(DEBRIEFED.read_text().split()) if DEBRIEFED.exists() else set()


def pending_sessions(cwd=None):
    """ Pending sessions, deduplicated, minus any already debriefed, optionally filtered to one project """
    done = debriefed_ids()
    seen = {}
    for row in load_jsonl(PENDING):
        sid = row.get('session_id')
        if sid and sid not in done:
            seen[sid] = row
    rows = list(seen.values())
    if cwd is not None:
        key = project_key(project_root(cwd))
        rows = [r for r in rows if project_key(project_root(r.get('cwd', ''))) == key]
    return rows


def is_real_prompt(rec):
    """ True for a prompt the human actually typed (not tool results, meta messages, or subagent traffic) """
    if rec.get('type') != 'user' or rec.get('isMeta') or rec.get('isSidechain'):
        return False
    content = rec.get('message', {}).get('content')
    if isinstance(content, str):
        return not content.startswith('<local-command')
    if isinstance(content, list):
        return any(b.get('type') == 'text' for b in content) and not any(b.get('type') == 'tool_result' for b in content)
    return False


def iter_records(path):
    with open(path, errors='replace') as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def count_prompts(path):
    try:
        return sum(is_real_prompt(r) for r in iter_records(path))
    except OSError:
        return 0


def find_transcript(ref):
    """ Accept a transcript path or a bare session ID """
    p = Path(ref).expanduser()
    if p.exists():
        return p
    matches = list(PROJECTS_DIR.glob(f'*/{ref}.jsonl'))
    return matches[0] if matches else None


# %% Hook entry points

def session_start():
    data = read_stdin_json()
    cwd = data.get('cwd') or os.getcwd()
    source = data.get('source', 'startup')
    GLOBAL_MEM.mkdir(parents=True, exist_ok=True)

    lines = [
        '# aipprentice',
        'You are working as an apprentice to this user: someone who learns their preferences, conventions, and domain over time, the way a good trainee employee would. The global knowledge base below holds lessons that apply across all projects; the per-project auto memory holds lessons for this project. Apply both. When a lesson looks outdated or conflicts with what the user says now, the user wins; flag the stale lesson so it can be fixed at the next debrief.',
        f'Global knowledge base: `{GLOBAL_MEM}` (index below; read individual files when relevant). Helper script: `python3 {SCRIPT}`.',
    ]

    index = GLOBAL_MEM / 'MEMORY.md'
    if index.exists() and index.read_text().strip():
        text = index.read_text().strip()
        if len(text) > MAX_INDEX_CHARS:
            text = text[:MAX_INDEX_CHARS] + '\n... (index truncated; run /aipprentice:reflect to consolidate)'
        lines += ['', '## Global knowledge index', text]
    else:
        lines += ['', '(Global knowledge base is empty so far.)']

    if source == 'startup': # Don't nag on resume/clear/compact
        here = pending_sessions(cwd)
        total = pending_sessions()
        if total:
            where = f'{len(here)} from this project, ' if here else ''
            lines += ['', f'Note for the user: {len(total)} past session(s) ({where}{len(total)} total) have not been debriefed. Mention this briefly once, at a natural point (not as your first words if the user has a task), suggesting `/aipprentice:debrief backlog`.']

    print('\n'.join(lines))


def session_end():
    data = read_stdin_json()
    sid = data.get('session_id')
    path = data.get('transcript_path')
    if not sid or not path or sid in debriefed_ids():
        return
    n = count_prompts(path)
    if n < MIN_TURNS:
        return
    STORE.mkdir(parents=True, exist_ok=True)
    row = dict(session_id=sid, transcript_path=path, cwd=data.get('cwd', ''), ended=now(), reason=data.get('reason', ''), prompts=n)
    with open(PENDING, 'a') as f:
        f.write(json.dumps(row) + '\n')


# %% Utilities for the skills

def title_of(path):
    title = None
    for rec in iter_records(path):
        if rec.get('type') == 'ai-title':
            title = rec.get('aiTitle')
    return title


def cmd_pending(args):
    rows = pending_sessions(None if '--all' in args else os.getcwd())
    if not rows:
        print('No sessions awaiting debrief.')
        return
    for r in sorted(rows, key=lambda r: r.get('ended', '')):
        title = title_of(r['transcript_path']) if Path(r['transcript_path']).exists() else '(transcript missing)'
        print(f"{r['session_id']}  {r.get('ended', '')}  prompts={r.get('prompts')}  cwd={r.get('cwd')}  title={title}")


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n] + '…'


def cmd_condense(args):
    """ Render a transcript as dialogue: full user prompts, assistant prose, one-line tool calls, tool errors only """
    if not args:
        sys.exit('Usage: condense PATH_OR_SESSION_ID [--max-msg N]')
    path = find_transcript(args[0])
    if path is None:
        sys.exit(f'Transcript not found: {args[0]}')
    max_msg = int(args[args.index('--max-msg') + 1]) if '--max-msg' in args else 3000

    out = []
    for rec in iter_records(path):
        if rec.get('isSidechain') or rec.get('isMeta'):
            continue
        kind = rec.get('type')
        content = rec.get('message', {}).get('content') if isinstance(rec.get('message'), dict) else None
        if kind == 'user':
            if isinstance(content, str):
                if not content.startswith('<local-command'):
                    out.append(f'\n### USER\n{short(content, max_msg)}')
            elif isinstance(content, list):
                for b in content:
                    if b.get('type') == 'text':
                        out.append(f'\n### USER\n{short(b.get("text", ""), max_msg)}')
                    elif b.get('type') == 'tool_result' and b.get('is_error'):
                        body = b.get('content')
                        if isinstance(body, list):
                            body = ' '.join(x.get('text', '') for x in body if isinstance(x, dict))
                        out.append(f'  [tool error: {short(body, 300)}]')
        elif kind == 'assistant' and isinstance(content, list):
            for b in content:
                if b.get('type') == 'text' and b.get('text', '').strip():
                    out.append(f'\n### ASSISTANT\n{short(b["text"], max_msg)}')
                elif b.get('type') == 'tool_use':
                    inp = b.get('input', {})
                    arg = inp.get('description') or inp.get('file_path') or inp.get('command') or inp.get('pattern') or inp.get('skill') or ''
                    out.append(f'  [{b.get("name")}: {short(arg, 160)}]')
    print(f'# Transcript {path.stem} ({title_of(path) or "untitled"})')
    print('\n'.join(out))


def cmd_done(args):
    if not args:
        sys.exit('Usage: done SESSION_ID ...')
    STORE.mkdir(parents=True, exist_ok=True)
    with open(DEBRIEFED, 'a') as f:
        for sid in args:
            f.write(sid + '\n')
    remaining = [r for r in load_jsonl(PENDING) if r.get('session_id') not in debriefed_ids()]
    PENDING.write_text(''.join(json.dumps(r) + '\n' for r in remaining))
    print(f'Marked {len(args)} session(s) as debriefed; {len(pending_sessions())} still pending.')


def cmd_journal(args):
    if not args:
        sys.exit('Usage: journal TEXT')
    STORE.mkdir(parents=True, exist_ok=True)
    cwd = project_root(os.getcwd())
    with open(JOURNAL, 'a') as f:
        f.write(f'- {datetime.date.today()} `{Path(cwd).name}`: {" ".join(args)}\n')


def cmd_paths(args):
    cwd = os.getcwd()
    print(f'global_memory:  {GLOBAL_MEM}')
    print(f'project_memory: {project_memory_dir(cwd)}')
    print(f'journal:        {JOURNAL}')
    print(f'projects_dir:   {PROJECTS_DIR}')
    print(f'personal_skills: {CLAUDE_DIR / "skills"}')


COMMANDS = {
    'session-start': lambda a: session_start(),
    'session-end': lambda a: session_end(),
    'pending': cmd_pending,
    'condense': cmd_condense,
    'done': cmd_done,
    'journal': cmd_journal,
    'paths': cmd_paths,
}


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    try:
        COMMANDS[cmd](sys.argv[2:])
    except Exception as e:
        if cmd.startswith('session-'): # Never break the user's session over a hook failure
            print(f'aipprentice hook error: {e}', file=sys.stderr)
            sys.exit(0)
        raise
