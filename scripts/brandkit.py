"""What the SKAO brand bank actually contains, checked against the source files.

Facts only: formats, versions and values confirmed in the brand bank
(September 2026). Files are not published from here. They reach staff as
Confluence attachments labelled "approved", which the theme lists as
downloads.
"""
import re
from links import pending

CLASSIFICATIONS = ['Unrestricted', 'Staff Resources', 'SKAO Staff Only', 'For Project Use', 'Confidential', 'Strictly Confidential']

# Rows added to a resource page's panel: (label, text or list).
PACK = {
 'standard-template.html': [
  ('Format', 'PowerPoint (.pptx), 16:9 widescreen'),
  ('Versions', CLASSIFICATIONS),
  ('Choose', 'Use the version whose label matches your content’s information classification.'),
  ('Google Slides', 'Also in the Google Slides template gallery, when you’re signed in with your SKAO Google account. ' + pending('GOOGLE_SLIDES', 'Open the gallery')),
 ],
 'master-deck.html': [
  ('Planned', ['About the SKAO', 'Science case', 'Construction progress, both sites', 'SRCNet', 'Working with local communities', 'Specialised topics']),
 ],
 'memos.html': [
  ('Format', 'Word (.docx)'),
  ('Includes', ['Memo template', 'Report template']),
 ],
 'partner-templates.html': [
  ('Format', 'PowerPoint (.pptx), 16:9; the SRCNet template also comes as Keynote (.key)'),
 ],
 'letterheads.html': [
  ('Format', 'Word (.docx)'),
  ('Versions', ['One per office address', 'Landscape layout', 'Classification-labelled versions']),
 ],
 'poster-templates.html': [
  ('Sizes', ['A0', 'A1', 'A2']),
  ('Formats', 'Word (.docx) and PDF for each size'),
 ],
 'logos.html': [
  ('Marks', ['Logo (lettermark)', 'Pictorial mark (roundel)']),
  ('Colours', ['Blueshift Navy', 'White', 'Black', 'Full colour: RGB for screen, CMYK for print']),
  ('Formats', 'AI, EPS, PDF, PNG and SVG, with and without the exclusion zone'),
 ],
 'partner-logos.html': [
  ('Includes', ['SRCNet logo and avatar', 'SRCNet regional centre logos']),
  ('Colours', ['Full colour', 'Black', 'White']),
  ('Formats', 'AI, EPS and PNG'),
 ],
 'brand-book.html': [
  ('Edition', 'March 2022, PDF, 62 pages'),
  ('Covers', 'Identity, logo use, colour, typography and brand architecture'),
  ('Related', 'SKAO–CSIRO and SKAO–SARAO co-branding guidelines (PDF).'),
 ],
}

# How a page's downloads are grouped, where file type alone would not say enough.
# Rules are tried in order against each file name (case-insensitive); files matching none
# fall back to the automatic groups. "label" names the row outright; "strip" removes words
# from the name to make the row label; "note" sits under the group heading; "desc" is a line
# on a card. "site" gives a group its site colour, so offices read by where they are.
OFFICES_UK = {'group': 'United Kingdom', 'note': 'Global Headquarters, Jodrell Bank', 'match': 'landscape|jodrell', 'label': 'Landscape layout', 'site': 'uk'}
AU = {'group': 'Australia', 'note': 'Geraldton and Perth offices', 'site': 'au'}
DOWNLOAD_GROUPS = {
 'letterheads.html': [OFFICES_UK,
  {**AU, 'match': 'bradford', 'label': 'Bradford Office, Geraldton'},
  {**AU, 'match': 'chapman', 'label': 'Chapman Office, Geraldton'},
  {**AU, 'match': 'kensington', 'label': 'Kensington Office, Perth (with CSIRO)'}],
 'co-branding-csiro.html': [
  {'group': 'Co-branding guidelines', 'match': 'guideline', 'label': 'SKAO and CSIRO co-branding guidelines'}],
 'co-branding-sarao.html': [
  {'group': 'Co-branding guidelines', 'match': 'guideline', 'label': 'SKAO and SARAO co-branding guidelines'}],
 'partner-templates.html': [
  {'group': 'Templates', 'match': 'sarao', 'label': 'SKAO and SARAO', 'desc': 'For joint work with the South African Radio Astronomy Observatory.'},
  {'group': 'Templates', 'match': 'rcn|srcnet', 'label': 'SRCNet', 'desc': 'For the SKA Regional Centre Network, in PowerPoint or Keynote.'}],
 'partner-logos.html': [
  {'group': 'SRCNet logo', 'note': 'The full logo, for most uses', 'match': 'srcnet_logo', 'strip': r'\bskao\b|\bsrcnet\b|\brgb\b|\blogo\b|\bmono'},
  {'group': 'SRCNet avatar', 'note': 'The round mark, for small spaces and social media', 'match': 'srcnet_avatar', 'strip': r'\bskao\b|\bsrcnet\b|\brgb\b|\bavatar\b|\bmono'},
  {'group': 'Regional centres', 'note': 'One pack per centre, with every version of its logo in AI, EPS and PNG', 'match': 'src'}],
 'master-deck.html': [
  {'group': 'About the SKAO', 'match': 'about|master|overview|introduc|briefing|press|media|colloquium|exhibition|samagam'},
  {'group': 'Science', 'match': 'science'},
  {'group': 'Construction progress', 'match': 'construction|progress'},
  {'group': 'SRCNet', 'match': 'srcnet|rcn'},
  {'group': 'Working with local communities', 'match': 'communit'},
  {'group': 'Specialised topics', 'match': '.'}],
 'memos.html': [
  {'group': 'Memos', 'match': 'memo'},
  {'group': 'Reports', 'match': 'report'}],
}
# How a page shows its downloads: a list (the default), cards with a cover (templates), or logo
# tiles with a preview. Approved slide decks has its own library (main.js), which takes its topics
# from the rules above. A cover is a picture attached to the same page
# under the file's own name (Template.pptx and Template.jpg); without one, the card shows the title.
DOWNLOAD_VIEW = {'partner-templates.html': 'cards', 'partner-logos.html': 'logos'}

# Primary colours from the Brand Book colour pages.
PRIMARY_EXTRA = {
 '7, 0, 104': [('CMYK', '100, 99, 20, 30'), ('Pantone', '2745 C')],
 '231, 0, 104': [('CMYK', '3, 100, 35, 0'), ('Pantone', '213 C')],
}

# Accent palettes: (name, use, [(hex, pantone)]). Hex values as published.
ACCENTS = [
 ('Science', 'science-related products and material', [
  ('#003D51', '3035 C'), ('#562A31', '504 C'), ('#EF7C38', '1575 C'), ('#F49E6B', '1565 C'), ('#EFEA78', '393 C'),
  ('#0D1D2C', '296 C'), ('#0E2538', '539 C'), ('#17243D', '289 C'), ('#087CBB', '7461 C'), ('#C1D66E', '374 C'),
  ('#0B3B5C', '302 C'), ('#4689C8', '279 C'), ('#EB5C5D', '178 C'), ('#D9B38E', '727 C'), ('#74C095', '346 C')]),
 ('Technology', 'engineering, big data, software and technology', [
  ('#004337', '3308 C'), ('#205B42', '554 C'), ('#1B1E2A', '532 C'), ('#F7BE00', '7408 C'), ('#5D2A2B', '490 C'),
  ('#313D47', '432 C'), ('#5B6770', '431 C'), ('#7C868B', '430 C'), ('#A0A7AB', '429 C'), ('#C1C6CA', '428 C')]),
 ('Sites', 'the telescope sites, local heritage and communities', [
  ('#6A3F23', '469 C'), ('#9B6017', '1395 C'), ('#B5814E', '729 C'), ('#F9B34C', '1365 C'), ('#EB7802', '716 C')]),
]

def copy_button(name, label, value):
 return (f'<button type="button" class="copy-value" data-copy="{value}" aria-label="Copy {name} {label} {value}">'
  f'<code>{label} {value}</code><span>Copy</span></button>')

def accent_palettes():
 out = ('<section class="accent-palettes"><h2>Accent palettes</h2><p>Use accents alongside the two primary colours, '
  'which should make up most of any design. Select a colour to copy its hex value.</p>')
 for i, (name, use, colours) in enumerate(ACCENTS):
  out += (f'<details class="palette" open><summary><span>{name}</span><small>{len(colours)} colours · for {use}</small></summary><div class="swatch-row">'
   + ''.join(f'<button type="button" class="swatch" data-copy="{h}" style="--c:{h}" title="Pantone {p}" aria-label="Copy {h}, Pantone {p}"><i class="swatch-chip"></i><code>{h}</code><span>Copy</span></button>' for h, p in colours)
   + '</div></details>')
 return out + '</section>'

def rep(body, old, new, page):
 assert old in body, f'{page}: expected text not found: {old[:60]}'
 return body.replace(old, new, 1)

def apply(pages):
 """Add confirmed brand-bank details to the pages they belong on."""
 def edit(name, fn):
  title, body = pages[name]
  pages[name] = (title, fn(name, body))

 # Colour values: CMYK and Pantone beside hex and RGB, wherever the swatches appear.
 def colours_extra(name, body):
  for rgb, extra in PRIMARY_EXTRA.items():
   m = re.search(r'<button type="button" class="copy-value" data-copy="' + re.escape(rgb) + r'" aria-label="Copy ([^"]+?) RGB [^"]*">.*?</button>', body, re.S)
   if m: body = body.replace(m.group(0), m.group(0) + ''.join(copy_button(m.group(1), l, v) for l, v in extra), 1)
  return body
 for name in ['brand.html', 'colours-and-type.html']: edit(name, colours_extra)

 def colours_page(name, body):
  body = rep(body, 'Use these digital values from the retained SKAO Brand Book v2, March 2022.',
   'Official values from the SKAO Brand Book (March 2022). Copy what you need: hex or RGB for screen, CMYK or Pantone for print.', name)
  body = rep(body, 'For print, use the Brand Book and the supplier’s agreed colour specifications rather than guessing CMYK or Pantone conversions.',
   'The colours are designed for screen (RGB). CMYK and Pantone equivalents print slightly duller, so check a proof with your supplier.', name)
  at = body.find('<section class="reading-section">')
  return body[:at] + accent_palettes() + body[at:]
 edit('colours-and-type.html', colours_page)

 def logo_rules(name, body):
  body = rep(body, 'Leave at least half the logo’s height clear on all sides, following the retained Brand Book.',
   'Leave at least half the logo’s height clear on all sides (the exclusion zone).', name)
  return rep(body, '<li>For detailed sizing and specialist applications, use the Brand Book.</li>',
   '<li>Minimum size: 20 mm wide in print, 50 px wide on screen.</li><li>If the full-colour logo won’t work on your background, use the single-colour logo, usually white on a dark background.</li>', name)
 edit('logo-guidance.html', logo_rules)

 def fonts(name, body):
  weights = ('<section class="reading-section"><h2>Which weight to use</h2><ul>'
   '<li><strong>Noto Sans Light</strong>: headlines, body text and long paragraphs.</li>'
   '<li><strong>Noto Sans Medium</strong>: emphasis within body copy and bold headlines.</li>'
   '<li><strong>Noto Sans Regular and Bold</strong>: small type, text over backgrounds, or where Light becomes hard to read.</li>'
   '<li><strong>Noto Mono</strong>: technical text, metrics and footnotes, used sparingly.</li>'
   '<li><strong>Verdana</strong>: the fallback when Noto Sans is not available.</li></ul></section>')
  at = body.find('<section class="reading-section">')
  return body[:at] + weights + body[at:]
 edit('fonts.html', fonts)

 def brand_book(name, body):
  return re.sub(r'<p class="quiet-note">The quick reference in this review build uses the retained SKAO Brand Book v2, March 2022\..*?</p>', '', body, count=1, flags=re.S)
 edit('brand-book.html', brand_book)

 def merch(name, body):
  reuse = ('<section class="reading-section"><h2>Existing designs to reuse</h2><ul>'
   '<li>SKAO apparel, promotional items, stationery and stickers.</li><li>SRCNet apparel.</li></ul>'
   '<p>Ask for the artwork before briefing something new.</p></section>')
  at = body.find('<section class="reading-section">')
  return body[:at] + reuse + body[at:]
 edit('stands.html', merch)
 return pages
