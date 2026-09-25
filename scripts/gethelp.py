"""Get help, simplified: one page to ask, one to share, one for questions.

Everything in this section ends at the creative helpdesk, so it says each thing
once: what to include, what happens next, and the few extra details a video,
print or business card request needs. The pages it replaces stay reachable at
their old addresses and point to the part of Get help that now holds their
content. The full previous text is kept in archive/get-help-v2.14.html and at
the git tag pre-get-help-simplify.
"""
import html, re

HOME = 'working-with-us.html'

# Old page -> where its content lives now, and what that part is called.
MOVED = {
 'request.html': (HOME, 'Get help'),
 'creative-services.html': (HOME + '#what-we-do', 'What we can help with'),
 'timing.html': (HOME + '#what-happens-next', 'What happens next'),
 'video-request.html': (HOME + '#video', 'Video or animation'),
 'print.html': (HOME + '#print', 'Print'),
 'business-cards.html': (HOME + '#business-cards', 'Business cards'),
 'help.html': ('faq.html', 'Common questions'),
 'updates.html': ('index.html', 'Just added, on the homepage'),
 'archive.html': ('index.html', 'Just added, on the homepage'),
}

TEMPLATE = '\n'.join([
 'What it is and who it is for:', '', 'When it will be used, and why then:', '',
 'What you need (format, size, quantity):', '', 'Who supplies the content, and who approves it:', '',
 'Source files or links:', '', 'Budget or other constraints:', ''])

def link(url, label, cls=''):
 return f'<a href="{html.escape(url, quote=True)}"' + (f' class="{cls}"' if cls else '') + f'>{label}</a>'

def details(key, title, items, extra=''):
 return (f'<details class="guidance-detail" id="{key}"><summary>{title}</summary><div><ul>'
  + ''.join(f'<li>{i}</li>' for i in items) + '</ul>' + (f'<p>{extra}</p>' if extra else '') + '</div></details>')

def page(jira):
 intro = ('<div class="task-intro"><div><span class="eyebrow">Creative Production</span>'
  '<p>Most everyday work can start from the Hub’s templates and guides. For new work or a review, send a brief to the creative helpdesk and we’ll reply to agree the details.</p></div>'
  + link(jira, 'Open the creative helpdesk ↗', 'button') + '</div>')
 include = ('<section class="reading-section" id="what-to-include"><h2>What to include</h2><ul>'
  '<li>What it is, who it’s for and what it should help them do.</li>'
  '<li>When it will be used, and why then.</li>'
  '<li>What you need: format, size and quantity.</li>'
  '<li>Who supplies the content, and who approves the result.</li>'
  '<li>Source files or links, and any budget or other constraints.</li></ul>'
  f'<p class="copy-template-row"><button type="button" class="copy-template" data-copy="{html.escape(TEMPLATE, quote=True)}" data-copy-label="Request template">'
  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6.5A2.5 2.5 0 0 0 13.5 4h-7A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H8"/></svg>'
  '<span>Copy as a template</span></button> Paste it into the helpdesk form and fill in the gaps.</p></section>')
 specific = ('<section class="reading-section" id="specific"><h2>Asking for something specific?</h2>'
  + details('video', 'Video or animation', [
     'Where it will be shown, and how long it can be.',
     'Existing footage, a draft script, images and source information.',
     'Accessibility needs such as captions.',
     'Any filming, and who needs to be available for it.'],
     'Check ' + link('video.html', 'Video and animation') + ' first: existing footage may already do the job.')
  + details('print', 'Print', [
     'The item, its dimensions and how many you need.',
     'Existing artwork or draft content, and where images come from.',
     'Where it should be delivered, and the supplier’s deadline.',
     'Finishing, such as lamination or folding.'],
     'Ordering from a supplier? See ' + link('print-suppliers.html', 'Work with print suppliers') + ' and ' + link('print-preparation.html', 'Prepare files for print') + '.')
  + details('business-cards', 'Business cards', [
     'Your name and job title, exactly as they should appear.',
     'The contact details for the card.',
     'How many, in which languages, and where to deliver them.',
     'Who will approve the proof.'])
  + '</section>')
 nxt = ('<ol>'
  '<li>The team reads your request and replies, often with a question or two.</li>'
  '<li>Together you agree what will be made, who reviews it and when it’s delivered.</li>'
  '<li>Work starts once that’s agreed.</li></ol>'
  '<p>Timing depends on when the content is ready, how complex the work is, how quickly reviewers can respond and any supplier deadlines. '
  'If it’s urgent, give the real deadline, the reason for it and what could be cut back. A date isn’t fixed until it’s agreed.</p>')
 scope = ('<ul>'
  '<li>Design and layout for publications, presentations and graphics.</li>'
  '<li>Video, animation and digital work.</li>'
  '<li>Visual identity, templates and reusable resources.</li>'
  '<li>Creative materials for events, print and displays.</li></ul>'
  '<p>You bring the purpose, the content and the person who approves it. Event logistics and editorial decisions stay with the teams that own them.</p>')
 item = lambda key, title, body: (f'<details class="rail-item" data-kind="info" id="{key}" open><summary><span class="rail-label">{title}</span></summary>'
  f'<div class="rail-body">{body}</div></details>')
 side = ('<aside class="landing-rail" aria-label="Good to know"><div class="rail-guides"><h2 class="rail-title">Good to know</h2>'
  + item('what-happens-next', 'What happens next', nxt) + item('what-we-do', 'What we can help with', scope) + '</div></aside>')
 more = ('<section class="dir-group"><h2>More help</h2><ul class="dir-list">'
  '<li><a class="dir-row" href="faq.html"><span class="dir-text"><strong>Common questions</strong><span>Where things are, who approves work, and what to do if something is missing.</span></span></a></li>'
  '<li><a class="dir-row" href="contribute.html"><span class="dir-text"><strong>Share material</strong><span>Send a deck, photos, video or a correction for review.</span></span></a></li>'
  '</ul></section>')
 return (intro + '<div class="landing-layout get-help-layout"><div class="landing-main">' + include + specific + '</div>' + side + '</div>'
  + '<div class="directory get-help-more">' + more + '</div>')

def faq(jira):
 q = lambda t, b: f'<details class="guidance-detail"><summary>{t}</summary><div><p>{b}</p></div></details>'
 return ('<div class="task-intro"><div><span class="eyebrow">Help</span><p>Short answers to the questions staff ask most.</p></div></div>'
  + q('Where are templates and slides?', 'Start with ' + link('resources.html', 'Templates and assets') + '. Presentation decks are under ' + link('presentations.html', 'Presentations') + '.')
  + q('Where are photos and video?', 'In the staff media library in Canto. ' + link('media.html', 'Photos and video') + ' shows a selection and links to it. Check each asset’s credit and permitted use.')
  + q('Can I adapt material myself?', 'Yes, within its usage notes, and keep the credits. Ask the content owner before changing facts or meaning, and the creative team before substantial design changes.')
  + q('Why can I browse but not upload?', 'Browsing and contributing have separate permissions. To add material, see ' + link('contribute.html', 'Share material') + '.')
  + q('Is my request booked once I send it?', 'Not yet. The team replies to agree what will be made and when; a date isn’t fixed until then. If it’s urgent, say why and what could be cut back.')
  + q('Who approves the work?', 'Name the content owner and the final reviewer in your request. The approval route depends on the work, so confirm it rather than assume it.')
  + q('A file is missing or a link is broken', 'Send the page link and what happened to the ' + link(jira, 'creative helpdesk ↗') + '.'))

def share(jira):
 return ('<div class="task-intro"><div><span class="eyebrow">Make good work reusable</span>'
  '<p>Sharing starts a review: nothing is published until its owner has checked it.</p></div>'
  + link(jira, 'Open the creative helpdesk ↗', 'button') + '</div>'
  '<section class="reading-section"><h2>What to send</h2><ul>'
  '<li><strong>A presentation:</strong> the editable deck or a link to it, with its audience, event date, content owner and any limits on reuse.</li>'
  '<li><strong>Photos or video:</strong> use the upload link you were given, with a title, creator, location and rights information. '
  'No link yet? Ask the helpdesk for one; the Canto library is for browsing, not uploading.</li>'
  '<li><strong>A correction:</strong> the page link, what should change and where the correct information comes from.</li></ul>'
  '<p>Keep working files where they are, so a new copy doesn’t become a competing version.</p></section>')

def moved(title, target):
 url, part = target
 where = 'Get help' if url.startswith(HOME) else part
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

def apply(pages, jira):
 for name, target in MOVED.items():
  if name in pages: pages[name] = (pages[name][0], moved(pages[name][0], target))
 pages[HOME] = ('Get help', page(jira))
 pages['faq.html'] = ('Common questions', faq(jira))
 pages['contribute.html'] = ('Share material', share(jira))
 pages = {n: (t, b if n in MOVED else trim_asks(relink(b))) for n, (t, b) in pages.items()}
 t, b = pages['print-preparation.html']
 pages['print-preparation.html'] = (t, b.replace('<a href="working-with-us.html" class="text-link">Brief the print work', '<a href="working-with-us.html#print" class="text-link">Brief the print work'))
 return pages
