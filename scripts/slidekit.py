"""The Standard SKAO template page: the SKAO master deck and the blank template in one place.

Communications' master deck (ready-made slides with approved facts) and the blank template it is built
on (six .potx files, one per information classification) are both attached to the Standard SKAO
Template page. The page offers two ways to start, shows what's in the deck, lists the template versions
and says how to use them. Pictures of the slides are attachments too, made by scripts/deck_images.py
under the names in PICTURES, so no slide images live in this repository.

Approved slide decks points here, since the master deck is where a new presentation starts.
"""
import links
from brandkit import CLASSIFICATIONS

PAGE = 'standard-template.html'
VERSION = '1.0'
RELEASED = 'October 2026'

# Picture name -> the master deck slide it shows (deck_images.py makes deck-cover.webp and so on).
PICTURES = {
 'deck-cover': 1, 'deck-template': 43,
 'deck-start': 2, 'deck-openers': 7, 'deck-01': 12, 'deck-02': 17, 'deck-03': 26, 'deck-04': 29,
 'deck-05': 32, 'deck-06': 38, 'deck-07': 46, 'deck-closing': 56,
}

# What's in the deck, in the deck's own words ("What's in this deck"): picture, number, name, line.
CONTENTS = [
 ('deck-start', '', 'Start here', 'Guide slides on using the deck, to delete before you present'),
 ('deck-openers', '', 'Openers', 'A title slide, the acknowledgement and an agenda'),
 ('deck-01', '01', 'The Square Kilometre Array Observatory', 'Who we are, our members and our history'),
 ('deck-02', '02', 'The telescopes', 'SKA-Low, SKA-Mid and how we’re building them'),
 ('deck-03', '03', 'Science', 'The big questions the telescopes will help answer'),
 ('deck-04', '04', 'Data', 'From the antennas to astronomers around the world'),
 ('deck-05', '05', 'Impact', 'Values, sustainability, communities and the radio sky'),
 ('deck-06', '06', 'Useful extras', 'Official wording, a glossary and common questions'),
 ('deck-07', '07', 'Building blocks', 'Layouts, icons and colours for your own slides'),
 ('deck-closing', '', 'Closing', 'A thank-you slide and the image credits'),
]

STEPS = [
 ('Open a copy', 'The template opens as a new presentation, so the original stays as it is. '
                 'Save the master deck under your own file name.'),
 ('Keep what you need', 'Delete the slides you won’t use, including the guide slides. '
                        'Home › New Slide adds any layout.'),
 ('Copy slides across', 'Paste them into another deck with Use Destination Theme, so they match it.'),
 ('Check the facts', 'Each fact slide’s notes say where its numbers come from and when they were checked. '
                     'For this month’s construction figures, use the <a href="site-progress.html">site progress slides</a>.'),
 ('Credit every photo', 'Keep the credit on the photo, as the Canto Media Library gives it.'),
]


def slide(name, label='', page_id=''):
    """A 16:9 slide picture from the page's attachments, or a gradient slide until it loads."""
    return (f'<div class="slide-pic" data-kit-image="{name}"'
            + (f' data-kit-page="{page_id}"' if page_id else '')
            + (f' data-label="{label}"' if label else '') + '></div>')


def template_page():
    start = (
        '<section class="start-section" aria-labelledby="startHeading"><h2 id="startHeading">Two ways to start</h2>'
        '<ul class="start-grid">'
        '<li class="start-card is-lead" id="master-deck">' + slide('deck-cover') +
        '<div class="start-body"><p class="start-kicker">Ready-made slides</p><h3>SKAO master deck</h3>'
        '<p>The SKAO story in seven sections, with approved facts, photos, charts and layouts. '
        'Keep the slides you need and delete the rest.</p>'
        '<ul class="start-meta"><li>PowerPoint</li><li data-file-size hidden></li><li>Unrestricted</li></ul>'
        '<div class="start-actions"><a class="button" data-file-button="master deck" hidden>Download the master deck</a>'
        '<span class="file-pending" data-file-pending>Download coming soon</span>'
        '<a class="text-link" href="#whats-inside">What’s inside</a></div></div></li>'
        '<li class="start-card" id="blank-template">' + slide('deck-template') +
        '<div class="start-body"><p class="start-kicker">Your own content</p><h3>Blank template</h3>'
        '<p>The same layouts, colours and fonts, ready for your own slides. '
        'There’s a version for each information classification.</p>'
        '<ul class="start-meta"><li>PowerPoint template (.potx)</li><li>Six versions</li></ul>'
        '<div class="start-actions"><a class="button secondary" href="#choose-version">Choose a version</a></div></div></li>'
        '</ul></section>')
    inside = (
        '<section class="deck-contents" id="whats-inside" aria-labelledby="insideHeading">'
        '<div class="section-lead"><h2 id="insideHeading">What’s in the master deck</h2>'
        '<p>It runs in the order you might tell the SKAO story. Each fact slide’s speaker notes give the source '
        'and the date it was last checked.</p></div><ol class="contents-grid">'
        + ''.join(f'<li class="contents-item">{slide(pic, num)}<p>'
                  + (f'<em>{num}</em>' if num else '') + f'<b>{name}</b><span>{line}</span></p></li>'
                  for pic, num, name, line in CONTENTS)
        + '</ol></section>')
    versions = (
        '<section class="versions" id="choose-version" aria-labelledby="versionsHeading">'
        '<h2 id="versionsHeading">Choose a template version</h2>'
        '<p>Use the version that matches your content’s information classification. Unrestricted has no label, '
        'for public talks. The other five print their label in the footer bar of every content slide.</p>'
        '<div data-downloads-slot><ul class="variant-list">' + ''.join(f'<li>{c}</li>' for c in CLASSIFICATIONS)
        + '</ul></div></section>')
    steps = (
        '<section class="use-section" id="how-to-use" aria-labelledby="useHeading"><h2 id="useHeading">How to use it</h2>'
        '<ol class="use-steps">' + ''.join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in STEPS) + '</ol></section>')
    gallery = links.pending('GOOGLE_SLIDES', 'Open the gallery')
    know = (
        '<section class="know-band" aria-labelledby="knowHeading"><h2 id="knowHeading" class="rail-title">Good to know</h2>'
        '<dl class="know-grid">'
        '<div><dt>Fonts</dt><dd>Noto Sans Light, Regular and Bold, already on staff computers. If text looks '
        'different, the deck’s Check your fonts slide shows what to do.</dd></div>'
        + links.needs('<div data-fact="google slides"><dt>Google Slides</dt><dd>There’s an SKAO template in the '
                      'Google Slides template gallery too, when you’re signed in with your SKAO Google account. '
                      + gallery + '</dd></div>', links.url('GOOGLE_SLIDES'))
        + '<div><dt>Joint work</dt><dd>Presenting with a partner? Use a <a href="partner-templates.html">partner '
        'template</a>.</dd></div>'
        f'<div><dt>Version {VERSION}</dt><dd>{RELEASED}, approved by Communications. Downloaded copies don’t '
        'update, so check here before each talk.</dd></div></dl></section>')
    return ('<div class="task-intro"><div><span class="eyebrow">Slides for every talk</span>'
            '<p>Every SKAO presentation starts here. Take the master deck for ready-made slides about the SKAO, '
            'or the blank template for your own content.</p></div></div>'
            '<div class="template-page" data-kit data-no-toc>' + start + inside
            + '<div class="template-columns">' + versions + steps + '</div>' + know + '</div>')


def banner(template_id):
    """Approved slide decks: the master deck leads, on the template page."""
    return ('<aside class="deck-banner" data-kit aria-labelledby="deckBannerHeading">'
            + slide('deck-cover', page_id=template_id) +
            '<div class="deck-banner-text"><p class="eyebrow">Starting a new presentation?</p>'
            '<h2 id="deckBannerHeading">Use the SKAO master deck</h2>'
            '<p>Ready-made slides with approved facts, photos and layouts, beside the blank template.</p></div>'
            '<a class="button" href="standard-template.html#master-deck">Get the master deck</a></aside>')


def apply(pages, meta):
    title, _ = pages[PAGE]
    pages[PAGE] = (title, template_page())
    title, body = pages['master-deck.html']
    slot = '<div data-deck-library></div>'
    assert slot in body
    pages['master-deck.html'] = (title, body.replace(slot, banner(meta[PAGE]['id']) + slot, 1))
    return pages
