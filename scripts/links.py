"""Links the Hub still needs from the brand owner.

Each one left as None shows a visible "link to follow" placeholder in the
preview and local test mode, so nothing points at a guessed address. The
production theme (page.vm) leaves out whatever still waits for a link, so
staff never see a placeholder. Fill in the URL and rebuild.
"""
import html

GOOGLE_SLIDES = None      # SKAO template in Google Slides
LOGO_REQUEST_FORM = None  # Logo use request form, for people outside the SKAO
AI_POLICY = None          # SKAO AI policy pages
IT_SERVICE_DESK = None    # IT service desk, for email signatures
LOW_DASHBOARD = None      # SKA-Low construction dashboard, kept by the SKA-Low team
MID_DASHBOARD = None      # SKA-Mid construction dashboard, kept by the SKA-Mid team
ALLHANDS_LOW = None       # Canto album of SKA-Low photos shared at the weekly all-hands
ALLHANDS_MID = None       # Canto album of SKA-Mid photos shared at the weekly all-hands

def pending(url, label, cls='text-link'):
 """A link when the address is known, otherwise the label marked as still to come."""
 if url:
  return f'<a href="{html.escape(url, quote=True)}" class="{cls}">{label} ↗</a>'
 return f'<span class="pending-link" title="Link to follow">{label} <small>link to follow</small></span>'

def needs(fragment, *urls):
 """Content that only makes sense once its links exist: marked so production leaves it out."""
 return fragment if all(urls) else f'<!--pending-->{fragment}<!--/pending-->'

def strip_pending(page):
 """Production: drop marked content and any placeholder that is still waiting for its link."""
 import re
 page = re.sub(r'<!--pending-->.*?<!--/pending-->', '', page, flags=re.S)
 return re.sub(r'<span class="pending-link"[^>]*>.*?</small></span>', '', page, flags=re.S)
