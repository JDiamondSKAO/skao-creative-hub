"""Visual and journey layer on top of the reviewed pages.

Adds section navigation, related pages, resource panels, checklists, the
resource catalogue and the homepage search and latest-assets bands. It only
reorganises reviewed content; it never invents files or availability.
"""
import html, re

def text(fragment):
 fragment = re.sub(r'<span[^>]*aria-hidden="?true"?[^>]*>.*?</span>', '', fragment, flags=re.S)
 return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()

def summary(body):
 m = re.search(r'<div class="task-intro[^"]*">.*?<p[^>]*>(.*?)</p>', body, re.S) or re.search(r'<p[^>]*>(.*?)</p>', body, re.S)
 return text(m.group(1)) if m else ''

SEARCH_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'

# Information architecture: the top menu, sidebars, landing directories and
# homepage all use these sections and groups, so staff meet one structure.
# (key, menu label, landing page, [(group, [pages])]). A page listed in more
# than one section belongs to the first; later listings are cross-links.
SECTIONS = [
 ('presentations', 'Presentations', 'presentations.html', [
  ('Templates', ['standard-template.html', 'widescreen-template.html']),
  ('Decks to reuse', ['master-deck.html', 'science-slides.html', 'low-slides.html', 'mid-slides.html', 'construction-slides.html', 'specialised-slides.html']),
  ('How to', ['formatting-slides.html'])]),
 ('documents', 'Documents', 'documents.html', [
  ('Templates', ['letterheads.html', 'memos.html', 'reports.html', 'email-signatures.html']),
  ('Posters', ['poster-templates.html'])]),
 ('brand', 'Brand', 'brand.html', [
  ('Artwork and files', ['logos.html', 'fonts.html', 'brand-book.html']),
  ('Using the brand', ['logo-guidance.html', 'colours-and-type.html', 'brand-in-practice.html']),
  ('Partner brands', ['co-branding-csiro.html', 'co-branding-sarao.html'])]),
 ('media', 'Photos and video', 'media.html', [
  ('Photos', ['canto-access.html', 'hero-images.html', 'telescope-images.html', 'event-photos.html']),
  ('Video', ['video.html', 'b-roll.html', 'recordings.html', 'animations.html']),
  ('Using media', ['image-usage.html'])]),
 ('events', 'Events', 'events.html', [
  ('Plan', ['event-checklist.html', 'event-safety.html']),
  ('Materials', ['stands.html', 'merchandise.html', 'print.html'])]),
 ('guides', 'How-to guides', 'self-service.html', [
  ('Print and posters', ['making-a-poster.html', 'print-preparation.html']),
  ('Good practice', ['accessibility.html', 'firefly.html', 'formatting-slides.html'])]),
 ('help', 'Get help', 'working-with-us.html', [
  ('Ask the team', ['request.html', 'creative-services.html', 'timing.html']),
  ('Specific requests', ['video-request.html', 'print.html', 'print-suppliers.html', 'business-cards.html']),
  ('Help with the Hub', ['help.html', 'faq.html', 'contribute.html', 'updates.html', 'archive.html'])]),
]
# Pages that belong to a section without being listed (duplicate source titles).
EXTRA = {'canto-guide.html': 'media'}

def members_of(section):
 key, label, landing, groups = section
 out = [landing]
 for g, pages in groups:
  out += [p for p in pages if p not in out]
 return out

# Where a cross-listed page lives when first listing is not its natural home.
HOME = {'print.html': 'help'}

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

# Catalogue filters, in the order staff usually look for things.
TYPES = [
 ('presentations', 'Presentations', {'Presentations'}),
 ('documents', 'Documents', {'Documents', 'Resources'}),
 ('brand', 'Brand', {'Brand'}),
 ('media', 'Photos and video', {'Media'}),
 ('events', 'Events', {'Events'}),
 ('guides', 'How-to guides', {'Guidance'}),
 ('services', 'Creative services', {'Creative help'}),
]
SKIP = {'resources.html', 'request.html'}
CHECKLISTS = {'event-checklist.html', 'print-preparation.html', 'making-a-poster.html', 'accessibility.html'}

def sidebar(current, titles):
 sec = section_of(current)
 out = '<aside class="sidebar">'
 if sec:
  key, label, landing, members, groups = sec
  out += f'<nav class="section-nav" aria-label="{label} pages"><h2>{label}</h2><a class="section-home" href="{landing}">{html.escape(titles[landing])}</a>'
  for g, pages in groups:
   out += f'<h3>{g}</h3><ul>' + ''.join(f'<li><a href="{m}">{html.escape(titles[m])}</a></li>' for m in pages) + '</ul>'
  out += '</nav>'
 else:
  out += '<nav class="section-nav" aria-label="Hub sections"><h2>Sections</h2><ul>' + ''.join(
   f'<li><a href="{landing}">{label}</a></li>' for key, label, landing, _ in SECTIONS) + '<li><a href="resources.html">Everything in the Hub</a></li></ul></nav>'
 return out + '<nav id="toc" class="toc" aria-label="On this page"></nav></aside>'

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
  f'<a class="related-card" href="{m}">' + ('<span class="related-next">Next</span>' if i == 0 and name != landing else '') +
  f'<strong>{html.escape(pages[m][0])}</strong><span>{html.escape(summaries[m])}</span></a>' for i, m in enumerate(picks))
 more = f'<a class="related-all" href="{landing}">{html.escape(pages[landing][0])} →</a>'
 return f'<nav class="section-next" aria-label="{heading}"><div class="section-next-head"><h2>{heading}</h2>{more}</div><div class="related-grid">{cards}</div></nav>'

# Resource pages: one panel with purpose, status and how to get the file.
ASSET_KIND = {'presentations': ('slides', 'Presentation', 'formatting-slides.html', 'How to format a presentation'),
 'documents': ('document', 'Document template', 'brand-in-practice.html', 'Apply the brand'),
 'brand': ('brand', 'Brand artwork', 'logo-guidance.html', 'Using the SKAO logo')}
ART = {'slides': '<span class="art-slide"><i>SKA Observatory</i><b>A shared story.</b></span>',
 'document': '<span class="art-doc"><b>SKAO</b><i></i><i></i><i></i></span>',
 'brand': '<span class="art-brand"><b>Aa</b><i></i><em></em></span>'}

def asset_panel(name, body, jira):
 m = re.search(r'<div class="task-intro"><div>(?:<span class="eyebrow">.*?</span>)?<p>(.*?)</p></div></div>', body, re.S)
 n = re.search(r'<aside class="availability-note".*?</aside>', body, re.S)
 if not (m and n): return body
 sec = section_of(name)
 kind, label, guide, guide_label = ASSET_KIND.get(sec[0] if sec else '', ASSET_KIND['documents'])
 if name == 'poster-templates.html': guide, guide_label = 'making-a-poster.html', 'Prepare a poster'
 detail = re.search(r'</strong> (.*?) Ask the team', n.group(0), re.S).group(1)
 panel = (f'<div class="task-intro asset-panel"><div class="asset-art {kind}" aria-hidden="true">{ART[kind]}</div><div class="asset-info">'
  f'<span class="eyebrow">{label}</span><p class="asset-purpose">{m.group(1)}</p>'
  '<dl class="asset-facts"><div><dt>Status</dt><dd><span class="status-pill">Available on request</span> ' + detail + '</dd></div>'
  '<div><dt>How to get it</dt><dd>Ask Creative Production through the helpdesk for the current version.</dd></div></dl>'
  f'<div class="asset-actions"><a class="button" href="{jira}">Ask for this file ↗</a><a class="text-link" href="{guide}">{guide_label}</a></div></div></div>')
 body = body.replace(m.group(0), panel).replace(n.group(0), '')
 return re.sub(r'<aside class="next-step"><div><h2>Choose a different starting point</h2>.*?</aside>', '', body, flags=re.S)

def checklist(name, body):
 total = 0
 def convert(m):
  nonlocal total
  items = re.findall(r'<li>(.*?)</li>', m.group(3), re.S)
  total += len(items)
  lis = ''.join(f'<li><label><input type="checkbox"><span>{it}</span></label></li>' for it in items)
  return f'<section class="reading-section checklist"><h2>{m.group(1)}</h2><ul class="check-list">{lis}</ul></section>'
 body = re.sub(r'<section class="reading-section"><h2>(.*?)</h2><(ul|ol)>(.*?)</\2></section>', convert, body, flags=re.S)
 if not total: return body
 bar = (f'<div class="checklist-bar" data-checklist="{name}"><span class="checklist-progress" role="status" aria-live="polite">0 of {total} done</span>'
  '<span class="checklist-meter" aria-hidden="true"><i></i></span><button type="button" data-checklist-reset>Clear ticks</button><button type="button" data-print>Print</button></div>')
 at = body.find('<section class="reading-section checklist">')
 return body[:at] + bar + body[at:]

def catalogue(pages, meta, summaries, on_request):
 cards, counts, seen = [], {}, set()
 for key, label, groups in TYPES:
  for name, m in meta.items():
   if m['group'] not in groups or name in SKIP: continue
   title = pages[name][0]
   if title in seen: continue
   seen.add(title)
   status = '<span class="resource-status">On request</span>' if name in on_request else ''
   cards.append(f'<a class="resource-card" href="{name}" data-resource data-type="{key}"><span class="resource-type">{label}</span><h3>{html.escape(title)}</h3><p>{html.escape(summaries[name])}</p>{status}</a>')
   counts[key] = counts.get(key, 0) + 1
 chips = f'<button type="button" data-type-filter="all" aria-pressed="true">All <span>{len(cards)}</span></button>' + ''.join(
  f'<button type="button" data-type-filter="{key}" aria-pressed="false">{label} <span>{counts[key]}</span></button>' for key, label, _ in TYPES if counts.get(key))
 return ('<section class="catalogue" aria-labelledby="catalogueHeading"><div class="catalogue-head"><h2 id="catalogueHeading">Everything in the Hub</h2>'
  '<label class="catalogue-search">' + SEARCH_ICON + '<span class="visually-hidden">Filter resources by name</span><input id="resourceFilter" type="search" autocomplete="off" placeholder="Filter by name, e.g. letterhead"></label></div>'
  '<div class="type-chips" role="group" aria-label="Show resource type">' + chips + '</div>'
  '<p id="filterStatus" class="filter-status" role="status"></p>'
  '<div class="resource-grid">' + ''.join(cards) + '</div>'
  '<div id="catalogueEmpty" class="catalogue-empty" hidden><p>Nothing matches that filter.</p><button type="button" id="clearFilters" class="button secondary">Show everything</button></div></section>')

def request_routes(body, jira):
 """Two clear routes first: submit a brief, or write one with the helper."""
 body = re.sub(r'(<div class="task-intro">.*?</div>)<a href="[^"]*" class="button">Open creative helpdesk ↗</a>(</div>)', r'\1\2', body, count=1, flags=re.S)
 body = body.replace('Already have a brief? Send it through the creative helpdesk with your files or source links.', 'Choose how you want to start. Either way, the team replies to agree the scope and timing with you.', 1)
 routes = (f'<div class="route-choice"><a class="route-card primary" href="{jira}"><span class="eyebrow">I have a brief</span><strong>Submit it in the helpdesk</strong><span>Attach your files or source links. The team replies to agree scope and timing.</span><em>Open creative helpdesk ↗</em></a>'
  '<a class="route-card" href="#brief-builder" data-open-details><span class="eyebrow">I need help</span><strong>Write my brief here</strong><span>Answer six short questions, then copy the result into the helpdesk.</span><em>Start the brief helper ↓</em></a></div>')
 body = body.replace('<div class="process-strip">', routes + '<div class="process-strip">', 1)
 return body.replace('<details class="brief-builder">', '<details class="brief-builder" id="brief-builder">', 1)

STATE = {}  # titles and summaries, filled by revise() for the header menus

def status_pill(name):
 return '<span class="status-pill">On request</span>' if name in STATE.get('on_request', ()) else ''

def directory(name, pages, summaries):
 sec = section_of(name)
 key, label, landing, members, groups = sec
 out = '<div class="directory">'
 for g, items in groups:
  out += f'<section class="dir-group"><h2>{g}</h2><div class="dir-grid">'
  for m in items:
   out += (f'<a class="dir-card" href="{m}"><strong>{html.escape(pages[m][0])}</strong><span>{html.escape(summaries[m])}</span>'
    + status_pill(m) + ('' if primary(m, key) else '<small class="dir-cross">In ' + section_of(m)[1] + '</small>') + '</a>')
  out += '</div></section>'
 return out + '</div>'

def unfold(body):
 """Landing pages show their short advice instead of hiding it."""
 def open_detail(m):
  inner = m.group(2)
  if '<h2' in inner: return f'<section class="landing-note">{inner}</section>'
  return f'<section class="landing-note"><h2>{m.group(1)}</h2>{inner}</section>'
 return re.sub(r'<details class="guidance-detail"><summary>(.*?)</summary><div>(.*?)</div></details>', open_detail, body, flags=re.S)

def landing(name, body, pages, summaries):
 # Cards that only pointed at a few section pages give way to the full directory.
 body = re.sub(r'<details class="guidance-detail"><summary>[^<]*</summary><div><div class="choice-grid">.*?</details>', '', body, flags=re.S)
 body = re.sub(r'<div class="choice-grid">(?:<a class="choice-card".*?</a>)+</div>', '', body, count=1, flags=re.S)
 body = unfold(body)
 d = directory(name, pages, summaries)
 # Quick answers (brand swatches, the Canto hand-off) stay first; the directory follows.
 for marker in ['<div class="type-spec">', '<div class="media-handoff">']:
  at = body.find(marker)
  if at >= 0:
   close = body.find('</div></div>', at) + 12
   return body[:close] + d + body[close:]
 m = re.search(r'<div class="task-intro">.*?</div>(?:<a [^>]*class="button"[^>]*>.*?</a>)?</div>', body, re.S)
 return body[:m.end()] + d + body[m.end():] if m else d + body

CHEVRON = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'

def nav(current=''):
 titles, summaries = STATE['titles'], STATE['summaries']
 cur = section_of(current)
 out = ''
 for key, label, landing_page, groups in SECTIONS:
  here = ' data-current="true"' if cur and cur[0] == key else ''
  out += (f'<div class="nav-item"><button type="button" class="nav-button" aria-expanded="false" aria-controls="menu-{key}"{here}>{label}{CHEVRON}</button>'
   f'<div class="mega" id="menu-{key}" hidden><div class="mega-inner"><div class="mega-intro"><strong>{label}</strong><p>{html.escape(summaries[landing_page])}</p>'
   f'<a class="mega-home" href="{landing_page}">{html.escape(titles[landing_page])} →</a></div>')
  for g, pages in groups:
   out += f'<div class="mega-group"><h3>{g}</h3><ul>' + ''.join(f'<li><a href="{m}">{html.escape(titles[m])}</a></li>' for m in pages) + '</ul></div>'
  out += '</div></div></div>'
 return out

TILES = [
 ('presentations', 'slides', 'Templates, reusable decks and formatting help.', ['standard-template.html', 'master-deck.html', 'formatting-slides.html']),
 ('documents', 'document', 'Letterheads, memos, reports and posters.', ['letterheads.html', 'email-signatures.html', 'poster-templates.html']),
 ('brand', 'brand', 'Logos, colours, fonts and partner rules.', ['logos.html', 'colours-and-type.html', 'fonts.html']),
 ('media', 'media', 'Photography and footage in Canto.', ['canto-access.html', 'hero-images.html', 'image-usage.html']),
 ('events', 'events', 'Stands, print and merchandise for events.', ['event-checklist.html', 'stands.html', 'merchandise.html']),
 ('guides', 'guides', 'Do-it-yourself checks for common jobs.', ['making-a-poster.html', 'print-preparation.html', 'accessibility.html']),
]
TILE_ART = {**ART,
 'events': '<span class="art-events"><i></i><b>SKAO</b><em></em></span>',
 'guides': '<span class="art-guides"><i></i><i></i><i></i></span>'}

def home_tiles(home, titles):
 media_svg = re.search(r'<a class="quick-resource media"[^>]*><div class="resource-art" aria-hidden="true">(.*?)</div>', home, re.S)
 art = {**TILE_ART, 'media': media_svg.group(1) if media_svg else ''}
 out = '<div class="section-tiles">'
 for key, kind, desc, links in TILES:
  sec = next(x for x in SECTIONS if x[0] == key)
  out += (f'<article class="section-tile kind-{kind}"><a class="tile-main" href="{sec[2]}"><div class="tile-art" aria-hidden="true">{art[kind]}</div>'
   f'<h3>{sec[1]}</h3><p>{desc}</p></a><ul class="tile-links">' + ''.join(f'<li><a href="{m}">{html.escape(titles[m])}</a></li>' for m in links) + '</ul></article>')
 return out + '</div>'

def latest_band():
 return ('<section class="latest-band journey-band" aria-labelledby="latestHeading"><div class="band-heading"><div><p class="eyebrow" id="latestEyebrow">03 / Just added</p>'
  '<h2 id="latestHeading">Latest approved assets</h2><p class="latest-lead" id="latestLead">The newest approved files uploaded to the Creative Hub.</p></div>'
  '<a href="resources.html" class="text-link">Browse everything →</a></div>'
  '<div id="latestAssets" class="latest-grid" data-approval-label="approved"><p class="latest-status">Loading the latest files…</p></div>'
  '<noscript><p class="latest-status">Turn on JavaScript to see the latest files, or browse <a href="resources.html">templates and assets</a>.</p></noscript></section>')

def revise(pages, meta, jira):
 titles = {n: t for n, (t, b) in pages.items()}
 summaries = {n: summary(b) for n, (t, b) in pages.items()}
 on_request = {n for n, (t, b) in pages.items() if 'availability-note' in b}
 STATE.update(titles=titles, summaries=summaries, on_request=on_request)
 for name in meta:
  title, body = pages[name]
  if name in on_request: body = asset_panel(name, body, jira)
  if name in CHECKLISTS: body = checklist(name, body)
  if name == 'request.html': body = request_routes(body, jira)
  pages[name] = (title, body)
 landings = {sec[2] for sec in SECTIONS}
 for name in meta:
  title, body = pages[name]
  if name in landings: body = landing(name, body, pages, summaries)
  pages[name] = (title, body + related(name, pages, summaries))
 title, body = pages['resources.html']
 body = body.replace('<div class="choice-grid">', '<div class="choice-grid compact">', 1)
 at = body.find('<aside class="next-step">')
 cat = catalogue(pages, meta, summaries, on_request)
 pages['resources.html'] = (title, body[:at] + cat + body[at:] if at >= 0 else body + cat)
 # Homepage: search first, then the latest approved files.
 title, home = pages['index.html']
 old = '<div class="actions"><a class="button" href="#library">Find a resource →</a></div>'
 assert old in home
 home = home.replace(old, '<form class="hero-search" data-hub-search role="search"><label for="heroSearch" class="visually-hidden">Search the Creative Hub</label>' + SEARCH_ICON +
  '<input id="heroSearch" type="search" autocomplete="off" placeholder="Search templates, logos, guidance…"><button class="button" type="submit">Search</button></form>')
 home = re.sub(r'<div class="quick-library">.*?</div></section>', lambda m: home_tiles(home, titles) + '</section>', home, count=1, flags=re.S)
 home = home.replace('<h2>What do you need?</h2>', '<h2>Browse by section</h2>', 1)
 assert home.endswith('</div>')
 pages['index.html'] = (title, home[:-6] + latest_band() + '</div>')
 return pages, titles
