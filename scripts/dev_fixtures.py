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
for page, patterns in spec['pages'].items():
    for pattern in patterns:
        found = sorted(p for p in base.glob(pattern) if p.is_file() and not any(s in '/' + str(p.relative_to(base)) + '/' for s in SKIP))
        if not found: missing.append(f'{page}: {pattern}')
        for p in found:
            st = p.stat()
            out.append({'page': page, 'title': p.name, 'path': str(p), 'size': st.st_size, 'labels': ['approved'],
                        'when': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()})
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
    portal = stand.get('link', 'https://skao.canto.global/v/SKAOLibrary')
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
