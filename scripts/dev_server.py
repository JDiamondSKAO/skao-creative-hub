"""Local test mode: the built Hub in its Confluence mode, with a stand-in for Confluence.

Serves docs/ on http://127.0.0.1:8767 and answers the few Confluence REST calls
the theme makes (page search, attachments, the announcement label), using a
local fixtures file. Attachment downloads stream from the paths in that file.

  python3 scripts/dev_fixtures.py   # build dev/fixtures.json from your local map
  python3 scripts/dev_server.py [--no-approved] [--no-announcement]

--no-approved     no attachment carries the "approved" label (tests fallbacks)
--no-announcement no page carries the "announcement" label
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote, quote
import html as htmllib, json, mimetypes, re, sys

ROOT = Path(__file__).resolve().parents[1]
DOCS, DEV = ROOT / 'docs', ROOT / 'dev'
PORT = 8767
ARGS = set(sys.argv[1:])

ROUTES = json.loads((ROOT / 'evidence/interior-route-map.json').read_text())
PAGE_ID = {name: meta['id'] for name, meta in ROUTES.items()}
FILE_OF = {meta['id']: name for name, meta in ROUTES.items()}
INDEX = {r['href']: r for r in json.loads((DOCS / 'search-index.json').read_text())}
FIXTURES = json.loads((DEV / 'fixtures.json').read_text()) if (DEV / 'fixtures.json').exists() else {'attachments': [], 'announcement': None}

def page_ref(name):
    meta = ROUTES.get(name, {})
    return {'id': meta.get('id', ''), 'title': meta.get('display_title', name), 'type': 'page', '_links': {'webui': '/' + name}}

def attachments(approved_only):
    rows = []
    for i, a in enumerate(FIXTURES['attachments']):
        if approved_only and ('approved' not in a.get('labels', []) or '--no-approved' in ARGS): continue
        pid = PAGE_ID.get(a['page'])
        if not pid: continue
        rows.append({'id': f'att{i}', 'type': 'attachment', 'title': a['title'], 'container': page_ref(a['page']),
                     'version': {'number': 1, 'when': a['when']}, 'extensions': {'fileSize': a['size']},
                     '_links': {'download': f'/download/attachments/{pid}/{quote(a["title"])}', 'webui': '/' + a['page']}, '_when': a['when']})
    return rows

def search(cql, limit):
    if 'type=attachment' in cql:
        rows = attachments('label="approved"' in cql)
        wanted = re.search(r'title="((?:[^"\\]|\\.)*)"', cql)
        if wanted: rows = [r for r in rows if r['title'] == wanted.group(1)]
        rows.sort(key=lambda r: r['title'].lower()) if 'ORDER BY title' in cql else rows.sort(key=lambda r: r['_when'], reverse=True)
        return rows[:limit]
    if 'label="announcement"' in cql:
        ann = FIXTURES.get('announcement')
        if not ann or '--no-announcement' in ARGS: return []
        ref = page_ref(ann['page']); ref.update(title=ann['title'], version={'number': ann.get('version', 1)})
        return [ref]
    terms = [t.lower() for t in re.findall(r'(?:title|text)~"((?:[^"\\]|\\.)*)"', cql)]
    hits = []
    for name, r in INDEX.items():
        hay = (r['title'] + ' ' + r.get('keywords', '')).lower()
        if any(t and t in hay for t in terms):
            ref = page_ref(name); ref['title'] = r['title']
            ref['ancestors'] = [{'title': 'Creative Hub'}] + ([{'title': r['group']}] if r.get('group') else [])
            hits.append(ref)
    return hits[:limit]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(DOCS), **k)

    def log_message(self, fmt, *args):
        if '/rest/' in self.path or '/download/' in self.path: super().log_message(fmt, *args)

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/rest/api/content/search':
            q = parse_qs(url.query)
            return self.send_json({'results': search(q.get('cql', [''])[0], int(q.get('limit', ['25'])[0]))})
        m = re.fullmatch(r'/download/attachments/(\d+)/(.+)', url.path)
        if m:
            name, title = FILE_OF.get(m.group(1)), unquote(m.group(2))
            match = next((a for a in FIXTURES['attachments'] if a['page'] == name and a['title'] == title), None)
            path = Path(match['path']) if match else None
            if not path or not path.is_file(): return self.send_error(404)
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(title)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(path.stat().st_size))
            self.send_header('Content-Disposition', 'attachment; filename="%s"' % title.replace('"', ''))
            self.end_headers()
            with path.open('rb') as f:
                while chunk := f.read(1 << 20): self.wfile.write(chunk)
            return
        name = url.path.strip('/') or 'index.html'
        if name.endswith('.html') and (DOCS / name).is_file():
            html = (DOCS / name).read_text()
            html = html.replace('data-mode="preview"', f'data-mode="confluence" data-context="" data-page-id="{PAGE_ID.get(name, "")}"', 1)
            routes = ''.join(f'<a data-page-id="{m["id"]}" href="/{n}">{htmllib.escape(m["source_title"])}</a>' for n, m in ROUTES.items())
            html = html.replace('</body>', f'<div id="hubRoutes" hidden>{routes}</div></body>', 1)
            html = re.sub(r'<div class="wrap preview-note">.*?</div>', '<div class="wrap preview-note">Local test mode · Confluence is simulated; downloads come from your local brand bank.</div>', html, count=1)
            body = html.encode()
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(body)
            return
        return super().do_GET()

if __name__ == '__main__':
    n = len(FIXTURES['attachments'])
    print(f'Creative Hub local test mode on http://127.0.0.1:{PORT} ({n} attachments{", none approved" if "--no-approved" in ARGS else ""})', flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
