"""Every file to attach in Confluence for go-live, in one folder per page, with an optional upload.

  python3 scripts/upload_kit.py            # gather the files into release/go-live/files/<Confluence page title>/
  python3 scripts/upload_kit.py --upload   # attach them to the CRH pages (asks for your Confluence token)
  python3 scripts/upload_kit.py --upload "Partner templates" "Partner logos"   # only those pages' folders

Each page folder has "approved" (downloads, which get the approved label) and "no label" (pictures the
theme shows on the page). The files come from the local map that local test mode uses
(dev/brandbank-map.json, not in Git) and from the pictures made in build/. Stand-in examples, the talk
bank, the Canto showcase (canto_sync.py publishes that) and the Events files (hidden for now) are left out.
Gathering replaces the files folder. Uploading never deletes, and skips a file already on its page at the same
size, so it is safe to run again; a changed file goes up as a new version.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
import getpass, json, os, shutil, sys, uuid

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / 'release' / 'go-live' / 'files'
SPACE = 'CRH'
SKIP = ('/ADMIN/', '/DEVELOPMENT/', '/LINKS/', '/_LEGACY', '/_REVIEW', '/.')
LIMIT = 100e6  # Confluence's usual attachment limit

def gather():
    spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
    routes = json.loads((ROOT / 'evidence' / 'interior-route-map.json').read_text())
    base, files = Path(spec['root']), []
    for page, patterns in spec['pages'].items():
        for pattern in patterns:
            files += [(page, p, p.name, 'approved') for p in sorted(base.glob(pattern))
                      if p.is_file() and not any(s in '/' + str(p.relative_to(base)) + '/' for s in SKIP)]
    # The SKAO slide deck and the six template versions; the other examples are stand-ins for local test mode.
    for ex in spec.get('examples', []):
        if ex.get('root') == 'master_deck_upload':
            files += [(ex['page'], p, ex['title'], 'approved') for p in sorted(Path(spec['master_deck_upload']).glob(ex['from']))[:1]]
    files += [('standard-template.html', p, p.name, 'no label') for p in sorted((ROOT / 'build' / 'deck').glob('deck-*.webp'))]
    files += [(page, ROOT / 'build' / 'site' / site / 'site-photo.jpg', 'site-photo.jpg', 'no label')
              for site, page in (('low', 'low-slides.html'), ('mid', 'mid-slides.html')) if (ROOT / 'build' / 'site' / site / 'site-photo.jpg').exists()]
    # A cover goes up only with the file it belongs to (same name, .jpg).
    names = {(page, Path(name).stem) for page, _, name, _ in files}
    files += [(d.name + '.html', p, p.name, 'no label') for d in sorted((ROOT / 'build' / 'covers').glob('*')) for p in sorted(d.glob('*.jpg'))
              if (d.name + '.html', p.stem) in names]
    if KIT.exists(): shutil.rmtree(KIT)
    big = []
    for page, src, name, label in files:
        # A colon in a file name shows as a slash in Finder and can trip uploads, so it becomes a hyphen.
        dest = KIT / routes[page]['source_title'] / label / name.replace(':', '-')
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest)
        if dest.stat().st_size > LIMIT: big.append(dest)
    for folder in sorted(KIT.iterdir()):
        counts = {label: len(list((folder / label).glob('*'))) for label in ('approved', 'no label') if (folder / label).is_dir()}
        print(f'{folder.name}: ' + ', '.join(f'{n} {label}' for label, n in counts.items()))
    total = sum(f.stat().st_size for f in KIT.rglob('*') if f.is_file())
    print(f'{len(files)} files, {total / 1e6:.0f} MB, in {KIT.relative_to(ROOT)}')
    for f in big: print(f'Over 100 MB, may be too big for Confluence: {f.relative_to(KIT)}')

def upload():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from canto_sync import http
    if not KIT.exists(): sys.exit('Run python3 scripts/upload_kit.py first, to gather the files.')
    base = os.environ.get('CONFLUENCE_BASE', 'https://confluence.skatelescope.org').rstrip('/')
    # Asked for here, so the token never sits in the shell history (CONFLUENCE_TOKEN works too).
    token = os.environ.get('CONFLUENCE_TOKEN') or getpass.getpass('Confluence personal access token (it will not show): ').strip() or sys.exit('No token given.')
    head = {'Authorization': f'Bearer {token}', 'X-Atlassian-Token': 'nocheck', 'Accept': 'application/json'}
    get = lambda path: json.loads(http('GET', base + path, head)[1])
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    done = failed = skipped = 0
    for folder in sorted(p for p in KIT.iterdir() if p.is_dir() and (not only or p.name in only)):
        found = get('/rest/api/content?' + urlencode({'spaceKey': SPACE, 'title': folder.name, 'type': 'page'})).get('results', [])
        if not found:
            print(f'No page called "{folder.name}" in {SPACE} yet. Create it, then run this again.'); continue
        page = found[0]['id']
        existing = {r['title']: r for r in get(f'/rest/api/content/{page}/child/attachment?limit=500').get('results', [])}
        for label in ('approved', 'no label'):
            for f in sorted((folder / label).glob('*')) if (folder / label).is_dir() else []:
                if not f.is_file() or f.name.startswith('.'): continue
                if (existing.get(f.name) or {}).get('extensions', {}).get('fileSize') == f.stat().st_size: skipped += 1; continue
                boundary = uuid.uuid4().hex
                body = b''.join([f'--{boundary}\r\nContent-Disposition: form-data; name="minorEdit"\r\n\r\ntrue\r\n'.encode(),
                                 f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{f.name}"\r\n'
                                 f'Content-Type: application/octet-stream\r\n\r\n'.encode(), f.read_bytes(), f'\r\n--{boundary}--\r\n'.encode()])
                path = f'/rest/api/content/{page}/child/attachment' + (f"/{existing[f.name]['id']}/data" if f.name in existing else '')
                try:
                    reply = json.loads(http('POST', base + path, {**head, 'Content-Type': f'multipart/form-data; boundary={boundary}'}, body)[1])
                    att = (reply.get('results') or [reply])[0]['id']
                    if label == 'approved':
                        http('POST', f'{base}/rest/api/content/{att}/label', {**head, 'Content-Type': 'application/json'},
                             json.dumps([{'prefix': 'global', 'name': 'approved'}]).encode())
                    done += 1; print(f'{folder.name}: {f.name}' + (' (approved)' if label == 'approved' else ''))
                except HTTPError as e:
                    failed += 1; print(f'{folder.name}: {f.name} FAILED ({e.code} {e.reason})')
    print(f'Uploaded {done} files' + (f', skipped {skipped} already there' if skipped else '') + (f', {failed} failed' if failed else ''))

if __name__ == '__main__':
    upload() if '--upload' in sys.argv else gather()
