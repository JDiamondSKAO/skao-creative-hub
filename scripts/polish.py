"""Visual layer on top of the reviewed journeys: homepage search, resource catalogue."""
import html, re

def text(fragment):
 fragment = re.sub(r'<span[^>]*aria-hidden="?true"?[^>]*>.*?</span>', '', fragment, flags=re.S)
 return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()

def summary(body):
 m = re.search(r'<div class="task-intro">.*?<p>(.*?)</p>', body, re.S) or re.search(r'<p[^>]*>(.*?)</p>', body, re.S)
 return text(m.group(1)) if m else ''

SEARCH_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'

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

def catalogue(pages, meta):
 cards, counts, seen = [], {}, set()
 for key, label, groups in TYPES:
  for name, m in meta.items():
   if m['group'] not in groups or name in SKIP: continue
   title, body = pages[name]
   if title in seen: continue
   seen.add(title)
   status = '<span class="resource-status">On request</span>' if 'availability-note' in body else ''
   cards.append(f'<a class="resource-card" href="{name}" data-resource data-type="{key}"><span class="resource-type">{label}</span><h3>{html.escape(title)}</h3><p>{html.escape(summary(body))}</p>{status}</a>')
   counts[key] = counts.get(key, 0) + 1
 chips = f'<button type="button" data-type-filter="all" aria-pressed="true">All <span>{len(cards)}</span></button>' + ''.join(
  f'<button type="button" data-type-filter="{key}" aria-pressed="false">{label} <span>{counts[key]}</span></button>' for key, label, _ in TYPES if counts.get(key))
 return ('<section class="catalogue" aria-labelledby="catalogueHeading"><div class="catalogue-head"><h2 id="catalogueHeading">Everything in the Hub</h2>'
  '<label class="catalogue-search">' + SEARCH_ICON + '<span class="visually-hidden">Filter resources by name</span><input id="resourceFilter" type="search" autocomplete="off" placeholder="Filter by name, e.g. letterhead"></label></div>'
  '<div class="type-chips" role="group" aria-label="Show resource type">' + chips + '</div>'
  '<p id="filterStatus" class="filter-status" role="status"></p>'
  '<div class="resource-grid">' + ''.join(cards) + '</div>'
  '<div id="catalogueEmpty" class="catalogue-empty" hidden><p>Nothing matches that filter.</p><button type="button" id="clearFilters" class="button secondary">Show everything</button></div></section>')

def revise(pages, meta):
 title, body = pages['resources.html']
 body = body.replace('<div class="choice-grid">', '<div class="choice-grid compact">', 1)
 at = body.find('<aside class="next-step">')
 body = body[:at] + catalogue(pages, meta) + body[at:] if at >= 0 else body + catalogue(pages, meta)
 pages['resources.html'] = (title, body)
 # Homepage: search is the first thing staff see.
 title, home = pages['index.html']
 old = '<div class="actions"><a class="button" href="#library">Find a resource →</a></div>'
 assert old in home
 home = home.replace(old, '<form class="hero-search" data-hub-search role="search"><label for="heroSearch" class="visually-hidden">Search the Creative Hub</label>' + SEARCH_ICON +
  '<input id="heroSearch" type="search" autocomplete="off" placeholder="Search templates, logos, guidance…"><button class="button" type="submit">Search</button></form>')
 pages['index.html'] = (title, home)
 return pages
