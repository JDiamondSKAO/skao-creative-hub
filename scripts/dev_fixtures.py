"""Build dev/fixtures.json for local test mode from dev/brandbank-map.json.

The map (kept out of Git) names a root folder and, for each Hub page, glob
patterns of final files to treat as attachments labelled "approved":

  {"root": "/path/to/brand/bank",
   "announcement": {"page": "updates.html", "title": "..."},
   "pages": {"standard-template.html": ["TEMPLATES/*.pptx"]}}
"""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / 'dev'
SKIP = ('/ADMIN/', '/DEVELOPMENT/', '/LINKS/', '/_LEGACY', '/_REVIEW', '/.')

spec = json.loads((DEV / 'brandbank-map.json').read_text())
base = Path(spec['root'])
out, missing = [], []
# Example files under their own names, for site progress and the approved decks:
# {"page": "low-slides.html", "title": "2026-10 SKA-Low progress.pptx", "from": "glob of any stand-in file"}.
# "root" names another folder in the map to look in (the talk bank), "labels" adds labels such as
# "approved", "comment" is the attachment comment (the deck's details on Approved slide decks), and
# "cover" attaches a cover made by scripts/cover_images.py.
# The date at the start of the title becomes the upload date, so the newest example sorts first.
for ex in spec.get('examples', []):
    found = sorted(p for p in Path(spec[ex.get('root', 'root')]).glob(ex['from']) if p.is_file())
    if not found: missing.append(f"{ex['page']}: {ex['from']}"); continue
    import re as _re
    d = _re.match(r'(\d{4})-(\d{2})', ex['title'])
    when = datetime(int(d[1]), int(d[2]), 15, tzinfo=timezone.utc).isoformat() if d else datetime.now(timezone.utc).isoformat()
    out.append({'page': ex['page'], 'title': ex['title'], 'path': str(found[0]), 'size': found[0].stat().st_size, 'labels': ex.get('labels', []), 'when': when,
                **({'comment': ex['comment']} if ex.get('comment') else {})})
# Covers from scripts/cover_images.py: a picture under a deck's own name, unlabelled, on the deck's page.
for folder in sorted((ROOT / 'build' / 'covers').glob('*')):
    for f in sorted(folder.glob('*.jpg')):
        out.append({'page': folder.name + '.html', 'title': f.name, 'path': str(f), 'size': f.stat().st_size, 'labels': [], 'when': '2026-01-01T00:00:00+00:00'})
for page, patterns in spec['pages'].items():
    for pattern in patterns:
        found = sorted(p for p in base.glob(pattern) if p.is_file() and not any(s in '/' + str(p.relative_to(base)) + '/' for s in SKIP))
        if not found: missing.append(f'{page}: {pattern}')
        for p in found:
            st = p.stat()
            out.append({'page': page, 'title': p.name, 'path': str(p), 'size': st.st_size, 'labels': ['approved'],
                        'when': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()})
# Event kit pictures from scripts/kit_images.py (no label: the theme shows them, not the downloads),
# and the Events Production Manual as an approved download, both on Exhibition kit.
for f in sorted((ROOT / 'build' / 'kit').glob('kit-*.webp')):
    out.append({'page': 'stands.html', 'title': f.name, 'path': str(f), 'size': f.stat().st_size, 'labels': [],
                'when': datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat()})
# Print and giveaway files from scripts/event_files.py: each download is approved; its cover (same name,
# .webp) has no label, so the page shows it on the card rather than as a download.
for f in sorted((ROOT / 'build' / 'event-files').glob('*')):
    out.append({'page': 'merchandise.html', 'title': f.name, 'path': str(f), 'size': f.stat().st_size,
                'labels': [] if f.suffix == '.webp' else ['approved'], 'when': datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat()})
if spec.get('events_guide'):
    for f in sorted(Path(spec['events_guide']).glob('FINALS/BROCHURE/*.pdf')):
        out.append({'page': 'stands.html', 'title': f.name, 'path': str(f), 'size': f.stat().st_size, 'labels': ['approved'],
                    'when': datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat()})
# Telescope photos from scripts/site_images.py, attached to each site page as site-photo.jpg.
for site, page in [('low', 'low-slides.html'), ('mid', 'mid-slides.html')]:
    f = ROOT / 'build' / 'site' / site / 'site-photo.jpg'
    if f.exists():
        out.append({'page': page, 'title': f.name, 'path': str(f), 'size': f.stat().st_size, 'labels': [], 'when': '2026-01-01T00:00:00+00:00'})
# Canto showcase: real dry-run output from scripts/canto_sync.py if present, otherwise stand-ins.
real = ROOT / 'build' / 'canto' / 'canto-showcase.json'
stand = spec.get('canto_standin')
if real.exists():
    manifest = json.loads(real.read_text())
    page = (stand or {}).get('page', 'media.html')
    thumbs = {i['thumb'] for al in manifest['albums'] for i in al['assets']} | {i['thumb'] for i in manifest.get('highlights', [])}
    for name in sorted(thumbs):
        f = real.parent / name
        if f.exists(): out.append({'page': page, 'title': name, 'path': str(f), 'size': f.stat().st_size, 'labels': [], 'when': manifest['generated']})
    out.append({'page': page, 'title': real.name, 'path': str(real), 'size': real.stat().st_size, 'labels': [], 'when': manifest['generated']})
    print(f'Canto: {len(thumbs)} real images ({len(manifest.get("highlights", []))} highlights) in {len(manifest["albums"])} collections from build/canto')
    stand = None
if stand:
    import sys; sys.path.insert(0, str(ROOT / 'scripts'))
    import canto_sync
    routes = json.loads((ROOT / 'evidence/interior-route-map.json').read_text())
    page = stand['page']; page_id = routes[page]['id']; out_dir = DEV / 'canto'; out_dir.mkdir(exist_ok=True)
    albums, sources = [], {}
    for i, (name, pattern) in enumerate(stand['albums'].items()):
        imgs = sorted(p for p in Path(stand['root']).glob(pattern) if p.is_file() and p.suffix.lower() in ('.jpg', '.jpeg', '.png') and '/.' not in str(p))[:stand.get('per_album', 10)]
        album = {'id': f'standin{i}', 'name': name, 'namePath': f'Library/Staff media library/Asset library - Staff/{name}', 'assetCount': len(imgs)}
        assets = []
        for j, p in enumerate(imgs):
            aid = f'standin{i}x{j}'; sources[aid] = p
            assets.append({'id': aid, 'name': p.name, 'scheme': 'image', 'copyright': ''})
        albums.append((album, assets))
    portal = stand.get('link', 'https://skao.canto.global/v/SKAOStaff')
    manifest = canto_sync.build_manifest(albums, 'skao', page_id, 'Staff media library', asset_url=portal, album_url=portal)
    for al in manifest['albums']:
        for item in al['assets']:
            thumb = out_dir / item['thumb']
            if not thumb.exists():
                thumb.write_bytes(canto_sync.make_thumb(sources[item['id']].read_bytes(), 640))
            from PIL import Image
            with Image.open(thumb) as im: item['width'], item['height'] = im.size
            out.append({'page': page, 'title': item['thumb'], 'path': str(thumb), 'size': thumb.stat().st_size, 'labels': [], 'when': manifest['generated']})
    (out_dir / canto_sync.MANIFEST).write_text(json.dumps(manifest, indent=1))
    out.append({'page': page, 'title': canto_sync.MANIFEST, 'path': str(out_dir / canto_sync.MANIFEST), 'size': (out_dir / canto_sync.MANIFEST).stat().st_size, 'labels': [], 'when': manifest['generated']})
    print(f'Canto stand-in: {sum(len(a["assets"]) for a in manifest["albums"])} images in {len(manifest["albums"])} albums')
(DEV / 'fixtures.json').write_text(json.dumps({'attachments': out, 'announcement': spec.get('announcement')}, indent=1))
pages = len({a['page'] for a in out})
print(f'{len(out)} files on {pages} pages, {sum(a["size"] for a in out) / 1e6:.0f} MB')
for m in missing: print('no match:', m)
