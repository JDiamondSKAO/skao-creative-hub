"""Move the Confluence pages the Hub no longer uses to the space's trash, so Confluence itself shows only what the Hub has.

  python3 scripts/confluence_cleanup.py           # list the pages that would go, and where their content is now
  python3 scripts/confluence_cleanup.py --apply   # move them to the trash (asks for your Confluence token)

Run scripts/confluence_text.py --apply first, since it moves the Hub's pages out from under old parents. A page that
still has a Hub page beneath it is kept. Pages go to the trash children first, and only pages that are current: a
space admin can restore any of them from Space tools > Content Tools > Trash until the trash is purged. This script
never purges the trash. The Events pages go too while the section is hidden on the Hub (21 October 2026: not approved
yet); to bring Events back, restore them from the trash first, so they keep the IDs the theme knows.
"""
from pathlib import Path
from urllib.error import HTTPError
import getpass, json, os, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from confluence_text import classify, BASE

def old_pages():
    from gethelp import MOVED, RETIRED
    routes = json.loads((ROOT / 'evidence' / 'interior-route-map.json').read_text())
    for name, kind in classify().items():
        if kind not in ('old', 'hidden'): continue
        now = 'Events, hidden on the Hub for now' if kind == 'hidden' else f'now part of {MOVED[name][1]}' if name in MOVED else 'retired'
        yield routes[name]['id'], routes[name]['source_title'], now

def show():
    rows = list(old_pages())
    print(f'{len(rows)} pages not on the Hub would go to the trash:')
    for _, title, now in rows: print(f'  {title} ({now})')
    print('Kept: every page the Hub uses and the space home page. Run with --apply to go ahead.')

def apply():
    from canto_sync import http
    base = (os.environ.get('CONFLUENCE_BASE') or BASE).rstrip('/')
    token = os.environ.get('CONFLUENCE_TOKEN') or getpass.getpass('Confluence personal access token (it will not show): ').strip() or sys.exit('No token given.')
    head = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    get = lambda path: json.loads(http('GET', base + path, head)[1])
    old = {pid: title for pid, title, _ in old_pages()}
    pending, gone, kept = dict(old), 0, 0
    for _ in range(5):  # children first, then their parents
        progress = False
        for pid, title in list(pending.items()):
            try:
                page = get(f'/rest/api/content/{pid}')  # current pages only, so a trashed page is never purged
            except HTTPError as e:
                if e.code != 404: raise
                print(f'{title}: already gone'); pending.pop(pid); continue
            if page.get('status') != 'current': pending.pop(pid); continue
            kids = get(f'/rest/api/content/{pid}/child/page?limit=200').get('results', [])
            others = [k['title'] for k in kids if k['id'] not in old]
            if others:
                print(f'{title}: kept, because {", ".join(others)} is still under it (run confluence_text.py --apply first)')
                pending.pop(pid); kept += 1; continue
            if any(k['id'] in pending for k in kids): continue  # its own old pages go first
            http('DELETE', f'{base}/rest/api/content/{pid}', {**head, 'X-Atlassian-Token': 'nocheck'})
            print(f'{title}: moved to the trash'); pending.pop(pid); gone += 1; progress = True
        if not pending or not progress: break
    print(f'{gone} pages moved to the trash' + (f', {kept} kept' if kept else '') +
          '. Restore any of them from Space tools > Content Tools > Trash; don\'t purge the trash for a few weeks.')

if __name__ == '__main__':
    apply() if '--apply' in sys.argv else show()
