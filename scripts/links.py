"""Links the Hub still needs from the brand owner.

Each one left as None shows a visible "link to follow" placeholder in the page,
so nothing points at a guessed address. Fill in the URL and rebuild.
"""
import html

GOOGLE_SLIDES = None      # SKAO template in Google Slides
LOGO_REQUEST_FORM = None  # Logo use request form, for people outside the SKAO
AI_POLICY = None          # SKAO AI policy pages
IT_SERVICE_DESK = None    # IT service desk, for email signatures

def pending(url, label, cls='text-link'):
 """A link when the address is known, otherwise the label marked as still to come."""
 if url:
  return f'<a href="{html.escape(url, quote=True)}" class="{cls}">{label} ↗</a>'
 return f'<span class="pending-link" title="Link to follow">{label} <small>link to follow</small></span>'
