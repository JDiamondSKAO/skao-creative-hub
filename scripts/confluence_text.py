"""The Hub's own text for each Confluence page, in Confluence's storage format, to replace the March placeholders.

  python3 scripts/confluence_text.py                       # write release/go-live/page-text/<Confluence title>.xml to review
  python3 scripts/confluence_text.py --apply               # put that text on the pages (asks for your Confluence token)
  python3 scripts/confluence_text.py --apply "Letterheads" # only the pages named

Staff on the Hub never see this text, because the theme shows its own. It is what Confluence's search and anyone opening
the page in Confluence itself see. It comes from the build's article copies (content/, run scripts/build.py first), with
the theme's furniture left out: icons, buttons' arrows, labels and empty slots. Where the Hub lists a page's files, the
Confluence page gets an Attachments macro instead (approved files only, except on the site progress pages).
Each update is a new page version, so page history can bring the old text back. Pages in hidden sections and pages not
yet in Confluence are left alone.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
import getpass, json, os, sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import links
OUT = ROOT / 'release' / 'go-live' / 'page-text'
KEEP = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'br', 'code', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'}
RENAME = {'b': 'strong', 'i': 'em', 'summary': 'h3', 'dt': 'h4', 'h1': 'h2'}
BLOCK = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'}
DROP = {'svg', 'script', 'style', 'button', 'form', 'input', 'select', 'textarea', 'img', 'picture', 'video', 'iframe', 'dialog'}
VOID = {'br', 'img', 'input', 'hr', 'meta', 'link', 'source'}
FURNITURE = ('eyebrow', 'arr', 'kicker', 'chip', 'badge', 'visually-hidden', 'sr-only')

def esc(text, quote=False):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text.replace('"', '&quot;') if quote else text

def macro(labels):
    """Confluence's own list of the page's files."""
    param = f'<ac:parameter ac:name="labels">{labels}</ac:parameter>' if labels else ''
    return f'<ac:structured-macro ac:name="attachments">{param}</ac:structured-macro>'

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
            self.close_para(); self.out.append(macro('' if 'data-attachments' in a else 'approved'))
        if (tag in DROP or 'hidden' in a or a.get('aria-hidden') == 'true' or 'data-downloads-slot' in a
                or 'data-attachments' in a or any(c in FURNITURE for c in classes)):
            if tag not in VOID: self.skip = 1
            return
        tag = RENAME.get(tag, tag)
        if tag not in KEEP:
            return  # layout: keep what is inside
        if tag in BLOCK:
            self.close_para()
        elif not self.in_block():
            self.open_para()
        if tag == 'a':
            if self.para and self.out and self.out[-1] == '</a>':
                self.close_para(); self.open_para()  # links side by side (cards, previous and next) get a line each
            href = a.get('href') or ''
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

def pages():
    """(Confluence title, page id or '', storage text) for every page the Hub shows, in route order."""
    routes = json.loads((ROOT / 'evidence' / 'interior-route-map.json').read_text())
    from polish import HIDDEN
    from interiors import PLANNED
    found = links.load()
    for name, meta in routes.items():
        src = ROOT / 'content' / name.replace('.html', '-confluence.html')
        if name in HIDDEN or not src.exists(): continue
        html = links.strip_pending(links.fill(src.read_text(), found))
        parser = Storage(); parser.feed(html)
        body = parser.result()
        ET.fromstring(f'<root xmlns:ac="http://atlassian.com/content">{body}</root>')  # must be well-formed
        yield meta['source_title'], ('' if meta['id'] in PLANNED else meta['id']), body

def write():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*.xml'): old.unlink()
    n = 0
    for title, _, body in pages():
        (OUT / (title.replace('/', '-') + '.xml')).write_text(body); n += 1
    print(f'{n} pages written to {OUT.relative_to(ROOT)}. Read a few, then run with --apply.')

def apply():
    from canto_sync import http
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    base = (os.environ.get('CONFLUENCE_BASE') or 'https://confluence.skatelescope.org').rstrip('/')
    token = os.environ.get('CONFLUENCE_TOKEN') or getpass.getpass('Confluence personal access token (it will not show): ').strip() or sys.exit('No token given.')
    head = {'Authorization': f'Bearer {token}', 'X-Atlassian-Token': 'nocheck', 'Accept': 'application/json'}
    get = lambda path: json.loads(http('GET', base + path, head)[1])
    done = failed = 0
    for title, page_id, body in pages():
        if only and title not in only: continue
        try:
            if not page_id:
                hits = get('/rest/api/content?' + urlencode({'spaceKey': 'CRH', 'title': title, 'type': 'page'})).get('results', [])
                if not hits: print(f'{title}: not in Confluence yet, left alone'); continue
                page_id = hits[0]['id']
            current = get(f'/rest/api/content/{page_id}?expand=version')
            update = {'id': page_id, 'type': 'page', 'title': current['title'],
                      'version': {'number': current['version']['number'] + 1, 'message': 'Creative Hub text, replacing the March placeholder'},
                      'body': {'storage': {'value': body, 'representation': 'storage'}}}
            http('PUT', f'{base}/rest/api/content/{page_id}', {**head, 'Content-Type': 'application/json'}, json.dumps(update).encode())
            done += 1; print(f'{title}: updated')
        except HTTPError as e:
            failed += 1; print(f'{title}: FAILED ({e.code} {e.reason})')
    print(f'Updated {done} pages' + (f', {failed} failed' if failed else '') + '. Page history keeps the old text.')

if __name__ == '__main__':
    apply() if '--apply' in sys.argv else write()
