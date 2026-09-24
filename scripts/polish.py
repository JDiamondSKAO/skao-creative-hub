"""Visual and journey layer on top of the reviewed pages.

Adds section navigation, related pages, resource panels, checklists, the
resource catalogue and the homepage search and latest-assets bands. It only
reorganises reviewed content; it never invents files or availability.
"""
import html, re
import brandkit

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
   out += (f'<details class="nav-group" open><summary><span>{g}</span><small>{len(pages)}</small></summary><ul>'
    + ''.join(f'<li><a href="{m}">{html.escape(titles[m])}</a></li>' for m in pages) + '</ul></details>')
  out += '</nav>'
 else:
  out += '<nav class="section-nav" aria-label="Hub sections"><h2>Sections</h2><ul>' + ''.join(
   f'<li><a href="{landing}">{label}</a></li>' for key, label, landing, _ in SECTIONS) + '<li><a href="resources.html">Templates and assets</a></li></ul></nav>'
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
 panel = (f'<div class="task-intro asset-panel" data-page-id="{STATE["ids"].get(name, "")}"><div class="asset-art {kind}" aria-hidden="true">{ART[kind]}</div><div class="asset-info">'
  f'<span class="eyebrow">{label}</span><p class="asset-purpose">{m.group(1)}</p>'
  '<dl class="asset-facts"><div><dt>Status</dt><dd><span class="status-pill">Available on request</span> ' + detail + '</dd></div>'
  '<div class="how-to-get"><dt>How to get it</dt><dd>Ask Creative Production through the helpdesk for the current version.</dd></div>'
  + ''.join(f'<div data-fact="{label.lower()}"><dt>{label}</dt><dd>' + ('<ul class="variant-list">' + ''.join(f'<li>{v}</li>' for v in value) + '</ul>' if isinstance(value, list) else value) + '</dd></div>'
    for label, value in brandkit.PACK.get(name, [])) + '</dl>'
  f'<div class="asset-actions"><a class="button" href="{jira}">Ask for this file ↗</a><a class="text-link" href="{guide}">{guide_label}</a></div>'
  '<div class="asset-downloads" data-downloads hidden></div></div></div>')
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
  for name, m in sorted(meta.items(), key=lambda kv: pages[kv[0]][0].lower()):
   if m['group'] not in groups or name in SKIP: continue
   title = pages[name][0]
   if title in seen: continue
   seen.add(title)
   status = '<span class="dir-meta req">On request</span>' if name in on_request else '<span class="dir-meta"></span>'
   cards.append(f'<li><a class="resource-row" href="{name}" data-page-id="{STATE["ids"].get(name, "")}" data-resource data-type="{key}"><span class="dir-text"><strong>{html.escape(title)}</strong><span>{html.escape(summaries[name])}</span></span><span class="resource-type">{label}</span>{status}</a></li>')
   counts[key] = counts.get(key, 0) + 1
 chips = f'<button type="button" data-type-filter="all" aria-pressed="true">All <span>{len(cards)}</span></button>' + ''.join(
  f'<button type="button" data-type-filter="{key}" aria-pressed="false">{label} <span>{counts[key]}</span></button>' for key, label, _ in TYPES if counts.get(key))
 return ('<section class="catalogue" aria-labelledby="catalogueHeading"><div class="catalogue-head"><h2 id="catalogueHeading">All resources</h2>'
  '<label class="catalogue-search">' + SEARCH_ICON + '<span class="visually-hidden">Filter resources by name</span><input id="resourceFilter" type="search" autocomplete="off" placeholder="Filter by name, e.g. letterhead"></label></div>'
  '<div class="type-chips" role="group" aria-label="Show resource type">' + chips + '</div>'
  '<p id="filterStatus" class="filter-status" role="status"></p>'
  '<ul class="resource-list">' + ''.join(cards) + '</ul>'
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

def row_meta(m, key):
 if m in STATE.get('on_request', ()): return '<span class="dir-meta req" title="On request"><span class="visually-hidden">On request</span></span>'
 if not primary(m, key): return '<span class="dir-meta">In ' + section_of(m)[1] + '</span>'
 return ''

def directory(name, pages, summaries):
 """A section as grouped link lists: label left, title and summary right."""
 key, label, landing, members, groups = section_of(name)
 listed = [m for g, items in groups for m in items]
 waiting = sum(m in STATE.get('on_request', ()) for m in listed)
 out = '<div class="directory">'
 if waiting:
  out += '<p class="dir-legend"><span class="dir-dot" aria-hidden="true"></span>On request: not downloadable from the Hub yet</p>'
 for g, items in groups:
  out += f'<section class="dir-group"><h2>{g} <span class="dir-count">{len(items)}</span></h2><ul class="dir-list">'
  for m in items:
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

def rail(rest, waiting):
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
 if not (items or waiting): return ''
 out = '<aside class="landing-rail" aria-label="Help with this section">'
 if waiting:
  out += (f'<div class="rail-status"><p><span class="dir-dot" aria-hidden="true"></span><strong>Need a file marked on request?</strong> '
   f'Creative Production will send you the current version.</p><a class="button" href="{STATE["jira"]}">Ask for a file ↗</a></div>')
 if items:
  out += '<div class="rail-guides"><h2 class="rail-title">Before you start</h2>' + ''.join(
   f'<details class="rail-item"{" open" if i == 0 else ""}><summary>{html.escape(t)}</summary><div class="rail-body">{b}</div></details>'
   for i, (t, b) in enumerate(items)) + '</div>'
 return out + '</aside>'

def landing(name, body, pages, summaries):
 # Cards that only pointed at a few section pages give way to the full directory.
 body = re.sub(r'<details class="guidance-detail"><summary>[^<]*</summary><div><div class="choice-grid">.*?</details>', '', body, flags=re.S)
 body = re.sub(r'<div class="choice-grid">(?:<a class="choice-card".*?</a>)+</div>', '', body, count=1, flags=re.S)
 body = unfold(body)
 d = directory(name, pages, summaries)
 # Quick answers (brand swatches, the Canto hand-off) stay first; the directory follows.
 def after(head, rest):
  side = rail(rest.strip(), 'dir-legend' in d)
  return head + (f'<div class="landing-layout"><div class="landing-main">{d}</div>{side}</div>' if side else d)
 for marker in ['<div class="type-spec">', '<div class="media-handoff">']:
  at = body.find(marker)
  if at >= 0:
   close = body.find('</div></div>', at) + 12
   return after(body[:close], body[close:])
 m = re.search(r'<div class="task-intro">.*?</div>(?:<a [^>]*class="button"[^>]*>.*?</a>)?</div>', body, re.S)
 return after(body[:m.end()], body[m.end():]) if m else d + body

def nav(current=''):
 """Top menu: one link per section. The landing page lists everything in it."""
 cur = section_of(current)
 out = ''
 for key, label, landing_page, groups in SECTIONS:
  state = ' aria-current="page"' if current == landing_page else ' aria-current="true"' if cur and cur[0] == key else ''
  out += f'<a href="{landing_page}"{state}>{label}</a>'
 return out

# Pages shown full width: they list a whole section, so a sidebar would repeat them.
FULL_WIDTH = {sec[2] for sec in SECTIONS} | {'resources.html'}

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
 """A compact index of the sections: small picture, name and what is inside."""
 media_svg = re.search(r'<a class="quick-resource media"[^>]*><div class="resource-art" aria-hidden="true">(.*?)</div>', home, re.S)
 art = {**TILE_ART, 'media': media_svg.group(1) if media_svg else ''}
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
CANTO_STRIPS = {'telescope-images.html': 'telescope telescopes ska-low ska-mid', 'hero-images.html': 'hero heroes banner', 'event-photos.html': 'event events',
 'animations.html': 'animation animations', 'video.html': 'video videos'}

def canto_gallery(canto):
 return ('<section class="canto-gallery" data-canto="" hidden aria-labelledby="cantoHeading"><div class="canto-head"><div><p class="eyebrow">Staff media library</p>'
  '<h2 id="cantoHeading">Approved photos and artwork</h2></div>'
  f'<a class="text-link canto-open" href="{canto}" target="_blank" rel="noopener">Open in Canto ↗</a></div>'
  '<div class="canto-tabs" role="group" aria-label="Show album"></div><ul class="canto-grid"></ul>'
  '<p class="canto-note">Select an image to open it in Canto, where you’ll find its credit, usage notes and downloads.</p></section>')

def canto_strip(words, canto):
 return (f'<section class="canto-strip" data-canto="{words}" hidden><div class="canto-head"><h2>In the staff media library</h2>'
  f'<a class="text-link canto-open" href="{canto}" target="_blank" rel="noopener">Open album in Canto ↗</a></div><ul class="canto-grid small"></ul></section>')

def revise(pages, meta, jira, canto=''):
 pages = brandkit.apply(pages)
 titles = {n: t for n, (t, b) in pages.items()}
 summaries = {n: summary(b) for n, (t, b) in pages.items()}
 on_request = {n for n, (t, b) in pages.items() if 'availability-note' in b}
 STATE.update(titles=titles, summaries=summaries, on_request=on_request, jira=jira, ids={n: m['id'] for n, m in meta.items()})
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
 # Canto slots go in after the landing layout exists, so they never land in the side panel.
 title, body = pages['media.html']
 at = body.find('<div class="landing-layout">')
 pages['media.html'] = (title, body[:at] + canto_gallery(canto) + body[at:] if at >= 0 else body + canto_gallery(canto))
 for name, words in CANTO_STRIPS.items():
  title, body = pages[name]
  m = re.search(r'<div class="media-handoff">.*?</div></div>', body, re.S)
  pages[name] = (title, body[:m.end()] + canto_strip(words, canto) + body[m.end():] if m else body)
 title, body = pages['resources.html']
 body = body.replace('Choose a starting point. Open its source page to see the file, guidance or availability information.', 'Every template, guide and service in the Hub in one list. Filter by type or name, then open a page to see the file, guidance or availability.', 1)
 body = re.sub(r'<div class="choice-grid">(?:<a class="choice-card".*?</a>)+</div>', '', body, count=1, flags=re.S)
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
 home = home.replace('<h2>What do you need?</h2>', '<h2>Browse the Hub</h2>', 1).replace('<p class="eyebrow">01 / Find and reuse</p>', '', 1)
 home = home.replace('<span>Jump to</span>', '<span>Quick links</span>', 1)
 # The newest files take the promo card's place; the help band gives way to the footer's help row.
 home = home.replace('</section><section id="library"', '</section>' + latest_strip() + '<section id="library"', 1)
 home = re.sub(r'<section class="help-band journey-band">.*?</section>', '', home, count=1, flags=re.S)
 assert home.endswith('</div>')
 pages['index.html'] = (title, home)
 return pages, titles
