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

# Navigation sections: key, label, landing page, pages in reading order.
SECTIONS = [
 ('presentations', 'Presentations', 'presentations.html', ['presentations.html', 'standard-template.html', 'widescreen-template.html', 'master-deck.html', 'science-slides.html', 'low-slides.html', 'mid-slides.html', 'construction-slides.html', 'specialised-slides.html', 'formatting-slides.html']),
 ('documents', 'Documents', 'documents.html', ['documents.html', 'letterheads.html', 'memos.html', 'reports.html', 'email-signatures.html', 'poster-templates.html']),
 ('brand', 'Brand', 'brand.html', ['brand.html', 'logos.html', 'logo-guidance.html', 'colours-and-type.html', 'fonts.html', 'brand-in-practice.html', 'co-branding-csiro.html', 'co-branding-sarao.html', 'brand-book.html']),
 ('media', 'Photos and video', 'media.html', ['media.html', 'canto-access.html', 'hero-images.html', 'telescope-images.html', 'event-photos.html', 'image-usage.html', 'video.html', 'b-roll.html', 'recordings.html', 'animations.html']),
 ('events', 'Events', 'events.html', ['events.html', 'event-checklist.html', 'stands.html', 'merchandise.html', 'event-safety.html']),
 ('guides', 'How-to guides', 'self-service.html', ['self-service.html', 'making-a-poster.html', 'print-preparation.html', 'accessibility.html', 'firefly.html']),
 ('services', 'Creative services', 'working-with-us.html', ['working-with-us.html', 'creative-services.html', 'request.html', 'timing.html', 'video-request.html', 'print.html', 'print-suppliers.html', 'business-cards.html']),
 ('support', 'Help', 'help.html', ['help.html', 'faq.html', 'contribute.html', 'updates.html', 'archive.html']),
]
# Pages that belong to a section without being listed (duplicate source titles).
EXTRA = {'canto-guide.html': 'media'}

def section_of(name):
 for key, label, landing, members in SECTIONS:
  if name in members or EXTRA.get(name) == key: return key, label, landing, members
 return None

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
 others = [(landing, label) for key, label, landing, _ in SECTIONS if not sec or key != sec[0]]
 out = '<aside class="sidebar">'
 if sec:
  key, label, landing, members = sec
  out += f'<nav class="section-nav" aria-label="{label} pages"><h2><a href="{landing}">{label}</a></h2><ul>'
  out += ''.join(f'<li><a href="{m}">{"Overview" if m == landing else html.escape(titles[m])}</a></li>' for m in members)
  out += '</ul></nav><details class="other-sections"><summary>Other sections</summary>'
 else:
  out += '<nav class="section-nav" aria-label="Hub sections"><h2>Sections</h2><div>'
 out += ''.join(f'<a href="{u}">{t}</a>' for u, t in [('resources.html', 'Templates and assets')] + others)
 out += '</details>' if sec else '</div></nav>'
 return out + '<nav id="toc" class="toc" aria-label="On this page"></nav></aside>'

def related(name, pages, summaries):
 sec = section_of(name)
 if not sec: return ''
 key, label, landing, members = sec
 if name == landing:
  if 'choice-grid' in pages[name][1]: return ''
  picks, heading, lead = [m for m in members if m != name], 'In this section', ''
 else:
  rest = [m for m in members if m != landing]
  at = rest.index(name) if name in rest else -1
  picks = [rest[(at + i) % len(rest)] for i in range(1, min(4, len(rest)))] if rest else []
  heading = 'More in ' + label
 cards = ''.join(
  f'<a class="related-card" href="{m}">' + ('<span class="related-next">Next</span>' if i == 0 and name != landing else '') +
  f'<strong>{html.escape(pages[m][0])}</strong><span>{html.escape(summaries[m])}</span></a>' for i, m in enumerate(picks))
 more = '' if name == landing else f'<a class="related-all" href="{landing}">All {label.lower() if key != "support" else "help"} pages →</a>'
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
 for name in meta:
  title, body = pages[name]
  if name in on_request: body = asset_panel(name, body, jira)
  if name in CHECKLISTS: body = checklist(name, body)
  if name == 'request.html': body = request_routes(body, jira)
  pages[name] = (title, body)
 for name in meta:
  title, body = pages[name]
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
 assert home.endswith('</div>')
 pages['index.html'] = (title, home[:-6] + latest_band() + '</div>')
 return pages, titles
