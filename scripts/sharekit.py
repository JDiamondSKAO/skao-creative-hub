"""Share your presentation: staff send a talk they've given for review, and some become approved slide decks.

A page created by scripts/confluence_text.py (matched by title until its ID is known). The button opens the
form named SHARE_DECK_FORM in dev/links.json; until that exists it opens the Comms helpdesk.
"""
from html import escape
import links

PAGE, TITLE = 'share-presentation.html', 'Share your presentation'
INTRO = ('Share a presentation you’ve given and the Communications team will take a look. Some are chosen to become '
         'approved slide decks, so colleagues can reuse and adapt your work.')
STEPS = [
    ('Share it', 'Add your slides, or a link to them, with the event, the audience and when you gave the talk.'),
    ('We take a look', 'We check the facts, the images and their credits, and how well it would work for other speakers.'),
    ('We let you know', 'If yours is chosen, we’ll agree any updates with you and add it to the approved slide decks, '
                        'with your name on it.'),
]
KNOW = [
    ('Not every talk is chosen', 'Many talks are written for one audience or moment, and that’s fine. Everything shared helps '
                                 'us see what people are presenting, and often shapes future slides.'),
    ('Large files', 'For a very large deck, share a link to where it’s stored instead of the file itself.'),
    ('Your file stays yours', 'Sharing sends us a copy. Your own file isn’t moved or changed.'),
]

def body(jira):
    """One panel with the ask and how it works side by side, then Good to know: no loose sections, no gaps."""
    href = escape(links.url('SHARE_DECK_FORM') or jira, quote=True)
    steps = ''.join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in STEPS)
    know = ''.join(f'<div><dt>{t}</dt><dd>{d}</dd></div>' for t, d in KNOW)
    return (
        f'<div class="template-page share-page" data-no-toc data-summary="{escape(INTRO, quote=True)}">'
        '<section class="share-hero" aria-label="Share your presentation">'
        '<div class="share-hero-main"><p class="share-kicker">For your talks</p>'
        f'<p class="share-lead">{INTRO}</p>'
        f'<a class="button" href="{href}" data-share-deck>Share your presentation ↗</a>'
        '<p class="share-note">Looking for slides to reuse? See <a href="master-deck.html">Approved slide decks</a>.</p></div>'
        '<div class="share-hero-steps"><h2 id="share-how" class="share-label">How it works</h2>'
        f'<ol class="use-steps">{steps}</ol></div></section>'
        '<section class="know-band" aria-labelledby="share-know"><h2 id="share-know" class="rail-title">Good to know</h2>'
        f'<dl class="know-grid">{know}</dl></section>'
        '</div>')

def apply(pages, jira):
    pages[PAGE] = (TITLE, body(jira))
    # Approved slide decks ends by inviting people to share their own talks.
    title, deck = pages['master-deck.html']
    pages['master-deck.html'] = (title, deck + '<div class="next-step"><div><h2>Given a talk worth sharing?</h2><p>Share your '
                                 'presentation for review. Some become approved slide decks.</p></div>'
                                 f'<a class="button secondary" href="{PAGE}">Share your presentation</a></div>')
    return pages
