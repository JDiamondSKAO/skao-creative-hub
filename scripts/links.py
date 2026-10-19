"""Links to internal documents and forms the Hub points at.

The addresses live in dev/links.json, which is gitignored: this repo is public,
and some of these documents open for anyone who has the link. Only the release
build (scripts/package.py, which sets HUB_LOCAL_LINKS) and local test mode read
that file, so the committed preview and page.vm never carry an address.

A link with no address shows as a "link to follow" placeholder in the preview,
so nothing points at a guessed address. The production theme leaves out
whatever still waits for a link, so staff never see a placeholder.
"""
import html, json, os, re
from pathlib import Path

LOCAL = Path(__file__).resolve().parents[1] / 'dev' / 'links.json'

NAMES = {
 'GOOGLE_SLIDES': 'SKAO template in Google Slides',
 'LOGO_REQUEST_FORM': 'Logo use request form, for people outside the SKAO',
 'AI_POLICY': 'SKAO AI policy pages',
 'IT_SERVICE_DESK': 'IT service desk, for email signatures',
 'CONSTRUCTION_STATUS': 'Overall construction status for both telescopes (Google Doc)',
 'LOW_STATUS': 'SKA-Low status slides, kept by the SKA-Low team (Google Slides)',
 'MID_STATUS': 'SKA-Mid status slides, kept by the SKA-Mid team (Google Slides)',
 'ALLHANDS': 'Canto folder of photos shared at the weekly all-hands, sorted into subfolders',
}

def load():
 """Addresses from dev/links.json, checked against NAMES."""
 urls = json.loads(LOCAL.read_text()) if LOCAL.exists() else {}
 unknown = set(urls) - set(NAMES)
 assert not unknown, f'unknown links in dev/links.json: {sorted(unknown)}'
 return {k: v for k, v in urls.items() if v}

URLS = load() if os.environ.get('HUB_LOCAL_LINKS') else {}

def url(name):
 assert name in NAMES, name
 return URLS.get(name)

def anchor(href, label, cls='text-link'):
 return f'<a href="{html.escape(href, quote=True)}" class="{cls}">{label} ↗</a>'

def pending(name, label, cls='text-link'):
 """A link when the address is known, otherwise the label marked as still to come."""
 href = url(name)
 if href:
  return anchor(href, label, cls)
 return f'<span class="pending-link" data-link="{name}" data-class="{cls}" title="Link to follow">{label} <small>link to follow</small></span>'

def fill(page, urls):
 """Local test mode: swap placeholders for the addresses in dev/links.json."""
 def swap(m):
  href = urls.get(m.group(1))
  return anchor(href, m.group(3), m.group(2)) if href else m.group(0)
 return re.sub(r'<span class="pending-link" data-link="(\w+)" data-class="([^"]*)" title="Link to follow">(.*?) <small>link to follow</small></span>', swap, page, flags=re.S)

def needs(fragment, *ready):
 """Content that only makes sense once its links exist: marked so production leaves it out."""
 return fragment if all(ready) else f'<!--pending-->{fragment}<!--/pending-->'

def strip_pending(page):
 """Production: drop marked content and any placeholder that is still waiting for its link."""
 page = re.sub(r'<!--pending-->.*?<!--/pending-->', '', page, flags=re.S)
 return re.sub(r'<span class="pending-link"[^>]*>.*?</small></span>', '', page, flags=re.S)
