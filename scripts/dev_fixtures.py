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
(DEV / 'fixtures.json').write_text(json.dumps({'attachments': out, 'announcement': spec.get('announcement')}, indent=1))
pages = len({a['page'] for a in out})
print(f'{len(out)} files on {pages} pages, {sum(a["size"] for a in out) / 1e6:.0f} MB')
for m in missing: print('no match:', m)
