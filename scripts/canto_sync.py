"""Sync Canto's staff media folder to the Creative Hub.

Reads every album under a Canto folder path (default "Staff media library"),
takes each album's newest images, makes web-sized thumbnails and publishes them
with a small manifest (canto-showcase.json) as attachments on one Hub page.
The theme reads the manifest from Confluence, so staff browsers never need a
Canto token and never see an expiring Canto link.

Adapted from the Canto client in canto-metadata-assistant, with what testing
against SKAO's Canto showed (September 2026):
- OAuth client credentials work at https://oauth.canto.global/oauth/api/oauth2/token
  (not the tenant host) and answer in camelCase (accessToken, expiresIn).
- /api/v1/album returns the web app, so albums are listed with /search?scheme=album
  (namePath, size); /album/{id} returns an album's contents.
- url.directUrlPreview gives an 800 px JPEG for images and a poster frame for videos,
  served from a CDN after a redirect.
Albums are grouped into collections by path (e.g. "Image bank - Staff/SKA-Low").

Environment
  CANTO_DOMAIN        subdomain, e.g. "skao"
  CANTO_API_KEY       direct API token, or CANTO_APP_ID and CANTO_APP_SECRET
  CANTO_FOLDER_PATH   namePath prefix to publish (default "Staff media library")
  CANTO_ASSET_URL     click-through template, default https://{domain}.canto.global/asset/{id}
  CANTO_ALBUM_URL     album link template, default https://{domain}.canto.global/album/{id}
  CANTO_GROUP_DEPTH   path levels below the folder that define a collection (default 3)
  CANTO_ORDER         collections to list first, comma-separated (default "SKA-Low,SKA-Mid,Hero shots")
  CANTO_OAUTH_URL     token endpoint, default https://oauth.canto.global/oauth/api/oauth2/token
  CANTO_MIN_ASSETS    leave out collections with fewer images or videos than this (default 3)
  CONFLUENCE_BASE     e.g. https://confluence.skatelescope.org
  CONFLUENCE_TOKEN    personal access token of the account that owns the sync
  CONFLUENCE_PAGE_ID  Hub page that holds the attachments

Usage
  python3 scripts/canto_sync.py --dry-run --out build/canto   # fetch from Canto, write files locally
  python3 scripts/canto_sync.py                               # fetch and publish to Confluence
  python3 scripts/canto_sync.py --self-test
Options: --per-album N (default 12), --width PX (default 640), --prune (remove stale canto-* thumbnails),
         --env FILE (read KEY=VALUE settings from a local file, e.g. dev/canto.env; values already set in the environment win)
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, HTTPRedirectHandler, HTTPSHandler, build_opener
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
import io, json, os, re, ssl, sys, time, uuid

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

def _tls_context():
    """Verify HTTPS with the system bundle, or certifi's where Python ships without one (python.org builds on macOS)."""
    paths = ssl.get_default_verify_paths()
    if os.environ.get('SSL_CERT_FILE') or (paths.cafile and os.path.exists(paths.cafile)):
        return ssl.create_default_context()
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

_opener = build_opener(HTTPSHandler(context=_tls_context()), _DropAuthOnRedirect)

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
    def __init__(self, domain, api_key=None, app_id=None, app_secret=None, oauth_url=None):
        self.domain, self.base = domain, f'https://{domain}.canto.global/api/v1'
        self.app_id, self.app_secret = app_id, app_secret
        self.oauth_url = oauth_url or 'https://oauth.canto.global/oauth/api/oauth2/token'
        # Client credentials renew themselves, so prefer them over a generated token.
        if app_id and app_secret: self.token, self.expires = None, -1
        else: self.token, self.expires = api_key, 0

    def _auth(self):
        if self.token and (self.expires == 0 or time.time() < self.expires): return
        body = urlencode({'grant_type': 'client_credentials', 'app_id': self.app_id, 'app_secret': self.app_secret}).encode()
        _, raw, _ = http('POST', self.oauth_url, {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}, body)
        data = json.loads(raw)
        token = data.get('accessToken') or data.get('access_token')
        if not token: raise RuntimeError('Canto did not return an access token')
        self.token = token
        self.expires = time.time() + int(data.get('expiresIn') or data.get('expires_in') or 3600) - 60

    def get(self, path, **params):
        self._auth()
        _, raw, _ = http('GET', f'{self.base}{path}?{urlencode(params)}', {'Authorization': f'Bearer {self.token}', 'Accept': 'application/json'})
        return json.loads(raw or b'{}')

    def albums(self):
        found, start = [], 0
        while True:
            data = self.get('/search', scheme='album', limit=1000, start=start)
            page = data.get('results', [])
            found += page
            if not page or len(found) >= int(data.get('found') or 0): return found
            start += len(page)

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
        if any('/'.join(segments[i:i + len(prefix.split('/'))]) == prefix for i in range(len(segments))) and (a.get('size', a.get('assetCount')) is None or int(a.get('size', a.get('assetCount'))) > 0):
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
    return str(asset.get('scheme', 'image')).lower() in ('image', 'video')

def tidy_segment(seg):
    return re.sub(r'\s+-\s+Staff$', '', seg.strip(), flags=re.I)

def collections(albums, folder_path, depth=3, order=None):
    """Group albums into collections by the first `depth` path levels below the folder."""
    groups = {}
    for a in albums:
        parts = [p for p in display_path(a.get('namePath'), folder_path).split(' / ') if p]
        key = tuple(parts[:depth]) or (a.get('name') or 'Album',)
        names = [tidy_segment(p) for p in key]
        label = names[-1] if not re.fullmatch(r'\d{4}', names[-1]) or len(names) < 2 else f'{names[-2]} {names[-1]}'
        g = groups.setdefault(key, {'name': label, 'albums': [], 'size': 0})
        g['albums'].append(a); g['size'] += int(a.get('size') or a.get('assetCount') or 0)
    order = [o.strip().lower() for o in (order or []) if o.strip()]
    # Preferred collections first, in the given order; the rest by newest activity.
    head = sorted([g for g in groups.values() if g['name'].lower() in order], key=lambda g: order.index(g['name'].lower()))
    tail = sorted([g for g in groups.values() if g['name'].lower() not in order], key=lambda g: max(str(a.get('time') or '') for a in g['albums']), reverse=True)
    return head + tail

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
                          'kind': 'video' if str(a.get('scheme', '')).lower() == 'video' else 'image',
                          'width': a.get('width'), 'height': a.get('height'), 'thumb': thumb,
                          'src': f'/download/attachments/{page_id}/{quote(thumb)}',
                          'href': asset_url.format(domain=domain, id=a['id'])})
        if items:
            out['albums'].append({'id': str(album.get('id')), 'name': album.get('name') or 'Album',
                                  'path': display_path(album.get('namePath'), folder_path) or album.get('name') or 'Album',
                                  'count': int(album.get('size') or album.get('assetCount') or len(items)),
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

def load_env(path):
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        key, value = line.split('=', 1)
        value = value.strip().strip('"').strip("'")
        if value and key.strip() not in os.environ: os.environ[key.strip()] = value

def run(args):
    if args.get('--env'): load_env(args['--env'])
    env = os.environ.get
    domain, folder = env('CANTO_DOMAIN'), env('CANTO_FOLDER_PATH', 'Staff media library')
    if not domain: sys.exit('Set CANTO_DOMAIN and CANTO_API_KEY (or CANTO_APP_ID and CANTO_APP_SECRET).')
    per_album = int(args.get('--per-album', 12)); width = int(args.get('--width', 640))
    page_id = env('CONFLUENCE_PAGE_ID', 'PAGE_ID')
    if not env('CANTO_API_KEY') and not (env('CANTO_APP_ID') and env('CANTO_APP_SECRET')):
        sys.exit('Canto credentials missing: set CANTO_API_KEY (generated access token), or both CANTO_APP_ID and CANTO_APP_SECRET.')
    log('Canto auth: ' + ('client credentials (App ID and App Secret)' if env('CANTO_APP_ID') and env('CANTO_APP_SECRET') else 'generated access token'))
    canto = Canto(domain, env('CANTO_API_KEY'), env('CANTO_APP_ID'), env('CANTO_APP_SECRET'), env('CANTO_OAUTH_URL'))
    albums = select_albums(canto.albums(), folder)
    groups = collections(albums, folder, int(env('CANTO_GROUP_DEPTH', 3)), (env('CANTO_ORDER') or 'SKA-Low,SKA-Mid,Hero shots').split(','))
    log(f'{len(albums)} albums under "{folder}", in {len(groups)} collections')
    picked = []
    for g in groups:
        pool = []
        for album in g['albums']:
            pool += [a for a in canto.album_assets(album['id'], per_album) if is_image(a)]
        seen, assets = set(), []
        for a in sorted(pool, key=lambda a: str(a.get('time') or ''), reverse=True):
            if a.get('id') not in seen: seen.add(a.get('id')); assets.append(a)
        biggest = max(g['albums'], key=lambda a: int(a.get('size') or 0))
        entry = {'id': biggest.get('id'), 'name': g['name'], 'namePath': g['name'], 'size': g['size']}
        if len(assets) < int(env('CANTO_MIN_ASSETS', 3)):
            log(f'  {g["name"]}: skipped ({len(assets)} images or videos)'); continue
        entry['_newest'] = str(assets[0].get('time') or '') if assets else ''
        picked.append((entry, assets[:per_album])); log(f'  {g["name"]}: {min(len(assets), per_album)} of {g["size"]} ({len(g["albums"])} albums)')
    # Preferred collections keep their place; the rest follow by newest asset.
    preferred = [o.strip().lower() for o in (env('CANTO_ORDER') or 'SKA-Low,SKA-Mid,Hero shots').split(',')]
    head = [p for p in picked if p[0]['name'].lower() in preferred]
    picked = head + sorted([p for p in picked if p[0]['name'].lower() not in preferred], key=lambda p: p[0]['_newest'], reverse=True)
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
    assert [i['kind'] for i in m['albums'][0]['assets']] == ['image', 'video'] and item['title'] == 'SKA Low station' and item['credit'] == 'SKAO'
    assert item['src'] == '/download/attachments/123/canto-x1.jpg' and item['href'] == 'https://skao.canto.global/asset/x1'
    assert m['albums'][0]['path'] == 'Asset library - Staff / Telescopes'
    assert build_manifest([(albums[0], [])], 'skao', '1', 'x')['albums'] == []
    staff = [{'id': 'l1', 'name': 'Stations', 'namePath': 'Staff media library/Asset library - Staff/Image bank - Staff/SKA-Low/Stations', 'size': 30, 'time': '2026'},
             {'id': 'l2', 'name': 'Aerials', 'namePath': 'Staff media library/Asset library - Staff/Image bank - Staff/SKA-Low/Aerials', 'size': 5, 'time': '2025'},
             {'id': 'e1', 'name': 'Vienna', 'namePath': 'Staff media library/Asset library - Staff/Events - Staff/2025/Vienna', 'size': 70, 'time': '2025'},
             {'id': 'e2', 'name': 'Launch', 'namePath': 'Staff media library/Asset library - Staff/Events - Staff/2026/Launch', 'size': 9, 'time': '2026'},
             {'id': 'h1', 'name': 'Dusk', 'namePath': 'Staff media library/Asset library - Staff/Image bank - Staff/Hero shots/Dusk', 'size': 5, 'time': '2024'}]
    groups = collections(staff, 'Staff media library', 3, ['SKA-Low', 'Hero shots'])
    assert [g['name'] for g in groups] == ['SKA-Low', 'Hero shots', 'Events 2026', 'Events 2025'], [g['name'] for g in groups]
    assert groups[0]['size'] == 35 and len(groups[0]['albums']) == 2
    vid = build_manifest([(albums[0], [{'id': 'v2', 'name': 'Zoom.mp4', 'scheme': 'video'}])], 'skao', '1', 'x')
    assert vid['albums'][0]['assets'][0]['kind'] == 'video'
    print('canto_sync self-test passed')

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--self-test' in argv: self_test(); sys.exit(0)
    opts = {}
    for i, a in enumerate(argv):
        if a.startswith('--'): opts[a] = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else True
    run(opts)
