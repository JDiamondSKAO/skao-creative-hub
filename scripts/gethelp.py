"""Get help, simplified: one page to ask, one to share, one for questions.

Get help is a short note that points to the Comms helpdesk for questions and
larger projects, then Common questions and Share material. The pages it replaces
stay reachable at their old addresses and point to Get help. The brief checklist,
"what happens next" steps and request extras it held until 2.17 are at the git
tag v2.16.0; the text before that is in archive/get-help-v2.14.html.
"""
import html, re
import links

HOME = 'working-with-us.html'

# Old page -> where its content lives now, and what that part is called.
MOVED = {
 'request.html': (HOME, 'Get help'),
 'creative-services.html': (HOME, 'Get help'),
 'timing.html': (HOME, 'Get help'),
 'video-request.html': (HOME, 'Get help'),
 'print.html': (HOME, 'Get help'),
 'business-cards.html': (HOME, 'Get help'),
 'help.html': ('faq.html', 'Common questions'),
 'updates.html': ('index.html', 'Just added, on the homepage'),
 'archive.html': ('index.html', 'Just added, on the homepage'),
 'email-signatures.html': ('documents.html', 'Documents'),
 'canto-guide.html': ('canto-access.html', 'Using the Canto library'),
 # 2.17: pages folded into fuller ones.
 'widescreen-template.html': ('standard-template.html', 'Standard SKAO template'),
 'science-slides.html': ('master-deck.html', 'Decks to reuse'),
 'construction-slides.html': ('master-deck.html', 'Decks to reuse'),
 'specialised-slides.html': ('master-deck.html', 'Decks to reuse'),
 'reports.html': ('memos.html', 'Memo and report templates'),
 'hero-images.html': ('media.html', 'Photos and video'),
 'telescope-images.html': ('media.html', 'Photos and video'),
 'event-photos.html': ('media.html', 'Photos and video'),
 'b-roll.html': ('media.html', 'Photos and video'),
 'recordings.html': ('media.html', 'Photos and video'),
 'animations.html': ('media.html', 'Photos and video'),
 'event-safety.html': ('events.html', 'Plan event materials'),
 'merchandise.html': ('stands.html', 'Stands and merchandise'),
}

# Retired pages say why, rather than only where to go: (eyebrow, message, searchable).
RETIRED = {
 'email-signatures.html': ('Now looked after by IT', 'Email signatures are now managed by IT. For a new or updated signature, contact the IT service desk.', True),
 'canto-guide.html': ('This page has moved', 'All the Canto guidance is now on one page: Using the Canto library.', False),
 'widescreen-template.html': ('This page has moved', 'All SKAO presentation templates are 16:9, so the Standard SKAO template is the widescreen one.', False),
}

def link(url, label, cls=''):
 return f'<a href="{html.escape(url, quote=True)}"' + (f' class="{cls}"' if cls else '') + f'>{label}</a>'

def page(jira):
 """A short note, the helpdesk, then the two other Get help pages."""
 ask = ('<div class="task-intro gh-intro"><div><p>Most everyday work can start from the Hub’s templates and guides.</p>'
  '<p>For anything else, from a quick question to a larger project such as new design, video or animation, print, events or business cards, '
  'contact the Comms helpdesk. Say what you need, who it’s for and when you need it, and attach anything you already have.</p></div>'
  + link(jira, 'Open the Comms helpdesk ↗', 'button') + '</div>')
 more = ('<nav class="gh-more" aria-label="More help">'
  '<a class="dir-row" href="faq.html"><span class="dir-text"><strong>Common questions</strong><span>Where things are, who approves work, and what to do if something is missing.</span></span></a>'
  '<a class="dir-row" href="contribute.html"><span class="dir-text"><strong>Share material</strong><span>Send a deck, photos, video or a correction for review.</span></span></a></nav>')
 return ask + more

def faq(jira):
 q = lambda t, b: f'<details class="guidance-detail"><summary>{t}</summary><div><p>{b}</p></div></details>'
 return ('<div class="task-intro"><div><span class="eyebrow">Help</span><p>Short answers to the questions staff ask most.</p></div></div>'
  + q('Where are templates and slides?', 'Start with ' + link('resources.html', 'Templates and assets') + '. Presentation decks are under ' + link('presentations.html', 'Presentations') + '.')
  + q('Where are photos and video?', 'In the staff media library in Canto. ' + link('media.html', 'Photos and video') + ' shows a selection and links to it. Check each asset’s credit and permitted use.')
  + q('Can I adapt material myself?', 'Yes, within its usage notes, and keep the credits. Ask the content owner before changing facts or meaning, and the creative team before substantial design changes.')
  + q('Why can I browse but not upload?', 'Browsing and contributing have separate permissions. To add material, see ' + link('contribute.html', 'Share material') + '.')
  + q('Is my request booked once I send it?', 'Not yet. The team replies to agree what will be made and when; a date isn’t fixed until then. If it’s urgent, say why and what could be cut back.')
  + q('Who approves the work?', 'Name the content owner and the final reviewer in your request. The approval route depends on the work, so confirm it rather than assume it.')
  + q('A file is missing or a link is broken', 'Send the page link and what happened to the ' + link(jira, 'Comms helpdesk ↗') + '.'))

def share(jira):
 return ('<div class="task-intro"><div><span class="eyebrow">Make good work reusable</span>'
  '<p>Send it through ' + link(jira, 'the Comms helpdesk') + '. Sharing starts a review: nothing is published until its owner has checked it.</p></div></div>'
  '<section class="reading-section"><h2>What to send</h2><ul>'
  '<li><strong>A presentation:</strong> the editable deck or a link to it, with its audience, event date, content owner and any limits on reuse.</li>'
  '<li><strong>Photos or video:</strong> use the upload link you were given, with a title, creator, location and rights information. '
  'No link yet? Ask the helpdesk for one; the Canto library is for browsing, not uploading.</li>'
  '<li><strong>A correction:</strong> the page link, what should change and where the correct information comes from.</li></ul>'
  '<p>Keep working files where they are, so a new copy doesn’t become a competing version.</p></section>')

def moved(title, target, name=''):
 url, part = target
 where = 'Get help' if url.startswith(HOME) else part
 if name in RETIRED:
  eyebrow, message, _ = RETIRED[name]
  action = (link(links.url('IT_SERVICE_DESK'), 'Open the IT service desk ↗', 'button') if name == 'email-signatures.html' and links.url('IT_SERVICE_DESK')
   else link(url, 'Go to ' + html.escape(where) + ' →', 'button'))
  return f'<div class="task-intro moved-note"><div><span class="eyebrow">{eyebrow}</span><p>{html.escape(message)}</p></div>{action}</div>'
 return ('<div class="task-intro moved-note"><div><span class="eyebrow">This page has moved</span>'
  f'<p>{html.escape(title)} is now part of {html.escape(where)}' + (f', under “{html.escape(part)}”' if url.startswith(HOME + '#') else '') + '.</p></div>'
  + link(url, 'Go to ' + html.escape(where) + ' →', 'button') + '</div>')

# "Ask the team" boxes that only repeat the footer band's call to action.
GENERIC_ASKS = ['Agree before producing', 'Ready to brief the work?', 'Need more than formatting?', 'Missing a resource?']

def trim_asks(h):
 for title in GENERIC_ASKS:
  h = re.sub(r'<aside class="next-step"><div><h2>' + re.escape(html.escape(title, quote=False).replace("'", '&#x27;')) + r'</h2>.*?</aside>', '', h, flags=re.S)
  h = re.sub(r'<aside class="next-step"><div><h2>' + re.escape(title) + r'</h2>.*?</aside>', '', h, flags=re.S)
 return h

def relink(h):
 """Point links at the part of Get help that now holds each old page."""
 for old, (url, _) in MOVED.items():
  h = h.replace(f'href="{old}"', f'href="{url}"')
 return h

def rename(h):
 """The catalogue is the full list, so it is called what it is."""
 for o, n in [('>Templates and assets</a>', '>All resources</a>'), ('>All templates and assets <span', '>All resources <span'),
              ('>Browse templates and assets <span', '>Browse all resources <span')]:
  h = h.replace(o, n)
 return h

def apply(pages, jira):
 for name, target in MOVED.items():
  if name in pages: pages[name] = (pages[name][0], moved(pages[name][0], target, name))
 pages[HOME] = ('Get help', page(jira))
 pages['faq.html'] = ('Common questions', faq(jira))
 pages['contribute.html'] = ('Share material', share(jira))
 pages = {n: (t, b if n in MOVED else rename(trim_asks(relink(b)))) for n, (t, b) in pages.items()}
 pages['resources.html'] = ('All resources', pages['resources.html'][1])
 return pages

# Search: short, ready-written answers to the questions staff ask most. When a search matches
# one, it shows above the results with a link to the page that has the detail. Kept as hidden
# links in the search dialog, so production rewrites their addresses like any other link.
ANSWERS = [
 ('logo logos lockup artwork emblem', 'Where do I get the SKAO logo?', 'Logo files are on Logos and icons, in versions for light and dark backgrounds. Anyone outside the SKAO needs permission to use it.', 'logos.html', 'Logos and icons'),
 ('template powerpoint pptx slides slide deck presentation', 'Where’s the slide template?', 'The Standard SKAO template is the 16:9 PowerPoint for any talk. For joint work, use a partner template.', 'standard-template.html', 'Standard SKAO template'),
 ('colour colours color colors hex rgb cmyk pantone palette', 'What are the SKAO colours?', 'Navy and magenta lead, with accent palettes for science, technology and the sites. Copy hex, RGB, CMYK or Pantone values from Colours and typography.', 'colours-and-type.html', 'Colours and typography'),
 ('font fonts typeface noto verdana typography', 'Which font do we use?', 'Noto Sans, with Verdana as the fallback where Noto isn’t installed.', 'fonts.html', 'Fonts'),
 ('photo photos image images picture pictures canto photography', 'Where are the photos?', 'In the staff media library in Canto. First time? Choose Register Now and use your SKAO email address.', 'media.html', 'Photos and video'),
 ('letterhead letterheads letter', 'Where are the letterheads?', 'Letterheads for each office are on Letterheads, grouped by information classification.', 'letterheads.html', 'Letterheads'),
 ('poster posters a0 a1 a2', 'How do I make a poster?', 'Start from a poster template in A0, A1 or A2, then follow Prepare a poster for the content and export.', 'making-a-poster.html', 'Prepare a poster'),
 ('business card cards', 'How do I get business cards?', 'Ask the Comms helpdesk, with your name, job title and contact details exactly as they should appear.', HOME, 'Get help'),
 ('signature signatures', 'How do I set up my email signature?', 'Email signatures are looked after by IT. Contact the IT service desk for a new or updated one.', 'email-signatures.html', 'Email signatures'),
 ('progress construction status figures stats statistics milestones', 'Where are the latest construction figures?', 'SKA-Low progress and SKA-Mid progress have each team’s live status slides, the overall construction status and their latest decks.', 'low-slides.html', 'SKA-Low progress'),
 ('help request brief commission design designer helpdesk project', 'Can someone design something for me?', 'Contact the Comms helpdesk. Say what you need, who it’s for and when, and attach anything you already have.', HOME, 'Get help'),
 ('ai firefly generative midjourney chatgpt', 'Can I use AI to make images?', 'Check the SKAO AI policy and use only approved tools. Never upload confidential or personal material.', 'firefly.html', 'Using AI image tools'),
 ('supplier suppliers printer printers printing', 'Who should print it?', 'Communications can recommend trusted print suppliers for your location and the kind of job you have.', 'print-suppliers.html', 'Work with print suppliers'),
 ('stand stands booth exhibition merchandise merch swag giveaway giveaways', 'Do we have a stand or merchandise?', 'Check the existing stand kit, designs and stock on Stands and merchandise before briefing anything new.', 'stands.html', 'Stands and merchandise'),
 ('talk talks speaker speakers', 'Where are the slides from staff talks?', 'Recent talks has slides shared by staff, newest first. You can add your own.', 'recent-talks.html', 'Recent talks'),
]

def answers_html():
 return ('<div id="hubAnswers" hidden>' + ''.join(
  f'<a href="{href}" data-keys="{keys}" data-question="{html.escape(q, quote=True)}" data-answer="{html.escape(a, quote=True)}">{html.escape(label)}</a>'
  for keys, q, a, href, label in ANSWERS) + '</div>')
