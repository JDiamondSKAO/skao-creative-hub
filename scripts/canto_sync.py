"""Sync Canto's staff media folder to the Creative Hub.

Reads every album under a Canto folder path (default "Staff media library"),
takes each album's newest images, makes web-sized thumbnails and publishes them
with a small manifest (canto-showcase.json) as attachments on one Hub page.
The theme reads the manifest from Confluence, so staff browsers never need a
Canto token and never see an expiring Canto link.

Adapted from the Canto client in canto-metadata-assistant: bearer token or
OAuth client credentials, /album listing with namePath, /album/{id} contents,
url.directUrlPreview for renditions, and retry with backoff on 429 and 5xx.

Environment
  CANTO_DOMAIN        subdomain, e.g. "skao"
  CANTO_API_KEY       direct API token, or CANTO_APP_ID and CANTO_APP_SECRET
  CANTO_FOLDER_PATH   namePath prefix to publish (default "Staff media library")
  CANTO_ASSET_URL     click-through template, default https://{domain}.canto.global/asset/{id}
  CANTO_ALBUM_URL     album link template, default https://{domain}.canto.global/album/{id}
  CONFLUENCE_BASE     e.g. https://confluence.skatelescope.org
  CONFLUENCE_TOKEN    personal access token of the account that owns the sync
  CONFLUENCE_PAGE_ID  Hub page that holds the attachments

Usage
  python3 scripts/canto_sync.py --dry-run --out build/canto   # fetch from Canto, write files locally
  python3 scripts/canto_sync.py                               # fetch and publish to Confluence
  python3 scripts/canto_sync.py --self-test
Options: --per-album N (default 12), --width PX (default 640), --prune (remove stale canto-* thumbnails)
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
import io, json, os, re, sys, time, uuid

MANIFEST = 'canto-showcase.json'
THUMB_PREFIX = 'canto-'

def log(msg): print(msg, file=sys.stderr, flush=True)

class _DropAuthOnRedirect(HTTPRedirectHandler):
    """Like requests: never forward the Canto token to another host (Canto previews redirect to a CDN)."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urlsplit(newurl).hostname != urlsplit(req.full_url).hostname:
            new.headers.pop('Authorization', None); new.unredirected_hdrs.pop('Authorization', None)
        return new

_opener = build_opener(_DropAuthOnRedirect)

def http(method, url, headers=None, data=None, retries=4):
    """HTTP with retry and backoff on 429 and 5xx, honouring Retry-After."""
    for attempt in range(retries + 1):
        try:
            with _opener.open(Request(url, data=data, headers=headers or {}, method=method), timeout=60) as r:
                return r.status, r.read(), dict(r.headers)
        except HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = float(e.headers.get('Retry-After') or 2 ** attempt)
                log(f'  {e.code} from {url.split("?")[0]}; retrying in {wait:.0f}s'); time.sleep(min(wait, 60)); continue
            raise
        except URLError:
            if attempt < retries: time.sleep(2 ** attempt); continue
            raise

# ---------- Canto ----------

class Canto:
    def __init__(self, domain, api_key=None, app_id=None, app_secret=None):
        self.domain, self.base = domain, f'https://{domain}.canto.global/api/v1'
        self.token, self.expires = api_key, 0 if api_key else -1
        self.app_id, self.app_secret = app_id, app_secret

    def _auth(self):
        if self.token and (self.expires == 0 or time.time() < self.expires): return
        body = urlencode({'grant_type': 'client_credentials', 'client_id': self.app_id, 'client_secret': self.app_secret}).encode()
        _, raw, _ = http('POST', f'https://{self.domain}.canto.global/oauth/api/oauth2/token', {'Content-Type': 'application/x-www-form-urlencoded'}, body)
        data = json.loads(raw)
        self.token, self.expires = data['access_token'], time.time() + int(data.get('expires_in', 3600)) - 60

    def get(self, path, **params):
        self._auth()
        _, raw, _ = http('GET', f'{self.base}{path}?{urlencode(params)}', {'Authorization': f'Bearer {self.token}', 'Accept': 'application/json'})
        return json.loads(raw or b'{}')

    def albums(self):
        return self.get('/album', limit=1000, sortBy='name', sortDirection='ascending').get('results', [])

    def album_assets(self, album_id, limit):
        return self.get(f'/album/{album_id}', limit=limit, start=0, sortBy='time', sortDirection='descending').get('results', [])

    def preview_bytes(self, asset):
        url = (asset.get('url') or {}).get('directUrlPreview') or (asset.get('url') or {}).get('preview')
        if not url: return None
        self._auth()
        _, raw, _ = http('GET', url, {'Authorization': f'Bearer {self.token}'})
        return raw

# ---------- Selection and manifest (pure, covered by --self-test) ----------

def norm(path): return '/'.join(p.strip().lower() for p in str(path or '').split('/') if p.strip())

def select_albums(albums, folder_path):
    """Albums at or below the folder path that contain assets."""
    prefix = norm(folder_path)
    picked = []
    for a in albums:
        path = norm(a.get('namePath') or a.get('name'))
        segments = path.split('/')
        # namePath may or may not start at the library root, so match the folder anywhere in the path.
        if any('/'.join(segments[i:i + len(prefix.split('/'))]) == prefix for i in range(len(segments))) and (a.get('assetCount') is None or int(a['assetCount']) > 0):
            picked.append(a)
    return picked

def display_path(name_path, folder_path):
    """Album path below the published folder, e.g. "Telescopes / SKA-Low"."""
    parts = [p.strip() for p in str(name_path or '').split('/') if p.strip()]
    low = [p.lower() for p in parts]
    fp = [p.strip().lower() for p in folder_path.split('/') if p.strip()]
    for i in range(len(low)):
        if low[i:i + len(fp)] == fp: parts = parts[i + len(fp):]; break
    return ' / '.join(parts)

def tidy_title(asset):
    name = asset.get('title') or asset.get('name') or ''
    name = re.sub(r'\.[A-Za-z0-9]{2,5}$', '', str(name))
    return re.sub(r'\s+', ' ', re.sub(r'[_]+', ' ', name)).strip() or 'Untitled'

def is_image(asset):
    return str(asset.get('scheme', 'image')).lower() == 'image'

def build_manifest(albums, domain, page_id, folder_path, asset_url=None, album_url=None, generated=None):
    """albums: [(album, [assets])]. Returns the manifest the theme reads."""
    asset_url = asset_url or 'https://{domain}.canto.global/asset/{id}'
    album_url = album_url or 'https://{domain}.canto.global/album/{id}'
    out = {'version': 1, 'generated': generated or datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'source': f'Canto: {folder_path}', 'albums': []}
    for album, assets in albums:
        items = []
        for a in assets:
            if not is_image(a) or not a.get('id'): continue
            thumb = f'{THUMB_PREFIX}{re.sub(r"[^A-Za-z0-9_-]", "", str(a["id"]))}.jpg'
            items.append({'id': str(a['id']), 'title': tidy_title(a), 'credit': str(a.get('copyright') or '').strip(),
                          'width': a.get('width'), 'height': a.get('height'), 'thumb': thumb,
                          'src': f'/download/attachments/{page_id}/{quote(thumb)}',
                          'href': asset_url.format(domain=domain, id=a['id'])})
        if items:
            out['albums'].append({'id': str(album.get('id')), 'name': album.get('name') or 'Album',
                                  'path': display_path(album.get('namePath'), folder_path) or album.get('name') or 'Album',
                                  'count': int(album.get('assetCount') or len(items)),
                                  'href': album_url.format(domain=domain, id=album.get('id')), 'assets': items})
    return out

def make_thumb(raw, width):
    """Resize to web width and drop embedded metadata (including any location data)."""
    try:
        from PIL import Image
    except ImportError:
        return raw
    im = Image.open(io.BytesIO(raw))
    im = im.convert('RGB')
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=82, optimize=True, progressive=True)
    return buf.getvalue()

# ---------- Confluence ----------

class Confluence:
    def __init__(self, base, token, page_id):
        self.base, self.page = base.rstrip('/'), str(page_id)
        self.headers = {'Authorization': f'Bearer {token}', 'X-Atlassian-Token': 'nocheck', 'Accept': 'application/json'}

    def attachments(self):
        found, start = {}, 0
        while True:
            _, raw, _ = http('GET', f'{self.base}/rest/api/content/{self.page}/child/attachment?limit=200&start={start}', self.headers)
            data = json.loads(raw)
            for r in data.get('results', []): found[r['title']] = r['id']
            if data.get('size', 0) < 200: return found
            start += 200

    def upload(self, name, body, content_type, existing):
        boundary = uuid.uuid4().hex
        parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="minorEdit"\r\n\r\ntrue\r\n'.encode(),
                 f'--{boundary}\r\nContent-Disposition: form-data; name="comment"\r\n\r\nPublished from Canto by the Creative Hub sync\r\n'.encode(),
                 f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: {content_type}\r\n\r\n'.encode(), body, f'\r\n--{boundary}--\r\n'.encode()]
        url = f'{self.base}/rest/api/content/{self.page}/child/attachment' + (f'/{existing[name]}/data' if name in existing else '')
        http('POST', url, {**self.headers, 'Content-Type': f'multipart/form-data; boundary={boundary}'}, b''.join(parts))

    def delete(self, attachment_id):
        http('DELETE', f'{self.base}/rest/api/content/{attachment_id}', self.headers)

# ---------- Run ----------

def run(args):
    env = os.environ.get
    domain, folder = env('CANTO_DOMAIN'), env('CANTO_FOLDER_PATH', 'Staff media library')
    if not domain: sys.exit('Set CANTO_DOMAIN and CANTO_API_KEY (or CANTO_APP_ID and CANTO_APP_SECRET).')
    per_album = int(args.get('--per-album', 12)); width = int(args.get('--width', 640))
    page_id = env('CONFLUENCE_PAGE_ID', 'PAGE_ID')
    canto = Canto(domain, env('CANTO_API_KEY'), env('CANTO_APP_ID'), env('CANTO_APP_SECRET'))
    albums = select_albums(canto.albums(), folder)
    log(f'{len(albums)} albums under "{folder}"')
    picked = []
    for album in albums:
        assets = [a for a in canto.album_assets(album['id'], per_album * 2) if is_image(a)][:per_album]
        picked.append((album, assets)); log(f'  {album.get("name")}: {len(assets)} images')
    manifest = build_manifest(picked, domain, page_id, folder, env('CANTO_ASSET_URL'), env('CANTO_ALBUM_URL'))
    files = {}
    for album, assets in picked:
        for a in assets:
            item = next((i for al in manifest['albums'] for i in al['assets'] if i['id'] == str(a.get('id'))), None)
            if not item or item['thumb'] in files: continue
            raw = canto.preview_bytes(a)
            if raw: files[item['thumb']] = make_thumb(raw, width)
    # Drop manifest entries whose image could not be fetched.
    for al in manifest['albums']: al['assets'] = [i for i in al['assets'] if i['thumb'] in files]
    manifest['albums'] = [al for al in manifest['albums'] if al['assets']]
    body = json.dumps(manifest, indent=1).encode()
    if '--dry-run' in args:
        out = Path(args.get('--out', 'build/canto')); out.mkdir(parents=True, exist_ok=True)
        for name, data in files.items(): (out / name).write_bytes(data)
        (out / MANIFEST).write_bytes(body)
        log(f'Wrote {len(files)} thumbnails and {MANIFEST} to {out}'); return
    conf = Confluence(env('CONFLUENCE_BASE') or sys.exit('Set CONFLUENCE_BASE'), env('CONFLUENCE_TOKEN') or sys.exit('Set CONFLUENCE_TOKEN'), page_id)
    existing = conf.attachments()
    for name, data in files.items(): conf.upload(name, data, 'image/jpeg', existing)
    conf.upload(MANIFEST, body, 'application/json', existing)  # last, so it never points at missing images
    if '--prune' in args:
        for name, att in existing.items():
            if name.startswith(THUMB_PREFIX) and name.endswith('.jpg') and name not in files: conf.delete(att)
    log(f'Published {len(files)} thumbnails and {MANIFEST} to page {page_id}')

def self_test():
    albums = [{'id': 'a1', 'name': 'Telescopes', 'namePath': 'Library/Staff media library/Asset library - Staff/Telescopes', 'assetCount': 3},
              {'id': 'a2', 'name': 'Press', 'namePath': 'Library/Media Kits/Press', 'assetCount': 9},
              {'id': 'a3', 'name': 'Empty', 'namePath': 'Staff media library/Empty', 'assetCount': 0}]
    picked = select_albums(albums, 'Staff media library')
    assert [a['id'] for a in picked] == ['a1'], picked
    assert display_path(albums[0]['namePath'], 'Staff media library') == 'Asset library - Staff / Telescopes'
    assets = [{'id': 'x1', 'name': 'SKA_Low_station.jpg', 'copyright': 'SKAO', 'scheme': 'image', 'width': 4000, 'height': 3000},
              {'id': 'v1', 'name': 'clip.mp4', 'scheme': 'video'}]
    m = build_manifest([(albums[0], assets)], 'skao', '123', 'Staff media library', generated='t')
    item = m['albums'][0]['assets'][0]
    assert len(m['albums'][0]['assets']) == 1 and item['title'] == 'SKA Low station' and item['credit'] == 'SKAO'
    assert item['src'] == '/download/attachments/123/canto-x1.jpg' and item['href'] == 'https://skao.canto.global/asset/x1'
    assert m['albums'][0]['path'] == 'Asset library - Staff / Telescopes'
    assert build_manifest([(albums[0], [])], 'skao', '1', 'x')['albums'] == []
    print('canto_sync self-test passed')

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--self-test' in argv: self_test(); sys.exit(0)
    opts = {}
    for i, a in enumerate(argv):
        if a.startswith('--'): opts[a] = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else True
    run(opts)
