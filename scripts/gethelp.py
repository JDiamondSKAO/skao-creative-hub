"""Get help is one page, Common questions: how to reach the Comms helpdesk, short answers
to the questions staff ask most, and how to share work.

It lives in the footer rather than the header. The pages it replaces (Get help, Share material
and the older request pages) stay reachable at their old addresses and point here. The brief
checklist and "what happens next" steps it held until 2.17 are at the git tag v2.16.0; the text
before that is in archive/get-help-v2.14.html.
"""
import html, re
import links

HOME = 'faq.html'

# Old page -> where its content lives now, and what that part is called.
MOVED = {
 'working-with-us.html': (HOME, 'Common questions'),
 'contribute.html': (HOME + '#share', 'Sharing your work'),
 'request.html': (HOME, 'Common questions'),
 'creative-services.html': (HOME, 'Common questions'),
 'timing.html': (HOME, 'Common questions'),
 'video-request.html': (HOME, 'Common questions'),
 'print.html': (HOME, 'Common questions'),
 'business-cards.html': (HOME, 'Common questions'),
 'help.html': ('faq.html', 'Common questions'),
 'updates.html': ('resources.html', 'Latest files'),
 'archive.html': ('resources.html', 'Latest files'),
 'email-signatures.html': ('documents.html', 'Documents'),
 'canto-guide.html': ('canto-access.html', 'Using the Canto library'),
 # 2.17: pages folded into fuller ones.
 'widescreen-template.html': ('standard-template.html', 'Standard SKAO template'),
 'science-slides.html': ('master-deck.html', 'Approved slide decks'),
 'construction-slides.html': ('master-deck.html', 'Approved slide decks'),
 'specialised-slides.html': ('master-deck.html', 'Approved slide decks'),
 'reports.html': ('memos.html', 'Memo and report templates'),
 'hero-images.html': ('media.html', 'Photos and video'),
 'telescope-images.html': ('media.html', 'Photos and video'),
 'event-photos.html': ('media.html', 'Photos and video'),
 'b-roll.html': ('media.html', 'Photos and video'),
 'recordings.html': ('media.html', 'Photos and video'),
 'animations.html': ('media.html', 'Photos and video'),
 # 2.22: Events covers what we've made to reuse; planning an event starts at the Comms helpdesk.
 'event-safety.html': ('events.html', 'Event materials'),
 'event-checklist.html': ('events.html', 'Event materials'),
}

# Retired pages say why, rather than only where to go: (eyebrow, message, searchable).
RETIRED = {
 'email-signatures.html': ('Now looked after by IT', 'Email signatures are now managed by IT. For a new or updated signature, contact the IT service desk.', True),
 'canto-guide.html': ('This page has moved', 'All the Canto guidance is now on one page: Using the Canto library.', False),
 'widescreen-template.html': ('This page has moved', 'All SKAO presentation templates are 16:9, so the Standard SKAO template is the widescreen one.', False),
 'event-safety.html': ('Part of planning an event', 'Safety is planned with the event, so the Hub doesn’t cover it. Planning an event? Start with the Comms helpdesk. For the exhibition kit and print files, see Event materials.', False),
 'event-checklist.html': ('This page has gone', 'Planning an event? Start with the Comms helpdesk. For the exhibition kit and print files, see Event materials.', False),
}

def link(url, label, cls=''):
 return f'<a href="{html.escape(url, quote=True)}"' + (f' class="{cls}"' if cls else '') + f'>{label}</a>'

def faq(jira):
 """The help page: the helpdesk first, then short answers, then how to share work."""
 q = lambda t, b, key='': (f'<details class="guidance-detail"' + (f' id="{key}"' if key else '') + f'><summary>{t}</summary><div><p>{b}</p></div></details>')
 ask = ('<div class="task-intro gh-intro"><div><p>Most everyday work can start from the Hub’s templates and guides.</p>'
  '<p>For anything else, from a quick question to a larger project such as new design, video or animation, print, events or business cards, '
  'contact the Comms helpdesk. Say what you need, who it’s for and when you need it, and attach anything you already have.</p></div>'
  + link(jira, 'Open the Comms helpdesk ↗', 'button') + '</div>')
 answers = ('<section class="help-answers" aria-label="Common questions">'
  + q('Where are templates and slides?', 'Slide templates and decks are under ' + link('presentations.html', 'Presentations') + ', and letterheads, memos and posters under ' + link('documents.html', 'Documents') + '. ' + link('resources.html', 'Latest files') + ' shows what’s new.')
  + q('Where are photos and video?', 'In the staff media library in Canto. ' + link('media.html', 'Photos and video') + ' shows a selection and links to it. Check each asset’s credit and permitted use.')
  + q('Can I adapt material myself?', 'Yes, within its usage notes, and keep the credits. Ask the content owner before changing facts or meaning, and the creative team before substantial design changes.')
  + q('Why can I browse but not upload?', 'Browsing and contributing have separate permissions. To add material, see ' + link('#share', 'Sharing your work') + ' below.')
  + q('Is my request booked once I send it?', 'Not yet. The team replies to agree what will be made and when; a date isn’t fixed until then. If it’s urgent, say why and what could be cut back.')
  + q('Who approves the work?', 'Name the content owner and the final reviewer in your request. The approval route depends on the work, so confirm it rather than assume it.')
  + q('Something is missing, wrong or broken', 'Send the page link, what happened or what should change, and where the correct information comes from, to the ' + link(jira, 'Comms helpdesk ↗') + '.')
  + '</section>')
 sharing = ('<section class="help-share" id="share"><h2>Sharing your work</h2>'
  '<p class="help-lead">Sharing starts a review: nothing is published until its owner has checked it.</p>'
  + q('How do I share a deck for others to reuse?', 'Send the editable deck, or a link to it, through the ' + link(jira, 'Comms helpdesk ↗') + ', with its audience, event date, content owner and any limits on reuse. '
     'Once Communications has approved it, it can join ' + link('master-deck.html', 'Approved slide decks') + '.', 'share-a-deck')
  + q('How do I share photos or video?', 'Ask the ' + link(jira, 'Comms helpdesk ↗') + ' for an upload link; the Canto library is for browsing, not uploading. '
     'Include a title, who took it, where, and any rights or consent information.', 'share-photos')
  + '<p class="quiet-note">Keep working files where they are, so a new copy doesn’t become a competing version.</p></section>')
 return ask + answers + sharing

def moved(title, target, name=''):
 url, part = target
 where = 'Common questions' if url.startswith(HOME) else part
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
 """The old Templates and assets page lists the newest files now, so it is called what it is."""
 for o, n in [('>Templates and assets</a>', '>Latest files</a>'), ('>All templates and assets <span', '>Latest files <span'),
              ('>Browse templates and assets <span', '>See the latest files <span')]:
  h = h.replace(o, n)
 return h

def apply(pages, jira):
 # Staff knew the old page by its menu label.
 if 'working-with-us.html' in pages: pages['working-with-us.html'] = ('Get help', pages['working-with-us.html'][1])
 for name, target in MOVED.items():
  if name in pages: pages[name] = (pages[name][0], moved(pages[name][0], target, name))
 pages[HOME] = ('Common questions', faq(jira))
 pages = {n: (t, b if n in MOVED else rename(trim_asks(relink(b)))) for n, (t, b) in pages.items()}
 pages['resources.html'] = ('Latest files', pages['resources.html'][1])
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
 ('business card cards', 'How do I get business cards?', 'Ask the Comms helpdesk, with your name, job title and contact details exactly as they should appear.', HOME, 'Common questions'),
 ('signature signatures', 'How do I set up my email signature?', 'Email signatures are looked after by IT. Contact the IT service desk for a new or updated one.', 'email-signatures.html', 'Email signatures'),
 ('progress construction status figures stats statistics milestones site sites telescope telescopes', 'Where are the latest construction figures?', 'Construction overview has the dashboard, the overall status and the newest slides from both site teams.', 'site-progress.html', 'Construction overview'),
 ('help request brief commission design designer helpdesk project', 'Can someone design something for me?', 'Contact the Comms helpdesk. Say what you need, who it’s for and when, and attach anything you already have.', HOME, 'Common questions'),
 ('ai firefly generative midjourney chatgpt', 'Can I use AI to make images?', 'Check the SKAO AI policy and use only approved tools. Never upload confidential or personal material.', 'firefly.html', 'Using AI image tools'),
 ('supplier suppliers printer printers printing', 'Who should print it?', 'Communications can recommend trusted print suppliers for your location and the kind of job you have.', 'print-suppliers.html', 'Work with print suppliers'),
 ('stand stands booth exhibition backdrop backdrops banner banners pull-up merchandise merch swag giveaway giveaways kit print', 'Do we have exhibition kit, banners or giveaways?', 'Yes. The exhibition kit is available on request from the Communications team at each site, and print and giveaway files are ready to download.', 'events.html', 'Event materials'),
 ('event events plan planning organise organize organising organizing conference venue', 'Can you help plan my event?', 'Contact the Communications team through the Comms helpdesk. For the exhibition kit and print files, see Event materials.', 'events.html', 'Event materials'),
 ('talk talks speaker speakers deck decks reuse', 'Where are slides I can reuse?', 'Approved slide decks has decks Communications has approved for reuse, including talks given by staff.', 'master-deck.html', 'Approved slide decks'),
 ('new latest recent added update updates whats', 'What’s new in the Hub?', 'Latest files lists every new and updated file, newest first.', 'resources.html', 'Latest files'),
]

def answers_html():
 return ('<div id="hubAnswers" hidden>' + ''.join(
  f'<a href="{href}" data-keys="{keys}" data-question="{html.escape(q, quote=True)}" data-answer="{html.escape(a, quote=True)}">{html.escape(label)}</a>'
  for keys, q, a, href, label in ANSWERS) + '</div>')
