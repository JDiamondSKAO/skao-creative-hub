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
  CANTO_PORTAL        portal staff browse in (default SKAOLibrary). Tiles open the asset's own view there:
                      https://{domain}.canto.global/v/{portal}/album/{album}?column={scheme}&id={id}
  CANTO_FEATURE_TAG   Canto tag or keyword that pins an asset to Highlights (default "Hub feature")
  CANTO_POOL          newest assets considered per album (default 100)
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
        g = groups.setdefault(key, {'name': label, 'key': key, 'albums': [], 'size': 0})
        g['albums'].append(a); g['size'] += int(a.get('size') or a.get('assetCount') or 0)
    order = [o.strip().lower() for o in (order or []) if o.strip()]
    # Preferred collections first, in the given order; the rest by newest activity.
    head = sorted([g for g in groups.values() if g['name'].lower() in order], key=lambda g: order.index(g['name'].lower()))
    tail = sorted([g for g in groups.values() if g['name'].lower() not in order], key=lambda g: max(str(a.get('time') or '') for a in g['albums']), reverse=True)
    return head + tail

# ---------- Curation (pure, covered by --self-test) ----------

MIN_LONG_SIDE = 2000
# Wording that means an asset is not cleared, whatever its approval status says.
BLOCKED = re.compile(r'heritage review|cultural review|waiting on|pending|do not (use|publish|share|distribute)|not for (use|publication|external)|'
                     r'embargo|restricted|internal only|confidential|draft|test (image|file)|placeholder|delete|duplicate', re.I)
# Subjects that make a strong showcase image, and ones that rarely do.
STRONG = re.compile(r'aerial|drone|panorama|dish|antenna|station|cluster|telescope|milky way|night sky|sunset|sunrise|dusk|dawn|emu in the sky|artist impression|composite', re.I)
WEAK = re.compile(r'vehicle|ambulance|car park|office|meeting|screenshot|poster|document|logo|signage|toilet|kitchen|desk', re.I)
CAMERA_NAME = re.compile(r'^(dji|img|dsc|dscf|gopr|mvi|pxl|p\d{7}|_mg|mg|screenshot|untitled|\d)[\s_\-]*\d*', re.I)

def terms_of(asset):
    return [str(t).strip() for t in (asset.get('tag') or []) + (asset.get('keyword') or []) if str(t).strip()]

PEOPLE_WORDS = re.compile(r'\b(team|teams|staff|crew|workers?|engineers?|students?|visit(ors?)?|delegation|minister|ambassador|ceremony|group photo|portrait|headshot|interview)\b', re.I)

def has_people(asset):
    """People keyword, or a description about people (Canto's keyword is not applied consistently)."""
    if any(t.lower() in ('people', 'person', 'portrait', 'portraits', 'staff photo') for t in terms_of(asset)): return True
    return bool(PEOPLE_WORDS.search(str(asset.get('description') or '') + ' ' + str(asset.get('name') or '')))

def is_featured(asset, feature_tag):
    return any(t.lower() == feature_tag.lower() for t in terms_of(asset))

def long_side(asset):
    try: return max(int(asset.get('width') or 0), int(asset.get('height') or 0))
    except (TypeError, ValueError): return 0

def is_landscape(asset):
    try: return int(asset.get('width') or 0) > 1.1 * int(asset.get('height') or 0)
    except (TypeError, ValueError): return False

def text_of(asset):
    return ' '.join([str(asset.get('name') or ''), str(asset.get('description') or '')] + terms_of(asset))

def is_list_description(desc):
    """A description that is only a list of tags ("SKAO Sites, Australia, Cluster, ...")."""
    return desc.count(',') >= 4 and not re.search(r'[.!?]', desc)

def eligible(asset, video_ok=False):
    """Approved, credited, big enough, cleared, and a kind the page can show."""
    kind = str(asset.get('scheme', '')).lower()
    if BLOCKED.search(text_of(asset)): return False
    if kind not in ('image', 'video') or (kind == 'video' and not video_ok): return False
    if str(asset.get('approvalStatus', 'Approved')).lower() != 'approved': return False
    if not str(asset.get('copyright') or '').strip(): return False
    return kind == 'video' or long_side(asset) >= MIN_LONG_SIDE

def score(asset, feature_tag, people_penalty=0):
    desc = str(asset.get('description') or '')
    good_desc = len(desc) >= 50 and not is_list_description(desc)
    subject = text_of(asset)
    return ((1000 if is_featured(asset, feature_tag) else 0) + (20 if good_desc else 5 if desc else 0)
            + min(len(terms_of(asset)), 10) + (8 if is_landscape(asset) else 0) + (5 if long_side(asset) >= 4000 else 0)
            + (15 if STRONG.search(subject) else 0) - (20 if WEAK.search(subject) else 0)
            + int(str(asset.get('time') or '0')[:4] or 0) / 1000 - (people_penalty if has_people(asset) else 0))

def near_key(asset, album_id):
    """Frames from one sequence (DJI_0012, DJI_0013 ...) in one album count as near-duplicates.
    Canto's time is the upload time, so it cannot separate shoots."""
    name = re.sub(r'\.[A-Za-z0-9]{2,5}$', '', str(asset.get('name') or ''))
    m = re.match(r'^(.*?)[\s_\-]*\d+\D*$', name)
    return (album_id, (m.group(1) if m and m.group(1).strip() else name).lower().strip())

# Highlights mix subjects: (name, pattern, most allowed). Crops of one composite, or many night skies, read as repeats.
SUBJECTS = [('composite', re.compile(r'composite|three sites|three continents|generated image', re.I), 1),
            ('night', re.compile(r'night|milky way|emu in the sky|starry|stars\b', re.I), 2),
            ('aerial', re.compile(r'aerial|drone', re.I), 3),
            ('impression', re.compile(r'artist impression|render', re.I), 2)]

def subject_of(asset):
    text = text_of(asset)
    return next((name for name, rx, _ in SUBJECTS if rx.search(text)), None)

def pick(candidates, n, feature_tag, per_album=2, people_penalty=0, mix_subjects=False):
    """Best n (asset, album_id) pairs: scored, at most per_album per album, no near-duplicates or identical files.
    people_penalty lowers people-tagged assets (Canto's "People" keyword is applied broadly, so it ranks rather than excludes)."""
    chosen, per, near, seen, files, titles, subjects = [], {}, set(), set(), set(), set(), {}
    caps = {name: cap for name, _, cap in SUBJECTS}
    for asset, album_id in sorted(candidates, key=lambda c: score(c[0], feature_tag, people_penalty), reverse=True):
        md5, title = asset.get('md5'), title_for(asset).lower()
        if asset.get('id') in seen or (md5 and md5 in files) or title in titles: continue
        featured = is_featured(asset, feature_tag)
        if not featured and (per.get(album_id, 0) >= per_album or near_key(asset, album_id) in near): continue
        subject = subject_of(asset) if mix_subjects else None
        if subject and not featured and subjects.get(subject, 0) >= caps[subject]: continue
        if subject: subjects[subject] = subjects.get(subject, 0) + 1
        chosen.append((asset, album_id)); seen.add(asset.get('id')); titles.add(title)
        if md5: files.add(md5)
        per[album_id] = per.get(album_id, 0) + 1; near.add(near_key(asset, album_id))
        if len(chosen) >= n: break
    return chosen

def title_for(asset):
    """Canto's name unless it looks like a file name; then the start of the description."""
    name = tidy_title(asset)
    desc = re.sub(r'\s+', ' ', str(asset.get('description') or '')).strip()
    filey = CAMERA_NAME.match(name) or len(name) < 4 or re.search(r'\d{4,}|\b[A-Z]\d{3,}\b', name) or (name.isupper() and len(name) > 6) or '_' in str(asset.get('name') or '')
    if desc and not is_list_description(desc) and filey:
        first = re.split(r'(?<=[.!?])\s', desc)[0]
        return first if len(first) <= 70 else first[:67].rsplit(' ', 1)[0] + '…'
    return name

def alt_for(asset):
    desc = re.sub(r'\s+', ' ', str(asset.get('description') or '')).strip()
    if is_list_description(desc): desc = ''
    return (desc if len(desc) <= 160 else desc[:157].rsplit(' ', 1)[0] + '…') or title_for(asset)

def portal_link(domain, portal, album_id, asset):
    kind = 'video' if str(asset.get('scheme', '')).lower() == 'video' else 'image'
    return f'https://{domain}.canto.global/v/{portal}/album/{album_id}?column={kind}&id={asset["id"]}'

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

def fingerprint(jpeg):
    """64-bit difference hash of an image, for spotting visual duplicates across files and albums."""
    try:
        from PIL import Image
    except ImportError:
        return None
    def dhash(im):
        px = list(im.convert('L').resize((9, 8)).getdata())
        return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
    im = Image.open(io.BytesIO(jpeg))
    side = min(im.size)
    centre = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width + side) // 2, (im.height + side) // 2))
    # Whole image and centre square: crops and re-exports of one picture share the centre.
    return (dhash(im), dhash(centre))

def distinct(items, prints, limit, threshold=10):
    """Keep items in order, dropping any that look like one already kept."""
    kept, seen = [], []
    for it in items:
        fp = prints.get(it['thumb'])
        if fp is not None and any(bin(a ^ b).count('1') <= threshold for s in seen for a, b in zip(fp, s)): continue
        kept.append(it)
        if fp is not None: seen.append(fp)
        if len(kept) >= limit: break
    return kept

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
    portal, feature = env('CANTO_PORTAL', 'SKAOLibrary'), env('CANTO_FEATURE_TAG', 'Hub feature')
    pool_size, min_assets = int(env('CANTO_POOL', 100)), int(env('CANTO_MIN_ASSETS', 3))
    preferred = [o.strip() for o in (env('CANTO_ORDER') or 'SKA-Low,SKA-Mid,Hero shots').split(',')]
    albums = select_albums(canto.albums(), folder)
    groups = collections(albums, folder, int(env('CANTO_GROUP_DEPTH', 3)), preferred)
    log(f'{len(albums)} albums under "{folder}", in {len(groups)} collections')
    pools = {al['id']: canto.album_assets(al['id'], pool_size) for g in groups for al in g['albums']}
    link = lambda album_id, asset: portal_link(domain, portal, album_id, asset)
    def item(asset, album_id):
        thumb = f'{THUMB_PREFIX}{re.sub(r"[^A-Za-z0-9_-]", "", str(asset["id"]))}.jpg'
        return {'id': str(asset['id']), 'title': title_for(asset), 'alt': alt_for(asset), 'credit': str(asset.get('copyright') or '').strip(),
                'kind': 'video' if str(asset.get('scheme', '')).lower() == 'video' else 'image', 'people': has_people(asset),
                'width': asset.get('width'), 'height': asset.get('height'), 'thumb': thumb,
                'src': f'/download/attachments/{page_id}/{quote(thumb)}', 'href': link(album_id, asset)}
    manifest = {'version': 2, 'generated': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': f'Canto: {folder}', 'highlights': [], 'albums': []}
    sources, showcase = {}, []
    for g in groups:
        video_ok = bool(re.search(r'video|animation', g['name'], re.I))
        people_ok = bool(re.search(r'event', g['name'], re.I))
        cands = [(a, al['id']) for al in g['albums'] for a in pools[al['id']] if eligible(a, video_ok)]
        cap = max(2, -(-per_album // max(1, len(g['albums']))))
        chosen = pick(cands, per_album + 4, feature, per_album=cap + 1, people_penalty=0 if people_ok else 10)  # spares for visual de-duplication
        need = 2 if g['name'].lower() in (x.lower() for x in preferred) else min_assets
        if len(chosen) < need:
            log(f'  {g["name"]}: skipped ({len(chosen)} suitable of {g["size"]})'); continue
        if not people_ok: showcase += [(a, al, g['name']) for a, al in cands]
        biggest = max(g['albums'], key=lambda al: int(al.get('size') or 0))
        href = f'https://{domain}.canto.global/v/{portal}/album/{biggest["id"]}'
        if len(g['albums']) > 1:
            parts, ids = str(biggest.get('namePath') or '').split('/'), str(biggest.get('idPath') or '').split('/')
            idx = next((i for i, p in enumerate(parts) if p.strip() == g['key'][-1]), None)
            if idx is not None and len(ids) == len(parts): href = f'https://{domain}.canto.global/v/{portal}/folder/{ids[idx]}'
        for asset, album_id in chosen: sources[str(asset['id'])] = asset
        manifest['albums'].append({'id': str(biggest.get('id')), 'name': g['name'], 'path': g['name'], 'count': g['size'], 'href': href,
                                   'assets': [item(a, al) for a, al in chosen], '_newest': max(str(a.get('time') or '') for a, _ in chosen)})
        log(f'  {g["name"]}: {len(chosen)} chosen of {len(cands)} suitable ({g["size"]} in {len(g["albums"])} albums)')
    # Preferred collections first, in order; the rest by their newest chosen asset.
    rank = {n.lower(): i for i, n in enumerate(preferred)}
    head = sorted((al for al in manifest['albums'] if al['name'].lower() in rank), key=lambda al: rank[al['name'].lower()])
    tail = sorted((al for al in manifest['albums'] if al['name'].lower() not in rank), key=lambda al: al['_newest'], reverse=True)
    manifest['albums'] = head + tail
    for al in manifest['albums']: al.pop('_newest', None)
    album_of = {str(a['id']): al for a, al, _ in showcase}
    images = [(a, grp) for a, al, grp in showcase if str(a.get('scheme')).lower() == 'image']
    by_collection = pick([c for c in images if not has_people(c[0]) or is_featured(c[0], feature)], 16, feature, per_album=5, mix_subjects=True)
    if len(by_collection) < 8:  # top up only when the mix is thin: first without it, then people-tagged, ranked below
        by_collection += [c for c in pick([c for c in images if not has_people(c[0])], 16, feature, per_album=5) if c not in by_collection][:16 - len(by_collection)]
    if len(by_collection) < 10:
        by_collection += [c for c in pick(images, 16, feature, per_album=5, people_penalty=40) if c not in by_collection][:16 - len(by_collection)]
    highlights = [(a, album_of[str(a['id'])]) for a, _ in by_collection]
    for asset, album_id in highlights: sources[str(asset['id'])] = asset
    manifest['highlights'] = [item(a, al) for a, al in highlights]
    log(f'  Highlights: {len(highlights)} ({sum(1 for a, _ in highlights if is_featured(a, feature))} tagged "{feature}")')
    files = {}
    for aid, asset in sources.items():
        thumb = f'{THUMB_PREFIX}{re.sub(r"[^A-Za-z0-9_-]", "", aid)}.jpg'
        if thumb in files: continue
        raw = canto.preview_bytes(asset)
        if raw: files[thumb] = make_thumb(raw, width)
    # Drop entries whose image could not be fetched, then near-identical images (crops, re-exports, copies in other albums).
    prints = {name: fingerprint(data) for name, data in files.items()}
    for al in manifest['albums']: al['assets'] = distinct([i for i in al['assets'] if i['thumb'] in files], prints, per_album)
    manifest['albums'] = [al for al in manifest['albums'] if al['assets']]
    manifest['highlights'] = distinct([i for i in manifest['highlights'] if i['thumb'] in files], prints, 12)
    used = {i['thumb'] for al in manifest['albums'] for i in al['assets']} | {i['thumb'] for i in manifest['highlights']}
    files = {k: v for k, v in files.items() if k in used}
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
    # Curation
    base = {'scheme': 'image', 'approvalStatus': 'Approved', 'copyright': 'SKAO', 'width': 6000, 'height': 4000, 'description': 'A long and useful description of the SKA-Low site at dawn.', 'tag': ['SKA-Low', 'Australia']}
    assert eligible(base) and not eligible({**base, 'copyright': ''}) and not eligible({**base, 'width': 1200, 'height': 800})
    assert not eligible({**base, 'approvalStatus': 'Restricted'}) and not eligible({**base, 'scheme': 'video'}) and eligible({**base, 'scheme': 'video'}, video_ok=True)
    burst = [({**base, 'id': f'b{i}', 'name': f'DJI_00{12 + i}.JPG', 'time': '2025062604'}, 'A') for i in range(4)]
    other = [({**base, 'id': f'o{i}', 'name': f'Dish {chr(65 + i)}.jpg', 'time': '2025011000', 'md5': f'm{i}'}, 'B') for i in range(3)]
    got = pick(burst + other, 5, 'Hub feature', per_album=2)
    assert sum(1 for a, al in got if al == 'A') == 1, 'one per frame sequence'
    assert sum(1 for a, al in got if al == 'B') == 2, 'at most two per album'
    people = ({**base, 'id': 'p1', 'name': 'Crew', 'keyword': ['People'], 'time': '2026'}, 'C')
    ranked = pick([people] + other, 5, 'Hub feature', people_penalty=40)
    assert ranked[-1] == people and len(ranked) == 3, 'people-tagged assets rank last rather than vanish'
    dupe = ({**base, 'id': 'd1', 'name': 'Copy', 'md5': 'm0'}, 'D')
    assert dupe not in pick(other + [dupe], 5, 'Hub feature'), 'identical files appear once'
    star = ({**base, 'id': 's1', 'tag': ['hub feature'], 'description': '', 'width': 2400, 'height': 3000}, 'A')
    assert pick(burst + other + [star], 3, 'Hub feature')[0][0]['id'] == 's1', 'tagged assets come first'
    assert title_for({'name': 'DJI_0012.JPG', 'description': 'Aerial view of SKA-Mid dishes. More text.'}) == 'Aerial view of SKA-Mid dishes.'
    assert title_for({'name': 'SKA-Low station at dusk.jpg'}) == 'SKA-Low station at dusk'
    assert not eligible({**base, 'description': 'WAITING ON HERITAGE REVIEW. Aerial view of the site.'}), 'uncleared wording blocks an asset'
    assert title_for({'name': 'DFM D850 45MP June 2025 00793.jpg', 'description': 'Field Node Distribution Hub for station S10-3. Taken June 2025.'}) == 'Field Node Distribution Hub for station S10-3.'
    assert title_for({'name': 'MID LOW DRONE COMPOSITE 2.jpg', 'description': 'SKAO Sites, Australia, Cluster, SKA-low, Station'}) == 'MID LOW DRONE COMPOSITE 2'
    assert alt_for({'name': 'x', 'description': 'SKAO Sites, Australia, Cluster, SKA-low, Station'}) == 'x'
    lifts = [({**base, 'id': f'l{i}', 'name': f'Big Lift {n}.jpg', 'md5': f'lift{i}'}, 'E') for i, n in enumerate([6, 45])]
    assert len(pick(lifts, 5, 'Hub feature', per_album=5)) == 1, 'numbered frames of one sequence appear once'
    same = [({**base, 'id': f't{i}', 'name': 'Aerial view of the CPF.jpg', 'md5': f't{i}'}, f'F{i}') for i in range(2)]
    assert len(pick(same, 5, 'Hub feature')) == 1, 'identical titles appear once'
    weak = ({**base, 'id': 'w1', 'name': 'Ambulance next to vehicle', 'md5': 'w'}, 'G'); strong = ({**base, 'id': 'g1', 'name': 'Aerial panorama of dishes', 'md5': 'g'}, 'G')
    assert pick([weak, strong], 2, 'Hub feature', per_album=2)[0] == strong
    try:
        from PIL import Image, ImageDraw
        def img(shift):
            im = Image.new('RGB', (300, 200), 'navy'); d = ImageDraw.Draw(im); d.ellipse((60 + shift, 40, 200 + shift, 180), fill='white')
            b = io.BytesIO(); im.save(b, 'JPEG'); return b.getvalue()
        def crop(raw):
            im = Image.open(io.BytesIO(raw)); b = io.BytesIO(); im.crop((50, 0, 250, 200)).save(b, 'JPEG'); return b.getvalue()
        near = {'a': fingerprint(img(0)), 'b': fingerprint(make_thumb(img(0), 150)), 'c': fingerprint(img(90)), 'd': fingerprint(crop(img(0)))}
        kept = distinct([{'thumb': 'a'}, {'thumb': 'b'}, {'thumb': 'c'}, {'thumb': 'd'}], near, 5)
        assert [k['thumb'] for k in kept] == ['a', 'c'], ('resized copies and crops count as the same image', [k['thumb'] for k in kept])
    except ImportError:
        pass
    assert portal_link('skao', 'SKAOLibrary', 'S980K', {'id': 'x1', 'scheme': 'video'}) == 'https://skao.canto.global/v/SKAOLibrary/album/S980K?column=video&id=x1'
    skies = [({**base, 'id': f'n{i}', 'name': f'Night sky {chr(65 + i)}', 'description': 'The Milky Way over the stations at night, a long description.', 'md5': f'n{i}'}, f'N{i}') for i in range(4)]
    mixed = pick(skies + other, 5, 'Hub feature', mix_subjects=True)
    assert sum(1 for a, _ in mixed if subject_of(a) == 'night') == 2, 'at most two night skies in a mixed pick'
    assert has_people({'description': 'Team installs the third hydrogen maser in South Africa.'}) and not has_people({'description': 'Aerial view of the S8 cluster.'})
    print('canto_sync self-test passed')

if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--self-test' in argv: self_test(); sys.exit(0)
    opts = {}
    for i, a in enumerate(argv):
        if a.startswith('--'): opts[a] = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else True
    run(opts)
