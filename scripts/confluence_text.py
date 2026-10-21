"""Set up the Confluence side of the Hub for people who read it in Confluence itself ("View in Confluence").

  python3 scripts/confluence_text.py                       # write each page's text to release/go-live/page-text/ and print the plan
  python3 scripts/confluence_text.py --apply               # carry out the plan (asks for your Confluence token)
  python3 scripts/confluence_text.py --apply "Letterheads" # only the pages named (moves and new pages included)

The plan:
- create the pages the Hub added later (Partner templates, Construction overview, Partner logos) where they belong;
- give every page the Hub uses its own text in place of the March placeholders, with Confluence's Attachments list where
  the Hub lists files, so the page works on its own;
- move pages so the page tree follows the Hub's sections;
- give the space home page a directory of the sections.
If dev/links.json names the Hub's address as HUB_SITE, each page also opens with a note pointing to the Hub.

The text comes from the build's article copies (content/, so run scripts/build.py first), without the theme's
furniture: icons, labels, in-page buttons and empty slots. Every change is a new page version, so page history can
bring the old text back. Pages in hidden sections (Events, for now) are left alone. Nothing is deleted.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
import getpass, html as htmllib, json, os, sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import links
OUT = ROOT / 'release' / 'go-live' / 'page-text'
SPACE, HOME = 'CRH', 'SKAO Creative Hub Home'
BASE = 'https://confluence.skatelescope.org'
# Pages the Hub added after the space was set up, and their parents.
NEW = {'Partner templates': 'Slide Decks & Presentations', 'Construction overview': 'Slide Decks & Presentations', 'Partner logos': 'Brand Guidelines',
       'Share your presentation': 'Slide Decks & Presentations'}
# Moves that make the page tree follow the Hub's sections (moving keeps a page's ID and address).
MOVES = {'Logos & Icons': 'Brand Guidelines', 'Slide Decks & Presentations': HOME, 'Video & Animation': 'Photography Media',
         'Accessibility Guidelines': 'Self-Service Guides', 'Adobe Firefly': 'Self-Service Guides', 'Canto DAM Access': 'Photography Media',
         'Document Templates': HOME, 'FAQ': HOME, 'Font Downloads': 'Brand Guidelines', 'Formatting a Presentation': 'Slide Decks & Presentations',
         'Photography Media': HOME, 'Poster Templates': 'Document Templates', 'Print Supplier Contacts': 'Self-Service Guides',
         'SKA-Low Overview': 'Construction overview', 'SKA-Mid Overview': 'Construction overview', 'Self-Service Guides': HOME}

KEEP = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'br', 'code', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'}
RENAME = {'b': 'strong', 'i': 'em', 'summary': 'h3', 'dt': 'h4', 'h1': 'h2'}
BLOCK = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'}
DROP = {'svg', 'script', 'style', 'button', 'form', 'input', 'select', 'textarea', 'img', 'picture', 'video', 'iframe', 'dialog'}
VOID = {'br', 'img', 'input', 'hr', 'meta', 'link', 'source'}
FURNITURE = ('eyebrow', 'arr', 'kicker', 'start-kicker', 'share-kicker', 'chip', 'badge', 'visually-hidden', 'sr-only', 'file-pending')

def esc(text, quote=False):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text.replace('"', '&quot;') if quote else text

def attachments(labels):
    """Confluence's own list of the page's files."""
    param = f'<ac:parameter ac:name="labels">{labels}</ac:parameter>' if labels else ''
    return f'<ac:structured-macro ac:name="attachments">{param}</ac:structured-macro>'

def hub_note(site):
    return ('<ac:structured-macro ac:name="info"><ac:rich-text-body><p>This page is also in the '
            f'<a href="{esc(site, True)}">Creative Hub</a>, with previews and quick downloads.</p></ac:rich-text-body></ac:structured-macro>')

class Storage(HTMLParser):
    """Keeps headings, paragraphs, lists, tables and links; unwraps layout; drops the theme's furniture."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack, self.skip, self.para = [], [], 0, False

    def in_block(self):
        return any(t in BLOCK for t in self.stack)

    def open_para(self):
        if not self.para and not self.in_block():
            self.out.append('<p>'); self.para = True

    def close_para(self):
        if self.para:
            self.out.append('</p>'); self.para = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.skip:
            if tag not in VOID: self.skip += 1
            return
        classes = (a.get('class') or '').split()
        if 'data-downloads-slot' in a or 'data-attachments' in a:
            self.close_para(); self.out.append(attachments('' if 'data-attachments' in a else 'approved'))
        href = a.get('href') or ''
        in_page_button = tag == 'a' and not href.startswith(('https://', 'http://', 'mailto:')) and (
            'button' in classes or 'text-link' in classes or not href)
        if (tag in DROP or 'hidden' in a or a.get('aria-hidden') == 'true' or 'data-downloads-slot' in a or 'data-attachments' in a
                or 'data-file-pending' in a or in_page_button or any(c in FURNITURE for c in classes)):
            if tag not in VOID: self.skip = 1
            return
        tag = RENAME.get(tag, tag)
        if tag not in KEEP:
            return  # layout: keep what is inside
        if tag in BLOCK:
            self.close_para()
        elif not self.in_block():
            self.open_para()
        if tag in ('strong', 'em', 'a') and self.out and self.out[-1] in ('</em>', '</strong>'):
            self.out.append(' ')
        if tag == 'a':
            if self.para and self.out and self.out[-1] == '</a>':
                self.close_para(); self.open_para()  # links side by side (cards, previous and next) get a line each
            if not href.startswith(('https://', 'http://', 'mailto:')):
                self.stack.append('a-unwrapped'); return
            self.out.append(f'<a href="{esc(href, True)}">')
        elif tag == 'br':
            self.out.append('<br />'); return
        else:
            self.out.append(f'<{tag}>')
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.skip:
            if tag not in VOID: self.skip -= 1
            return
        tag = RENAME.get(tag, tag)
        if tag not in KEEP or tag == 'br':
            if tag in ('div', 'section', 'nav', 'article', 'header', 'footer', 'aside', 'details', 'dd', 'figure'):
                self.close_para()  # a layout block ends any loose paragraph inside it
            return
        while self.stack:
            top = self.stack.pop()
            if top == 'a' and self.out and not self.out[-1].startswith('<'): self.out[-1] = self.out[-1].rstrip()
            if top != 'a-unwrapped': self.out.append(f'</{top}>')
            if top == 'strong' and 'a' in self.stack: self.out.append('<br />')  # a card's title, then its description
            if top == tag or (tag == 'a' and top == 'a-unwrapped'): break

    def handle_data(self, data):
        if self.skip or not data.strip() and not self.in_block() and not self.para:
            return
        self.open_para()
        if self.out and self.out[-1] == '</strong>' and data[:1].isalnum():
            data = ': ' + data  # "Start here: Guide slides on using the deck"
        self.out.append(esc(data))

    def result(self):
        self.close_para()
        while self.stack:
            top = self.stack.pop()
            if top != 'a-unwrapped': self.out.append(f'</{top}>')
        text = ''.join(self.out)
        for empty in ('<p></p>', '<p> </p>', '<li></li>', '<ul></ul>', '<strong></strong>'):
            text = text.replace(empty, '')
        return text

def well_formed(body):
    ET.fromstring(f'<root xmlns:ac="http://atlassian.com/content">{body}</root>')
    return body

def page_link(meta):
    return f"{BASE}/display/{SPACE}/{meta['source_title'].replace(' ', '+')}" if meta['id'].startswith('9900') else f"{BASE}/pages/viewpage.action?pageId={meta['id']}"

def home_text(routes, note):
    """The space home page: what the Hub is, then each section and its pages."""
    from polish import SECTIONS, CHILD_OF
    by_file = {name: meta for name, meta in routes.items()}
    out = [note, '<p>Templates, brand files, slides and photos from across the SKAO, including the latest from both sites, '
           'from the Communications team.</p>']
    for key, label, landing, groups in SECTIONS:
        out.append(f'<h2><a href="{esc(page_link(by_file[landing]), True)}">{esc(label)}</a></h2><ul>')
        for group, names in groups:
            for name in names:
                if name in by_file and name not in CHILD_OF:
                    out.append(f'<li><a href="{esc(page_link(by_file[name]), True)}">{esc(by_file[name]["display_title"])}</a></li>')
        out.append('</ul>')
    out.append(f'<h2>Help</h2><ul><li><a href="{esc(page_link(by_file["faq.html"]), True)}">Common questions</a></li>'
               f'<li><a href="{esc(page_link(by_file["resources.html"]), True)}">All files</a></li></ul>')
    return well_formed(''.join(out))

def classify():
    """Each route page as 'hub' (on the Hub), 'hidden' (a hidden section, kept) or 'old' (folded into another page)."""
    from polish import SECTIONS, HIDDEN, members_of
    from gethelp import MOVED, RETIRED
    routes = json.loads((ROOT / 'evidence' / 'interior-route-map.json').read_text())
    live = {'resources.html', 'faq.html'}.union(*(members_of(sec) for sec in SECTIONS))
    return {name: 'hidden' if name in HIDDEN else 'hub' if name in live else 'old' if name in MOVED or name in RETIRED else 'other'
            for name in routes}

def pages():
    """(Confluence title, page id or '' for a page still to create, storage text) for the Hub's pages, home page last.
    Old pages are left out: scripts/confluence_cleanup.py moves them to the trash."""
    routes = json.loads((ROOT / 'evidence' / 'interior-route-map.json').read_text())
    from interiors import PLANNED
    found, kinds = links.load(), classify()
    note = hub_note(found['HUB_SITE']) if found.get('HUB_SITE') else ''
    for name, meta in routes.items():
        src = ROOT / 'content' / name.replace('.html', '-confluence.html')
        if kinds[name] != 'hub' or not src.exists(): continue
        parser = Storage(); parser.feed(links.strip_pending(links.fill(src.read_text(), found)))
        yield meta['source_title'], ('' if meta['id'] in PLANNED else meta['id']), well_formed(note + parser.result())
    yield HOME, '', home_text(routes, note)

def write():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.xml'): old.unlink()
    n = 0
    for title, _, body in pages():
        (OUT / (title.replace('/', '-') + '.xml')).write_text(body); n += 1
    print(f'{n} pages written to {OUT.relative_to(ROOT)}.')
    print('With --apply:\n  create ' + ', '.join(f'{t} (under {p})' for t, p in NEW.items()))
    print('  move ' + ', '.join(f'{t} -> {p}' for t, p in MOVES.items()))
    print(f'  replace the text on all {n} pages, home page included. Read a few files first.')

def apply():
    from canto_sync import http
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    base = (os.environ.get('CONFLUENCE_BASE') or BASE).rstrip('/')
    token = os.environ.get('CONFLUENCE_TOKEN') or getpass.getpass('Confluence personal access token (it will not show): ').strip() or sys.exit('No token given.')
    head = {'Authorization': f'Bearer {token}', 'X-Atlassian-Token': 'nocheck', 'Accept': 'application/json'}
    send = lambda method, path, data: json.loads(http(method, base + path, {**head, 'Content-Type': 'application/json'}, json.dumps(data).encode())[1] or b'{}')
    ids = {}
    def find(title):
        if title not in ids:
            hits = json.loads(http('GET', base + '/rest/api/content?' + urlencode({'spaceKey': SPACE, 'title': title, 'type': 'page'}), head)[1]).get('results', [])
            ids[title] = hits[0]['id'] if hits else ''
        return ids[title]
    texts = {title: (page_id, body) for title, page_id, body in pages()}
    done = failed = 0
    created = set()
    for title, parent in NEW.items():  # the pages the Hub added later
        if (only and title not in only) or find(title): continue
        try:
            made = send('POST', '/rest/api/content', {'type': 'page', 'title': title, 'space': {'key': SPACE}, 'ancestors': [{'id': find(parent)}],
                                                       'body': {'storage': {'value': texts[title][1], 'representation': 'storage'}}})
            ids[title] = made['id']; created.add(title); done += 1; print(f'{title}: created under {parent}')
        except HTTPError as e:
            failed += 1; print(f'{title}: NOT created ({e.code} {e.reason})')
    for title, (page_id, body) in texts.items():
        if (only and title not in only) or title in created: continue
        page_id = page_id or find(title)
        if not page_id: print(f'{title}: not in Confluence, left alone'); continue
        try:
            current = json.loads(http('GET', f'{base}/rest/api/content/{page_id}?expand=version', head)[1])
            update = {'id': page_id, 'type': 'page', 'title': current['title'], 'body': {'storage': {'value': body, 'representation': 'storage'}},
                      'version': {'number': current['version']['number'] + 1, 'message': 'Creative Hub text, replacing the March placeholder'}}
            parent = find(MOVES[title]) if title in MOVES else ''
            if parent: update['ancestors'] = [{'id': parent}]
            send('PUT', f'/rest/api/content/{page_id}', update)
            done += 1; print(f'{title}: text updated' + (f', moved under {MOVES[title]}' if parent else ''))
        except HTTPError as e:
            failed += 1; print(f'{title}: FAILED ({e.code} {e.reason})')
    print(f'Done: {done} changes' + (f', {failed} failed' if failed else '') + '. Page history keeps the old text.')

if __name__ == '__main__':
    apply() if '--apply' in sys.argv else write()
