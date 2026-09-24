"""What the SKAO brand bank actually contains, checked against the source files.

Facts only: formats, versions and values confirmed in the brand bank
(September 2026). Files are not published from here. They reach staff as
Confluence attachments labelled "approved", which the theme lists as
downloads.
"""
import re

CLASSIFICATIONS = ['Unrestricted', 'Staff Resources', 'SKAO Staff Only', 'For Project Use', 'Confidential', 'Strictly Confidential']

# Rows added to a resource page's panel: (label, text or list).
PACK = {
 'standard-template.html': [
  ('Format', 'PowerPoint (.pptx), 16:9 widescreen'),
  ('Versions', CLASSIFICATIONS),
  ('Choose', 'Use the version whose label matches your content’s information classification.'),
  ('Partner versions', 'SKAO–SARAO presentation template; SRCNet PowerPoint and Keynote templates.'),
 ],
 'widescreen-template.html': [
  ('Format', 'PowerPoint (.pptx), 16:9'),
  ('Note', 'The current SKAO presentation templates are all 16:9, so this is the same layout as the <a href="standard-template.html">Standard SKAO template</a>.'),
 ],
 'letterheads.html': [
  ('Format', 'Word (.docx)'),
  ('Versions', ['One per office address', 'Landscape layout', 'Classification-labelled versions', 'SKAO–CSIRO co-branded']),
 ],
 'email-signatures.html': [
  ('Format', 'Signature images (PNG)'),
  ('Versions', ['Full-colour logo', 'White logo']),
 ],
 'poster-templates.html': [
  ('Sizes', ['A0', 'A1', 'A2']),
  ('Formats', 'Illustrator (.ai), Word (.docx) and PDF for each size'),
 ],
 'logos.html': [
  ('Marks', ['Logo (lettermark)', 'Pictorial mark (roundel)']),
  ('Colours', ['Blueshift Navy', 'White', 'Black', 'Full colour: RGB for screen, CMYK for print']),
  ('Formats', 'AI, EPS, PDF, PNG and SVG, with and without the exclusion zone'),
  ('Also available', 'SKAO–CSIRO and SKAO–SARAO co-brand logos; SRCNet regional centre logos (10 centres).'),
 ],
 'brand-book.html': [
  ('Edition', 'March 2022, PDF, 62 pages'),
  ('Covers', 'Identity, logo use, colour, typography and brand architecture'),
  ('Related', 'SKAO–CSIRO and SKAO–SARAO co-branding guidelines (PDF).'),
 ],
}

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
  out += (f'<details class="palette"{" open" if i == 0 else ""}><summary><span>{name}</span><small>{len(colours)} colours · for {use}</small></summary><div class="swatch-row">'
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

 for name, extra in [('co-branding-csiro.html', 'SKAO–CSIRO letterheads'), ('co-branding-sarao.html', 'the SKAO–SARAO presentation template')]:
  edit(name, lambda n, b, extra=extra: rep(b, 'The source page has no linked co-branding pack.',
   f'A co-branding pack is available on request: the joint guidelines (PDF), both organisations’ logo files and {extra}.', n))

 def video(name, body):
  kit = ('<section class="reading-section"><h2>Brand video kit</h2><p>For your own edits, ask Creative Production for:</p><ul>'
   '<li>Logo intro and outro animations, landscape and portrait, with title and statement versions.</li>'
   '<li>Lower thirds and motion graphics templates for Premiere Pro (.mogrt).</li>'
   '<li>Safe-zone guides for framing.</li></ul></section>')
  at = body.find('<section class="reading-section">')
  return body[:at] + kit + body[at:]
 edit('video.html', video)

 def merch(name, body):
  reuse = ('<section class="reading-section"><h2>Existing designs to reuse</h2><ul>'
   '<li>SKAO apparel, promotional items, stationery and stickers.</li><li>SRCNet apparel.</li></ul>'
   '<p>Ask for the artwork before briefing something new.</p></section>')
  at = body.find('<section class="reading-section">')
  return body[:at] + reuse + body[at:]
 edit('merchandise.html', merch)
 return pages
