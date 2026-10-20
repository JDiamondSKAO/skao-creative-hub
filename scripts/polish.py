"""Visual and journey layer on top of the reviewed pages.

Adds section navigation, related pages, resource panels, Latest files and the
homepage search and latest-assets bands. It only reorganises reviewed content;
it never invents files or availability.
"""
import html, json, re
from gethelp import MOVED
from interiors import PLANNED
import brandkit, links

def text(fragment):
 fragment = re.sub(r'<span[^>]*aria-hidden="?true"?[^>]*>.*?</span>', '', fragment, flags=re.S)
 # Tags become spaces, so a link right before a comma would leave "times , and".
 return re.sub(r'\s+([,.;:!?])', r'\1', re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment)))).strip()

def summary(body):
 # A page can name its own one-line summary when its first paragraph isn't one.
 own = re.search(r'data-summary="([^"]*)"', body)
 if own: return html.unescape(own.group(1))
 m = re.search(r'<div class="task-intro[^"]*">.*?<p[^>]*>(.*?)</p>', body, re.S) or re.search(r'<p[^>]*>(.*?)</p>', body, re.S)
 return text(m.group(1)) if m else ''

SEARCH_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'

# Information architecture: the top menu, sidebars, landing directories and
# homepage all use these sections and groups, so staff meet one structure.
# (key, menu label, landing page, [(group, [pages])]). A page listed in more
# than one section belongs to the first; later listings are cross-links.
SECTIONS = [
 ('presentations', 'Presentations', 'presentations.html', [
  ('Templates', ['standard-template.html', 'partner-templates.html']),
  ('Slide decks', ['master-deck.html']),
  ('Site progress', ['site-progress.html', 'low-slides.html', 'mid-slides.html']),
  ('How to', ['formatting-slides.html'])]),
 ('documents', 'Documents', 'documents.html', [
  ('Templates', ['letterheads.html', 'memos.html']),
  ('Posters', ['poster-templates.html'])]),
 ('brand', 'Brand', 'brand.html', [
  ('Artwork and files', ['logos.html', 'partner-logos.html', 'fonts.html', 'brand-book.html']),
  ('Using the brand', ['logo-guidance.html', 'colours-and-type.html', 'brand-in-practice.html']),
  ('Partner brands', ['co-branding-csiro.html', 'co-branding-sarao.html'])]),
 ('media', 'Photos and video', 'media.html', [
  ('Find and use media', ['canto-access.html', 'video.html', 'image-usage.html'])]),
 ('events', 'Events', 'events.html', [
  ('Materials', ['stands.html'])]),
 ('guides', 'How-to guides', 'self-service.html', [
  ('Print and posters', ['making-a-poster.html', 'print-preparation.html', 'print-suppliers.html']),
  ('Good practice', ['accessibility.html', 'firefly.html'])]),
]
# Pages that belong to a section without being listed (duplicate source titles).
EXTRA = {}
# Pages that sit under another page in their group: listed beneath it, indented, by a short name.
CHILDREN = {'site-progress.html': [('low-slides.html', 'SKA-Low'), ('mid-slides.html', 'SKA-Mid')]}
CHILD_OF = {c: parent for parent, kids in CHILDREN.items() for c, _ in kids}

def members_of(section):
 key, label, landing, groups = section
 out = [landing]
 for g, pages in groups:
  out += [p for p in pages if p not in out]
 return out

# Where a cross-listed page lives when first listing is not its natural home.
HOME = {}

def section_of(name):
 """Primary section of a page: (key, label, landing, members, groups)."""
 for sec in sorted(SECTIONS, key=lambda x: x[0] != HOME.get(name)):
  if name in members_of(sec) or EXTRA.get(name) == sec[0]:
   key, label, landing, groups = sec
   return key, label, landing, members_of(sec), groups
 return None

def primary(name, key):
 sec = section_of(name)
 return bool(sec) and sec[0] == key

# Latest files filters by the Hub's own sections, so a page sits under the same name everywhere.
TYPES = [(key, label) for key, label, _, _ in SECTIONS]

# Side menus fold away to give the page more room: section pages on the left, "On this page" on the right.
PANEL_LEFT = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16"/></svg>')
PANEL_RIGHT = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M15 4v16"/></svg>')
TOC_RAIL = ('<aside class="toc-rail" hidden><div class="toc-head"><strong id="tocHeading">On this page</strong>'
 '<button type="button" class="rail-toggle" data-rail="toc" aria-controls="toc" aria-expanded="true" aria-label="Hide On this page" title="Hide On this page">' + PANEL_RIGHT + '</button></div>'
 '<nav id="toc" class="toc" aria-labelledby="tocHeading"></nav></aside>')

def sidebar(current, titles):
 sec = section_of(current)
 out = ('<aside class="sidebar"><button type="button" class="rail-toggle" data-rail="nav" aria-controls="sectionNav" aria-expanded="true" aria-label="Hide the section menu" title="Hide the section menu">'
  + PANEL_LEFT + '</button>')
 if sec:
  key, label, landing, members, groups = sec
  # Every page is listed: sections are short, so nothing hides behind a toggle. The heading is a
  # heading, "Overview" is the landing page, and small capitals only ever mean a group label.
  out += (f'<nav class="section-nav" id="sectionNav" aria-label="{label} pages"><h2>{label}</h2>'
   f'<ul class="nav-overview"><li><a class="section-home" href="{landing}" title="{html.escape(titles[landing])}">Overview</a></li></ul>')
  for g, pages in groups:
   out += (f'<div class="nav-group"><h3>{g}</h3><ul>'
    + ''.join(f'<li><a href="{m}">{html.escape(titles[m])}</a>' + (
      '<ul class="nav-children">' + ''.join(f'<li><a href="{c}" title="{html.escape(titles[c])}">{short}</a></li>' for c, short in CHILDREN[m]) + '</ul>'
      if m in CHILDREN else '') + '</li>' for m in pages if m not in CHILD_OF) + '</ul></div>')
  out += '</nav>'
 else:
  out += '<nav class="section-nav" id="sectionNav" aria-label="Hub sections"><h2>Sections</h2><ul>' + ''.join(
   f'<li><a href="{landing}">{label}</a></li>' for key, label, landing, _ in SECTIONS) + '<li><a href="resources.html">Latest files</a></li></ul></nav>'
 return out + '</aside>'

def related(name, pages, summaries):
 sec = section_of(name)
 if not sec: return ''
 key, label, landing, members, groups = sec
 if name == landing: return ''
 if True:
  rest = [m for m in members if m != landing and primary(m, key)]
  at = rest.index(name) if name in rest else -1
  picks = [rest[(at + i) % len(rest)] for i in range(1, min(4, len(rest)))] if rest else []
  heading = 'More in ' + label
 cards = ''.join(
  f'<a class="related-card" href="{m}">' +
  f'<strong>{html.escape(pages[m][0])}</strong><span>{html.escape(summaries[m])}</span></a>' for i, m in enumerate(picks))
 more = f'<a class="related-all" href="{landing}">{html.escape(pages[landing][0])} →</a>'
 # Wide screens: a quiet previous and next pair, since the sidebar already lists the section.
 # Phones have no sidebar, so they keep the "More in" list.
 prev = rest[at - 1] if at > 0 else None
 nxt = rest[at + 1] if 0 <= at < len(rest) - 1 else None
 pager = ''
 if prev or nxt:
  pager = (f'<nav class="page-pager" aria-label="Previous and next in {label}">'
   + (f'<a class="pager-prev" href="{prev}" rel="prev"><span aria-hidden="true">←</span>{html.escape(pages[prev][0])}</a>' if prev else '<span></span>')
   + (f'<a class="pager-next" href="{nxt}" rel="next">{html.escape(pages[nxt][0])}<span aria-hidden="true">→</span></a>' if nxt else '')
   + '</nav>')
 return pager + f'<nav class="section-next" aria-label="{heading}"><div class="section-next-head"><h2>{heading}</h2>{more}</div><div class="related-grid">{cards}</div></nav>'

# Resource pages: one panel with purpose, status and how to get the file.
ASSET_KIND = {'presentations': ('slides', 'Presentation', 'formatting-slides.html', 'How to format a presentation'),
 'documents': ('document', 'Document template', 'brand-in-practice.html', 'Apply the brand'),
 'brand': ('brand', 'Brand artwork', 'logo-guidance.html', 'Using the SKAO logo')}
ART = {'slides': '<span class="art-slide"><i>SKA Observatory</i><b>A shared story.</b></span>',
 'document': '<span class="art-doc"><b>SKAO</b><i></i><i></i><i></i></span>',
 'brand': '<span class="art-brand"><b>Aa</b><i></i><em></em></span>'}

# Who signs off the files labelled "approved" on a resource page.
APPROVER = 'Communications'
# Links beside the guide link on a resource page's card.
CARD_LINKS = {'standard-template.html': [('partner-templates.html', 'Partner templates')],
 'logos.html': [('partner-logos.html', 'Partner logos')],
 'partner-logos.html': [('logos.html', 'SKAO logos')]}

def asset_panel(name, body, jira):
 m = re.search(r'<div class="task-intro"><div>(?:<span class="eyebrow">.*?</span>)?<p>(.*?)</p></div></div>', body, re.S)
 n = re.search(r'<aside class="availability-note".*?</aside>', body, re.S)
 if not (m and n): return body
 sec = section_of(name)
 kind, label, guide, guide_label = ASSET_KIND.get(sec[0] if sec else '', ASSET_KIND['documents'])
 if name == 'poster-templates.html': guide, guide_label = 'making-a-poster.html', 'Prepare a poster'
 facts = brandkit.PACK.get(name, [])
 # Version, date and approver come from the approved files themselves, so they are hidden until those load.
 release = [('version', 'Version', ''), ('updated', 'Last updated', ''), ('approved', 'Approved by', APPROVER)]
 if any(l.lower() == 'edition' for l, _ in facts): release = release[1:]
 card_links = ''.join(f'<a class="text-link" href="{h}">{t}</a>' for h, t in [(guide, guide_label)] + CARD_LINKS.get(name, []))
 panel = (f'<div class="task-intro asset-panel" data-page-id="{STATE["ids"].get(name, "")}"><div class="asset-art {kind}" aria-hidden="true">{ART[kind]}</div><div class="asset-info">'
  f'<span class="eyebrow">{label}</span><p class="asset-purpose">{m.group(1)}</p>'
  '<dl class="asset-facts"><div class="how-to-get"><dt>Availability</dt><dd>Not yet available to download. The files appear here once they are approved.</dd></div>'
  + ''.join(links.needs(f'<div data-fact="{label.lower()}"><dt>{label}</dt><dd>' + ('<ul class="variant-list">' + ''.join(f'<li>{v}</li>' for v in value) + '</ul>' if isinstance(value, list) else value) + '</dd></div>',
    'pending-link' not in str(value)) for label, value in facts)
  + ''.join(f'<div data-fact="{key}" class="release-fact" hidden><dt>{label}</dt><dd>{value}</dd></div>' for key, label, value in release) + '</dl>'
  f'<div class="asset-actions">{card_links}</div>'
  '<div class="asset-downloads" data-downloads hidden></div></div></div>')
 body = body.replace(m.group(0), panel).replace(n.group(0), '')
 return re.sub(r'<aside class="next-step"><div><h2>Choose a different starting point</h2>.*?</aside>', '', body, flags=re.S)

def feed(pages, meta):
 """Latest files: every approved file in the Hub and the site teams' progress slides, newest first.
 main.js fills it from Confluence. Each file shows the page it's on and that page's Hub section, so
 the page map below covers every route by ID and by title (Confluence titles in production)."""
 where = {}
 for name, m in meta.items():
  home = MOVED.get(name, (name,))[0].split('#')[0]
  sec = section_of(home)
  if not sec or home not in pages: continue
  row = [sec[0], pages[home][0]]
  # Pages not yet in Confluence only have stand-in IDs, so they are found by title.
  if m['id'] not in PLANNED: where['i:' + m['id']] = row
  for t in (m['source_title'], pages[name][0]): where['t:' + t.lower()] = row
 sites = [meta[n]['id'] for n in ('low-slides.html', 'mid-slides.html')]
 return ('<section class="file-feed" data-file-feed aria-label="Latest files"'
  f' data-pages="{html.escape(json.dumps(where, separators=(",", ":")), quote=True)}"'
  f' data-sections="{html.escape(json.dumps(TYPES, separators=(",", ":")), quote=True)}"'
  f' data-site-pages="{html.escape(json.dumps(sites), quote=True)}">'
  '<div class="catalogue-bar"><label class="catalogue-search">' + SEARCH_ICON + '<span class="visually-hidden">Search the latest files</span>'
  '<input id="fileFilter" type="search" autocomplete="off" placeholder="Search files, e.g. letterhead or logo"></label></div>'
  '<div class="type-chips" role="group" aria-label="Show a section" hidden></div>'
  '<p id="feedStatus" class="filter-status" role="status"></p>'
  '<div class="feed-body" data-feed-list></div>'
  '<div id="feedEmpty" class="catalogue-empty" hidden><p>No files match that search.</p><button type="button" id="clearFeed" class="button secondary">Show everything</button></div></section>')

def request_routes(body, jira):
 """Two clear routes first: submit a brief, or write one with the helper."""
 body = re.sub(r'(<div class="task-intro">.*?</div>)<a href="[^"]*" class="button">Open the Comms helpdesk ↗</a>(</div>)', r'\1\2', body, count=1, flags=re.S)
 body = body.replace('Already have a brief? Send it through the Comms helpdesk with your files or source links.', 'Choose how you want to start. Either way, the team replies to agree the scope and timing with you.', 1)
 routes = (f'<div class="route-choice"><a class="route-card primary" href="{jira}"><span class="eyebrow">I have a brief</span><strong>Submit it in the helpdesk</strong><span>Attach your files or source links. The team replies to agree scope and timing.</span><em>Open the Comms helpdesk ↗</em></a>'
  '<a class="route-card" href="#brief-builder" data-open-details><span class="eyebrow">I need help</span><strong>Write my brief here</strong><span>Answer six short questions, then copy the result into the helpdesk.</span><em>Start the brief helper ↓</em></a></div>')
 body = body.replace('<div class="process-strip">', routes + '<div class="process-strip">', 1)
 return body.replace('<details class="brief-builder">', '<details class="brief-builder" id="brief-builder">', 1)

STATE = {}  # titles and summaries, filled by revise() for the header menus

def row_meta(m, key):
 if not primary(m, key): return '<span class="dir-meta">In ' + section_of(m)[1] + '</span>'
 return ''

def directory(name, pages, summaries):
 """A section as grouped link lists: label left, title and summary right."""
 key, label, landing, members, groups = section_of(name)
 out = '<div class="directory">'
 for g, items in groups:
  # Each group can be linked to, e.g. presentations.html#site-progress.
  out += f'<section class="dir-group" id="{re.sub(r"[^a-z0-9]+", "-", g.lower()).strip("-")}"><h2>{g}</h2><ul class="dir-list">'
  for m in items:
   if m in CHILD_OF: continue  # the parent page leads to its children
   out += (f'<li><a class="dir-row" href="{m}" data-page-id="{STATE["ids"].get(m, "")}"><span class="dir-text"><strong>{html.escape(pages[m][0])}</strong>'
    f'<span>{html.escape(summaries[m])}</span></span>{row_meta(m, key)}</a></li>')
  out += '</ul></section>'
 return out + '</div>'

def unfold(body):
 """Landing pages show their short advice instead of hiding it."""
 def open_detail(m):
  inner = m.group(2)
  if '<h2' in inner: return f'<section class="landing-note">{inner}</section>'
  return f'<section class="landing-note"><h2>{m.group(1)}</h2>{inner}</section>'
 return re.sub(r'<details class="guidance-detail"><summary>(.*?)</summary><div>(.*?)</div></details>', open_detail, body, flags=re.S)

VOID = {'br', 'img', 'input', 'hr', 'meta', 'link', 'source', 'wbr'}

def top_level(fragment):
 """Split an HTML fragment into its top-level elements."""
 parts, depth, start = [], 0, None
 for m in re.finditer(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*?(/?)>', fragment):
  closing, tag, selfclose = m.group(1), m.group(2).lower(), m.group(3)
  if tag in VOID or selfclose: continue
  if not closing:
   if depth == 0: start = m.start()
   depth += 1
  else:
   depth -= 1
   if depth == 0 and start is not None:
    parts.append(fragment[start:m.end()]); start = None
 return parts

# Help panel items come in three kinds, each with its own tint: guidance to know,
# checks to run through, and a prompt to ask the team.
def rail_kind(title, body):
 if '<ol' in body or '<ul' in body: return 'check'
 return 'ask' if title.rstrip().endswith('?') else 'info'

def rail_links(body):
 """Links left loose at the end of a panel item ("A · B") become a row of small buttons."""
 run = r'(?:<a [^>]*>(?:(?!</a>).)*</a>\s*(?:·\s*)?)+'
 return re.sub('(' + run + r')(?=\s*</(?:section|div|aside)>)',
  lambda m: '<p class="rail-links">' + re.sub(r'</a>\s*·\s*', '</a>', m.group(1)).strip() + '</p>', body, flags=re.S)

def rail(rest):
 """Status and advice beside the list: headings visible, detail on demand."""
 items = []
 for el in top_level(rest):
  if 'responsibility-split' in el[:60]:
   title, body = 'Who does what', el
  else:
   h = re.search(r'<h2[^>]*>(.*?)</h2>', el, re.S)
   if not h: continue
   title, body = text(h.group(1)), el.replace(h.group(0), '', 1)
  body = re.sub(r'<span class="eyebrow">.*?</span>', '', body, count=1, flags=re.S)
  items.append((title, body))
 if not items: return ''
 out = '<aside class="landing-rail" aria-label="Help with this section">'
 if items:
  out += ('<div class="rail-guides"><h2 class="rail-title">Before you start</h2>') + ''.join(
   # One item reads open; several start closed, so the panel stays compact beside a short list.
   f'<details class="rail-item" data-kind="{rail_kind(t, b)}"{" open" if len(items) == 1 else ""}><summary>'
   f'<span class="rail-label">{html.escape(t)}</span></summary><div class="rail-body">{rail_links(b)}</div></details>'
   for i, (t, b) in enumerate(items)) + '</div>'
 return out + '</aside>'

def landing(name, body, pages, summaries):
 # Cards that only pointed at a few section pages give way to the full directory.
 body = re.sub(r'<details class="guidance-detail"><summary>[^<]*</summary><div><div class="choice-grid">.*?</details>', '', body, flags=re.S)
 body = re.sub(r'<div class="choice-grid">(?:<a class="choice-card".*?</a>)+</div>', '', body, count=1, flags=re.S)
 body = unfold(body)
 d = directory(name, pages, summaries)
 # Quick answers (brand swatches, the Canto hand-off) stay first; the directory follows.
 def after(head, rest, beside=False):
  # Sections marked data-landing-main (the Events lead times, say) stay under the list, not in the rail.
  keep = [el for el in top_level(rest) if 'data-landing-main' in el[:200]]
  for el in keep: rest = rest.replace(el, '', 1)
  main = d + ''.join(keep)
  side = rail(rest.strip())
  if side and beside:
   # "Before you start" sits level with the intro, at the top of the page, rather than halfway down.
   return f'<div class="landing-layout"><div class="landing-main">{head}{main}</div>{side}</div>'
  return head + (f'<div class="landing-layout"><div class="landing-main">{main}</div>{side}</div>' if side else main)
 for marker in ['<div class="type-spec">', '<div class="media-handoff">']:
  at = body.find(marker)
  if at >= 0:
   close = body.find('</div></div>', at) + 12
   return after(body[:close], body[close:])
 m = re.search(r'<div class="task-intro">.*?</div>(?:<a [^>]*class="button"[^>]*>.*?</a>)?</div>', body, re.S)
 return after(body[:m.end()], body[m.end():], beside=True) if m else d + body

def nav(current=''):
 """Top menu: one link per section. The landing page lists everything in it."""
 cur = section_of(current)
 out = ''
 for key, label, landing_page, groups in SECTIONS:
  state = ' aria-current="page"' if current == landing_page else ' aria-current="true"' if cur and cur[0] == key else ''
  out += f'<a href="{landing_page}" data-label="{label}"{state}>{label}</a>'
 return out

# Pages shown full width: they list a whole section, so a sidebar would repeat them.
FULL_WIDTH = {sec[2] for sec in SECTIONS} | {'resources.html', 'faq.html'}

TILES = [
 ('presentations', 'slides', 'Templates, approved decks and site progress.', ['standard-template.html', 'master-deck.html', 'site-progress.html']),
 ('documents', 'document', 'Letterheads, memos, reports and posters.', ['letterheads.html', 'memos.html', 'poster-templates.html']),
 ('brand', 'brand', 'Logos, colours, fonts and partner rules.', ['logos.html', 'colours-and-type.html', 'fonts.html']),
 ('media', 'media', 'Photography and footage in Canto.', ['canto-access.html', 'video.html', 'image-usage.html']),
 ('events', 'events', 'Stands, print and merchandise for events.', ['stands.html']),
 ('guides', 'guides', 'Do-it-yourself checks for common jobs.', ['making-a-poster.html', 'print-preparation.html', 'accessibility.html']),
]
TILE_ART = {**ART,
 'events': '<span class="art-events"><i></i><b>SKAO</b><em></em></span>',
 'guides': '<span class="art-guides"><i></i><i></i><i></i></span>',
 'media': '<span class="art-media"><i></i><b></b><em></em></span>'}

def home_tiles(home, titles):
 """A compact index of the sections: small picture, name and what is inside."""
 art = TILE_ART
 out = '<ul class="section-index">'
 for key, kind, desc, links in TILES:
  sec = next(x for x in SECTIONS if x[0] == key)
  out += (f'<li><a class="index-item kind-{kind}" href="{sec[2]}"><span class="index-art" aria-hidden="true">{art[kind]}</span>'
   f'<span class="index-text"><strong>{sec[1]}</strong><span>{desc}</span></span></a></li>')
 return out + '</ul>'


def latest_strip():
 """One quiet line of the newest files; hidden until there is something to show."""
 return ('<section class="latest-strip" id="latestStrip" aria-labelledby="latestHeading" hidden><div class="strip-label"><h2 id="latestHeading">Just added</h2>'
  '<p class="latest-lead" id="latestLead">Newest approved files</p></div>'
  '<div id="latestAssets" class="strip-items" data-approval-label="approved"></div>'
  '<a class="strip-all" href="resources.html">See all <span aria-hidden="true">→</span></a></section>')

# Canto showcase slots: the gallery on Photos and video, and strips on topic pages
# matched to album names. They stay hidden until the synced manifest has matching albums.
CANTO_STRIPS = {'video.html': 'video videos'}

def canto_show(words, heading, eyebrow='', wide=False):
 """A view-only slideshow: it shows what is in Canto; the button beside it opens the library."""
 return (f'<section class="canto-show{" wide" if wide else ""}" data-canto="{words}" hidden aria-labelledby="show-{words.split()[0] if words else "all"}">'
  f'<div class="canto-head"><div>' + (f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else '') + f'<h2 id="show-{words.split()[0] if words else "all"}">{heading}</h2></div></div>'
  '<div class="show-stage" aria-roledescription="carousel"><ul class="show-slides" aria-live="off"></ul>'
  '<div class="show-controls"><button type="button" class="show-prev" aria-label="Previous image"><span aria-hidden="true">‹</span></button>'
  '<button type="button" class="show-play" aria-label="Pause slideshow" aria-pressed="false"><span aria-hidden="true"></span></button>'
  '<button type="button" class="show-next" aria-label="Next image"><span aria-hidden="true">›</span></button></div></div>'
  '<div class="show-dots" role="group" aria-label="Choose an image"></div>'
  '<div class="show-foot"><p class="show-note">A few of the approved images in the library. Open Canto to search everything, see each credit and download.'
  + (' First time? Choose <strong>Register Now</strong> and use your SKAO email address.' if wide else '') + '</p></div>'
  '</section>')

PHOTOS_ICON = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
 '<rect x="3" y="7" width="14" height="12" rx="2"/><path d="M7 4h11a3 3 0 0 1 3 3v9"/><circle cx="8" cy="11" r="1.4"/><path d="m3.5 17 4-4 3.5 3.5 2-2 3.5 3.5"/></svg>')

def site_photos():
 """Weekly all-hands photos: one link to where they are stored."""
 return links.needs('<section class="site-photos"><span class="site-photos-icon">' + PHOTOS_ICON + '</span>'
  '<div><p class="eyebrow">From the sites · New each week</p><h2>Weekly all-hands photos</h2>'
  '<p>Photos from each site’s weekly all-hands update, in the staff media library.</p></div>'
  + links.pending('ALLHANDS', 'See the all-hands photos', 'button secondary') + '</section>', links.url('ALLHANDS'))

def deck_library():
 """Approved slide decks: search, topics and sort, then the decks. main.js fills the list."""
 return ('<section class="deck-library" data-deck-library aria-label="Approved slide decks">'
  '<div class="catalogue-bar"><label class="catalogue-search">' + SEARCH_ICON + '<span class="visually-hidden">Search the decks</span>'
  '<input id="deckFilter" type="search" autocomplete="off" placeholder="Search by title, event or speaker"></label>'
  '<label class="deck-sort"><span>Sort</span><select id="deckSort"><option value="new">Newest first</option><option value="old">Oldest first</option><option value="az">A to Z</option></select></label></div>'
  '<div class="type-chips" role="group" aria-label="Show a topic" hidden></div>'
  '<p id="deckStatus" class="filter-status" role="status"></p>'
  '<ol class="deck-list-cards" data-deck-list></ol>'
  '<div id="deckEmpty" class="catalogue-empty" hidden><p>No decks match that search.</p><button type="button" id="clearDecks" class="button secondary">Show all decks</button></div></section>')

def canto_gallery(canto):
 return canto_show('', 'A look inside the staff media library', wide=True)

def canto_strip(words, canto):
 return canto_show(words, 'In the staff media library', 'From Canto')

def revise(pages, meta, jira, canto=''):
 pages = brandkit.apply(pages)
 titles = {n: t for n, (t, b) in pages.items()}
 summaries = {n: summary(b) for n, (t, b) in pages.items()}
 on_request = {n for n, (t, b) in pages.items() if 'availability-note' in b}
 STATE.update(titles=titles, summaries=summaries, on_request=on_request, jira=jira, ids={n: m['id'] for n, m in meta.items()})
 for name in meta:
  title, body = pages[name]
  if name in on_request: body = asset_panel(name, body, jira)
  if name == 'request.html': body = request_routes(body, jira)
  if name in brandkit.DOWNLOAD_GROUPS:
   view = brandkit.DOWNLOAD_VIEW.get(name, 'list')
   body = f'<div hidden data-dl-groups="{html.escape(json.dumps(brandkit.DOWNLOAD_GROUPS[name]), quote=True)}" data-dl-view="{view}"></div>' + body
  pages[name] = (title, body)
 landings = {sec[2] for sec in SECTIONS}
 for name in meta:
  title, body = pages[name]
  if name in landings: body = landing(name, body, pages, summaries)
  pages[name] = (title, body + related(name, pages, summaries))
 # Canto slots go in after the landing layout exists, so they never land in the side panel.
 title, body = pages['media.html']
 at = body.find('<div class="landing-layout">')
 pages['media.html'] = (title, body[:at] + canto_gallery(canto) + site_photos() + body[at:] if at >= 0 else body + canto_gallery(canto) + site_photos())
 title, body = pages['master-deck.html']
 assert '<div data-deck-library></div>' in body
 pages['master-deck.html'] = (title, body.replace('<div data-deck-library></div>', deck_library()))
 # The weekly all-hands photos have their own band on the construction pages too.
 for name in ('site-progress.html', 'low-slides.html', 'mid-slides.html'):
  title, body = pages[name]
  assert '<div data-site-photos></div>' in body, name
  pages[name] = (title, body.replace('<div data-site-photos></div>', site_photos()))
 for name, words in CANTO_STRIPS.items():
  title, body = pages[name]
  m = re.search(r'<div class="media-handoff">.*?</div></div>', body, re.S)
  pages[name] = (title, body[:m.end()] + canto_strip(words, canto) + body[m.end():] if m else body)
 title, body = pages['resources.html']
 body = body.replace('Choose a starting point. Open its source page to see the file, guidance or availability information.', 'New and updated files from across the Hub, newest first: templates, slide decks, logos and more.', 1)
 body = re.sub(r'<span class="eyebrow">[^<]*</span>', '', body, count=1)
 body = re.sub(r'<div class="choice-grid">(?:<a class="choice-card".*?</a>)+</div>', '', body, count=1, flags=re.S)
 body = re.sub(r'<aside class="next-step">.*?</aside>', '', body, flags=re.S)
 pages['resources.html'] = (title, body + feed(pages, meta))
 # Homepage: search first, then the latest approved files.
 title, home = pages['index.html']
 old = '<div class="actions"><a class="button" href="#library">Find a resource →</a></div>'
 assert old in home
 home = home.replace(old, '<form class="hero-search" data-hub-search role="search"><label for="heroSearch" class="visually-hidden">Search the Creative Hub</label>' + SEARCH_ICON +
  '<input id="heroSearch" type="search" autocomplete="off" placeholder="Search or ask, e.g. where’s the logo?"><button class="button" type="submit">Search</button></form>')
 home = re.sub(r'<div class="quick-library">.*?</div></section>', lambda m: home_tiles(home, titles) + '</section>', home, count=1, flags=re.S)
 home = home.replace('<h2>What do you need?</h2>', '<h2>Browse the Hub</h2>', 1).replace('<p class="eyebrow">01 / Find and reuse</p>', '', 1)
 home = home.replace('<span>Jump to</span>', '<span>Quick links</span>', 1)
 # The newest files take the promo card's place; the help band gives way to the footer's help row.
 home = home.replace('</section><section id="library"', '</section>' + latest_strip() + '<section id="library"', 1)
 home = re.sub(r'<section class="help-band journey-band">.*?</section>', '', home, count=1, flags=re.S)
 assert home.endswith('</div>')
 pages['index.html'] = (title, home)
 return pages, titles
