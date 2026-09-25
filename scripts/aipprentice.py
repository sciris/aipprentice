#!/usr/bin/env python3
"""
aipprentice helper: activation, hook entry points, and utilities for the skills.

An apprentice is a folder (see template/WIKI.md). Apprentices are registered by
name and are only active in sessions where they were explicitly activated.

Usage:
    aipprentice.py list                                   # registered apprentices
    aipprentice.py activate NAME [--path DIR] [--session ID] [--mentor TEXT]
                                                          # register/create if needed, mark session active, print context
    aipprentice.py context NAME                           # print the context bundle without activating
    aipprentice.py pending NAME [--here]                  # sessions awaiting debrief (optionally only this project)
    aipprentice.py inbox NAME                             # this project's auto-memory entries not yet absorbed
    aipprentice.py absorbed NAME FILE ...                 # mark auto-memory files as absorbed into the wiki
    aipprentice.py done NAME SESSION_ID ...               # mark sessions as debriefed (or dismissed)
    aipprentice.py journal NAME TEXT                      # append to this month's journal page
    aipprentice.py condense PATH_OR_SESSION_ID            # print a transcript as compact dialogue
    aipprentice.py paths NAME                             # print locations
    aipprentice.py session-start | session-end            # hook entry points (read hook JSON on stdin)

Stdlib only; hooks must be fast and never fail loudly.
"""

import os
import re
import sys
import json
import shutil
import datetime
import subprocess
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home() / '.claude'))
PROJECTS_DIR = CLAUDE_DIR / 'projects'
STATE = Path(os.environ.get('AIPPRENTICE_HOME', CLAUDE_DIR / 'aipprentice'))
REGISTRY = STATE / 'registry.json'
ACTIVE = STATE / 'active.json'
SCRIPT = Path(__file__).resolve()
TEMPLATE = SCRIPT.parent.parent / 'template'

MIN_TURNS = int(os.environ.get('AIPPRENTICE_MIN_TURNS', 3)) # Sessions with fewer real user prompts aren't queued
MAX_PAGE_CHARS = 8000 # Cap on each page injected into context
ACTIVE_TTL_DAYS = 90 # Forget session activations older than this


# %% General helpers

def now():
    return datetime.datetime.now().isoformat(timespec='seconds')


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def read_stdin_json():
    try:
        return json.loads(sys.stdin.read() or '{}')
    except json.JSONDecodeError:
        return {}


def load_jsonl(path):
    rows = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def capped(text, n=MAX_PAGE_CHARS):
    text = text.strip()
    return text if len(text) <= n else text[:n] + '\n... (truncated; this page should be split or trimmed)'


def pop_opt(args, flag, default=None):
    """ Remove '--flag value' from args and return value """
    if flag in args:
        i = args.index(flag)
        val = args[i+1] if i+1 < len(args) else default
        del args[i:i+2]
        return val
    return default


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


def auto_memory_dir(cwd):
    return PROJECTS_DIR / project_key(project_root(cwd)) / 'memory'


def frontmatter(text):
    """ Minimal YAML-frontmatter reader: flat 'key: value' pairs only """
    out = {}
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ':' in line and not line.startswith(' '):
                k, v = line.split(':', 1)
                out[k.strip()] = v.split('#')[0].strip().strip('"\'')
    return out


# %% Apprentices

class Apprentice:

    def __init__(self, name, path):
        self.name = name
        self.path = Path(path).expanduser().resolve()
        self.state = self.path / '.state'
        self.pending_file = self.state / 'pending.jsonl'
        self.debriefed_file = self.state / 'debriefed.txt'
        self.absorbed_file = self.state / 'absorbed.txt'

    @classmethod
    def get(cls, name):
        reg = read_json(REGISTRY, {})
        if name not in reg:
            sys.exit(f'Unknown apprentice "{name}". Registered: {", ".join(reg) or "none"}. Activate with --path DIR to register or create it.')
        return cls(name, reg[name])

    def page(self, rel):
        p = self.path / rel
        return p.read_text() if p.exists() else ''

    def project_page(self, cwd):
        """ The projects/*.md page whose 'repo:' contains cwd, if any """
        root = Path(project_root(cwd)).resolve()
        best = None
        for p in sorted((self.path / 'projects').glob('*.md')):
            repo = frontmatter(p.read_text()).get('repo')
            if not repo:
                continue
            repo = Path(repo).expanduser().resolve()
            if root == repo or repo in root.parents:
                if best is None or len(str(repo)) > len(str(best[1])):
                    best = (p, repo)
        return best[0] if best else None

    def skills(self):
        out = []
        for p in sorted((self.path / 'skills').glob('*/SKILL.md')):
            fm = frontmatter(p.read_text())
            out.append((fm.get('name', p.parent.name), fm.get('description', ''), p))
        return out

    def debriefed(self):
        return set(self.debriefed_file.read_text().split()) if self.debriefed_file.exists() else set()

    def pending(self, cwd=None):
        done = self.debriefed()
        rows = {r['session_id']: r for r in load_jsonl(self.pending_file) if r.get('session_id') and r['session_id'] not in done}
        rows = list(rows.values())
        if cwd is not None:
            key = project_key(project_root(cwd))
            rows = [r for r in rows if project_key(project_root(r.get('cwd', ''))) == key]
        return sorted(rows, key=lambda r: r.get('ended', ''))

    def absorbed(self):
        return set(self.absorbed_file.read_text().splitlines()) if self.absorbed_file.exists() else set()

    def inbox(self, cwd):
        """ Auto-memory files for this project that haven't been absorbed (or changed since) """
        d = auto_memory_dir(cwd)
        seen = self.absorbed()
        return [p for p in sorted(d.glob('*.md')) if p.name != 'MEMORY.md' and f'{p}\t{int(p.stat().st_mtime)}' not in seen]

    def context(self, cwd, session=None):
        """ Everything the model needs on activation """
        L = [
            f'# aipprentice: "{self.name}" is active for this session',
            f'Folder: `{self.path}`. Helper: `python3 {SCRIPT}` (pass `{self.name}` as the apprentice name).' + (f' Session: `{session}`.' if session else ''),
            f'You are this apprentice. Its knowledge lives in the wiki in that folder, organized per `WIKI.md`. Read `WIKI.md` before creating or restructuring any page. Consult wiki pages when relevant to the task (Home.md lists them all). Use `/aipprentice:debrief` to capture lessons and `/aipprentice:reflect` to consolidate.',
            '', '## APPRENTICE.md', capped(self.page('APPRENTICE.md')) or '(missing)',
            '', '## Home.md', capped(self.page('Home.md')) or '(missing)',
        ]
        pp = self.project_page(cwd)
        if pp:
            L += ['', f'## Project page: {pp.relative_to(self.path)}', capped(pp.read_text())]
        else:
            L += ['', f'## Project page', f'None yet for `{project_root(cwd)}`. The debrief will create `projects/<name>.md` with `repo:` frontmatter if there is anything worth recording.']
        skills = self.skills()
        if skills:
            L += ['', '## Apprentice skills', 'These are your own procedures. When one applies, read its SKILL.md and follow it.']
            L += [f'- **{n}**: {d} (`{p}`)' for n, d, p in skills]
        notes = []
        pend = self.pending()
        if pend:
            here = len(self.pending(cwd))
            notes.append(f'{len(pend)} past session(s) ({here} from this project) have not been debriefed; suggest `/aipprentice:debrief backlog`.')
        inbox = self.inbox(cwd)
        if inbox:
            notes.append(f'{len(inbox)} auto-memory entr{"y" if len(inbox) == 1 else "ies"} for this project not yet folded into the wiki; the next debrief will absorb them.')
        if notes:
            L += ['', '## Housekeeping (mention briefly once, at a natural point; don\'t lead with it if the user has a task)'] + [f'- {n}' for n in notes]
        return '\n'.join(L)


def scaffold(name, path, mentor):
    """ Create a new apprentice folder from the template, never overwriting existing files """
    path.mkdir(parents=True, exist_ok=True)
    subs = {'{{name}}': name, '{{date}}': str(datetime.date.today()), '{{mentor}}': mentor or 'its mentor'}
    created = []
    for src in sorted(TEMPLATE.iterdir()):
        dst = path / src.name
        if dst.exists():
            continue
        text = src.read_text()
        for k, v in subs.items():
            text = text.replace(k, v)
        dst.write_text(text)
        created.append(src.name)
    return created


# %% Commands

def cmd_list(args):
    reg = read_json(REGISTRY, {})
    if not reg:
        print('No apprentices registered.')
    for name, path in reg.items():
        ok = (Path(path) / 'APPRENTICE.md').exists()
        print(f'{name}\t{path}' + ('' if ok else '\t(MISSING)'))


def cmd_activate(args):
    path = pop_opt(args, '--path')
    session = pop_opt(args, '--session')
    mentor = pop_opt(args, '--mentor')
    if not args:
        sys.exit('Usage: activate NAME [--path DIR] [--session ID] [--mentor TEXT]')
    name = args[0]
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
        sys.exit(f'Apprentice names must be lowercase-kebab-case: "{name}"')
    reg = read_json(REGISTRY, {})

    if path is None:
        if name not in reg:
            print(f'UNKNOWN: no apprentice named "{name}". Ask the user for its folder (existing apprentice or where to create a new one), then rerun with --path.')
            sys.exit(2)
        path = reg[name]
    folder = Path(path).expanduser().resolve()
    if (folder / 'APPRENTICE.md').exists():
        fm_name = frontmatter((folder / 'APPRENTICE.md').read_text()).get('name')
        if fm_name and fm_name != name:
            print(f'NOTE: folder says its name is "{fm_name}"; registering it as "{name}".')
    else:
        created = scaffold(name, folder, mentor)
        print(f'CREATED: new apprentice "{name}" at {folder} ({", ".join(created)}).')
    if reg.get(name) != str(folder):
        reg[name] = str(folder)
        write_json(REGISTRY, reg)

    if session and not session.startswith('${'):
        active = read_json(ACTIVE, {})
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=ACTIVE_TTL_DAYS)).isoformat()
        active = {k: v for k, v in active.items() if v.get('activated', '') > cutoff}
        active[session] = dict(name=name, activated=now())
        write_json(ACTIVE, active)
    else:
        print('WARNING: no session ID given; hooks will not queue this session or re-inject after compaction.')
    print(Apprentice(name, folder).context(os.getcwd(), session))


def cmd_context(args):
    print(Apprentice.get(args[0]).context(os.getcwd()))


def cmd_pending(args):
    here = '--here' in args
    a = Apprentice.get([x for x in args if not x.startswith('--')][0])
    rows = a.pending(os.getcwd() if here else None)
    if not rows:
        print('No sessions awaiting debrief.')
    for r in rows:
        p = Path(r['transcript_path'])
        title = title_of(p) if p.exists() else '(transcript missing)'
        print(f"{r['session_id']}  {r.get('ended', '')}  prompts={r.get('prompts')}  cwd={r.get('cwd')}  title={title}")


def cmd_inbox(args):
    a = Apprentice.get(args[0])
    items = a.inbox(os.getcwd())
    print(f'Auto-memory dir: {auto_memory_dir(os.getcwd())}')
    print('\n'.join(str(p) for p in items) if items else 'Inbox empty.')


def cmd_absorbed(args):
    a = Apprentice.get(args[0])
    a.state.mkdir(parents=True, exist_ok=True)
    with open(a.absorbed_file, 'a') as f:
        for fn in args[1:]:
            p = Path(fn).expanduser().resolve()
            if p.exists():
                f.write(f'{p}\t{int(p.stat().st_mtime)}\n')
    print(f'Marked {len(args) - 1} file(s) absorbed.')


def cmd_done(args):
    a = Apprentice.get(args[0])
    a.state.mkdir(parents=True, exist_ok=True)
    with open(a.debriefed_file, 'a') as f:
        for sid in args[1:]:
            f.write(sid + '\n')
    done = a.debriefed()
    remaining = [r for r in load_jsonl(a.pending_file) if r.get('session_id') not in done]
    a.pending_file.write_text(''.join(json.dumps(r) + '\n' for r in remaining))
    print(f'Marked {len(args) - 1} session(s) debriefed; {len(a.pending())} still pending.')


def cmd_journal(args):
    a = Apprentice.get(args[0])
    today = datetime.date.today()
    page = a.path / 'journal' / f'{today:%Y-%m}.md'
    page.parent.mkdir(parents=True, exist_ok=True)
    if not page.exists():
        page.write_text(f'# Journal {today:%Y-%m}\n\n')
    with open(page, 'a') as f:
        f.write(f'- {today} ({Path(project_root(os.getcwd())).name}): {" ".join(args[1:])}\n')


def cmd_paths(args):
    a = Apprentice.get(args[0])
    cwd = os.getcwd()
    pp = a.project_page(cwd)
    print(f'apprentice:    {a.path}')
    print(f'project_page:  {pp or "(none yet)"}')
    print(f'auto_memory:   {auto_memory_dir(cwd)}')
    print(f'projects_dir:  {PROJECTS_DIR}')
    print(f'template:      {TEMPLATE}')


# %% Transcripts

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


def title_of(path):
    title = None
    for rec in iter_records(path):
        if rec.get('type') == 'ai-title':
            title = rec.get('aiTitle')
    return title


def find_transcript(ref):
    p = Path(ref).expanduser()
    if p.exists():
        return p
    matches = list(PROJECTS_DIR.glob(f'*/{ref}.jsonl'))
    return matches[0] if matches else None


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n] + '…'


def cmd_condense(args):
    """ Render a transcript as dialogue: full user prompts, assistant prose, one-line tool calls, tool errors only """
    max_msg = int(pop_opt(args, '--max-msg', 3000))
    if not args:
        sys.exit('Usage: condense PATH_OR_SESSION_ID [--max-msg N]')
    path = find_transcript(args[0])
    if path is None:
        sys.exit(f'Transcript not found: {args[0]}')
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


# %% Hooks: silent unless the session activated an apprentice

def active_apprentice(session_id):
    entry = read_json(ACTIVE, {}).get(session_id or '')
    if not entry:
        return None
    path = read_json(REGISTRY, {}).get(entry['name'])
    return Apprentice(entry['name'], path) if path and Path(path).exists() else None


def session_start():
    data = read_stdin_json()
    how = data.get('source') or data.get('how') # Field name differs across Claude Code versions
    if how not in ('resume', 'compact'): # Fresh sessions start inactive
        return
    a = active_apprentice(data.get('session_id'))
    if a:
        print(a.context(data.get('cwd') or os.getcwd(), data.get('session_id')))


def session_end():
    data = read_stdin_json()
    sid, path = data.get('session_id'), data.get('transcript_path')
    a = active_apprentice(sid)
    if not a or not path or sid in a.debriefed():
        return
    n = sum(is_real_prompt(r) for r in iter_records(path))
    if n < MIN_TURNS:
        return
    a.state.mkdir(parents=True, exist_ok=True)
    row = dict(session_id=sid, transcript_path=path, cwd=data.get('cwd', ''), ended=now(), reason=data.get('reason') or data.get('why') or '', prompts=n)
    with open(a.pending_file, 'a') as f:
        f.write(json.dumps(row) + '\n')


COMMANDS = {
    'list': cmd_list,
    'activate': cmd_activate,
    'context': cmd_context,
    'pending': cmd_pending,
    'inbox': cmd_inbox,
    'absorbed': cmd_absorbed,
    'done': cmd_done,
    'journal': cmd_journal,
    'condense': cmd_condense,
    'paths': cmd_paths,
    'session-start': lambda a: session_start(),
    'session-end': lambda a: session_end(),
}


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd not in ('list', 'condense', 'session-start', 'session-end') and not [a for a in args if not a.startswith('--')]:
        sys.exit(__doc__)
    try:
        COMMANDS[cmd](args)
    except Exception as e:
        if cmd.startswith('session-'): # Never break the user's session over a hook failure
            print(f'aipprentice hook error: {e}', file=sys.stderr)
            sys.exit(0)
        raise
