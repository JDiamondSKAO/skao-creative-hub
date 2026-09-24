"""Build the same clean shell for the local preview and Scroll Viewport package."""
from pathlib import Path
import json,html,re,shutil,zipfile
R=Path(__file__).resolve().parents[1];D=R/'docs';D.mkdir(exist_ok=True)
(R/'content').mkdir(exist_ok=True)
(R/'evidence').mkdir(exist_ok=True)
JIRA='https://jira.skatelescope.org/servicedesk/customer/portal/364'
CANTO='https://skao.canto.global/v/SKAOLibrary?from_main_library'
LIVE='https://confluence.skatelescope.org/crh/'
NAV=[('index.html','Home'),('resources.html','Templates and assets'),('brand.html','Brand guidance'),('request.html','Request help'),('contribute.html','Share material')]
LIVE_LINKS={'index.html':LIVE,'resources.html':LIVE+'templates-assets-381891696.html','presentations.html':LIVE+'slide-decks-presentations-381891794.html','brand.html':LIVE+'brand-guidelines-381891606.html','request.html':LIVE+'submitting-a-request-381891661.html','contribute.html':LIVE+'how-to-submit-your-deck-381891810.html','events.html':LIVE+'events-support-381891637.html','help.html':LIVE+'tools-resources-381891870.html'}
def a(h,t,cls=''):return f'<a href="{html.escape(h,quote=True)}" class="{cls}">{t}</a>'
def card(n,title,text,href,cta):return f'<a class="card" href="{href}"><span class="card-number">{n}</span><h3>{title}</h3><p>{text}</p><span class="go">{cta} ↗</span></a>'
def callout(title,text,link='',label=''):return f'<aside class="callout"><h2>{title}</h2><p>{text}</p>{a(link,label) if link else ""}</aside>'
def rows(items):return '<ul class="list">'+''.join(f'<li>{a(h,f"<span>{t}<small>{d}</small></span><span aria-hidden=true>↗</span>")}</li>' for t,d,h in items)+'</ul>'
home='''<section class="hero"><div><p class="eyebrow">For everyone at the SKAO</p><h1>Good work starts<br>with the right resources.</h1><p class="lead">Find a template, prepare a presentation or get creative support. Everything you need to make your next piece of work feel like SKAO.</p><div class="actions"><a class="button" href="resources.html">Find a resource <span aria-hidden="true">→</span></a><a class="button secondary" href="request.html">Request creative help</a></div></div><aside class="feature"><div class="deck-art" aria-hidden="true"><span>SKA Observatory</span><strong>A shared story.<br>Your next talk.</strong></div><div class="feature-copy"><p class="eyebrow">Presenting the Observatory</p><h2>Start with the slide library</h2><p>Find templates, reusable slides and the right checks before you present.</p><a href="presentations.html">Explore presentation resources →</a></div></aside></section>'''
home+='<section class="section"><div class="section-head"><h2>What are you working on?</h2><span class="eyebrow">Start here</span></div><div class="tasks">'
home+=card('01','A presentation','Templates, reusable slides and guidance for your audience.','presentations.html','Prepare your slides')+card('02','A document or design','Start with a template and keep the brand details consistent.','resources.html','Browse resources')+card('03','Photos or video','Find approved media and check credits and permitted use.',CANTO,'Open Canto')+card('04','An event','Plan the creative materials, briefing and production handover.','events.html','Plan your materials')+'</div></section>'
home+='<section class="section split"><div><h2>Useful starting points</h2>'+rows([('Presentation library','Templates and reusable content','presentations.html'),('SKAO logos and brand guidance','Use the right files and colours','brand.html'),('Creative brief','Turn your idea into a clear request','request.html'),('Photos and video in Canto','Check each asset’s usage information',CANTO)])+'</div>'+callout('Something worth sharing?','Help colleagues reuse your good work. Contribute a presentation, suggest a resource or send material for review.','contribute.html','Choose a contribution route →')+'</section>'
resources='''<p>Choose what you need to make. Templates and presentations live in the Hub; approved photography and media live in Canto.</p><div class="filters"><label>Find a resource<input id="resourceFilter" type="search" placeholder="Try slides, logo or document"></label><label>Resource type<select id="resourceType"><option value="all">All resources</option><option value="presentation">Presentations</option><option value="document">Documents</option><option value="brand">Brand</option><option value="media">Media</option></select></label></div><p id="filterStatus" class="status" role="status">6 resources shown.</p><div class="resource-grid">'''
items=[('presentation','Presentation library','Templates, standard narrative and reusable modules.','presentations.html','Browse presentations'),('document','Document templates','Letterheads, reports and memos. Download from the current source page.',LIVE+'document-templates-381891700.html','Open template pages'),('brand','Logos and brand guidance','Logo files, typography, colours and co-branding.','brand.html','Find brand guidance'),('media','Photography and video','Approved assets with credits and usage information.',CANTO,'Open Canto'),('document','Creative request brief','Prepare purpose, scope, dates and review responsibilities.','request.html','Prepare a request'),('document','Event materials','Brief the creative work for a talk, stand or exhibition.','events.html','Plan event materials')]
for typ,title,text,href,label in items:resources+=f'<article class="card" data-resource data-type="{typ}"><span class="tag">{typ.capitalize()}</span><h2>{title}</h2><p>{text}</p>{a(href,label)}</article>'
resources+='</div>'
presentations='''<p>Start with an approved release and adapt it for your audience. A downloaded copy will not update automatically, so return to the library before your next talk.</p><div class="actions">'''+a(LIVE+'slide-decks-presentations-381891794.html','Open the current slide library','button')+a('contribute.html','Contribute a presentation','button secondary')+'''</div><h2>Choose the right starting point</h2>'''+rows([('Presentation templates','For a new talk with your own content',LIVE+'slide-decks-presentations-381891794.html'),('Standard SKAO narrative','Check the library for the latest released deck',LIVE+'slide-decks-presentations-381891794.html'),('Reusable science and telescope slides','Check audience, source, review date and permitted reuse',LIVE+'slide-decks-presentations-381891794.html')])+'''<h2>Before you present</h2><ol><li>Check the version, audience and usage notes on the source page.</li><li>Keep credits, source information and speaker notes with the slides you reuse.</li><li>Check contrast, reading order and alternative text. Caption video content.</li><li>Ask the relevant content or science owner to review new claims or changes in meaning.</li></ol><h2>When to ask for a review</h2><p>Request help for high-stakes public presentations, new claims, partner-sensitive material or substantial changes. Reusing unchanged approved slides should not create another design task.</p>'''+callout('Library release pattern','Each release should show its content owner, audience, reviewed date, format, version and reuse conditions. Drafts stay separate from released files. This is the proposed publishing pattern, not a claim that every current deck is ready.')
request='''<p>Tell us the outcome you need, the audience and the real use date. The team will confirm scope and capacity before making a delivery commitment.</p><div class="actions">'''+a(JIRA,'Go straight to the creative helpdesk','button')+'''</div><h2>Prepare a short brief</h2><p>This helper creates text for your request. Nothing is submitted or saved to the Hub. Attach files in the helpdesk after you open it.</p><noscript><p>Open the creative helpdesk to prepare your request. The optional brief helper needs JavaScript.</p></noscript><form id="briefForm" hidden><div class="form-grid">'''
fields=[('Project','What is the work called?','input',True),('Use date','When will it be used, and why then?','input',True),('Purpose and audience','What should this help people understand or do?','textarea',True),('Outputs and scope','What do you need? Include format, quantity and what is out of scope.','textarea',True),('Content and review owners','Who supplies the content and who approves the result?','textarea',False),('Inputs and constraints','Source links, budget, rights, missing information and dependencies.','textarea',False)]
for label,hint,kind,required in fields:request+=f'<label class="field">{label}{" *" if required else ""}<{kind} name="{label}" {"required" if required else ""} maxlength="3000"'+('>' if kind=='textarea' else ' type="text">')+('</textarea>' if kind=='textarea' else '')+f'<small>{hint}</small></label>'
request+='''</div><button class="button" type="submit">Prepare my request</button></form><section id="draftPanel" hidden><h2 id="draftHeading" tabindex="-1">Your request draft</h2><p>Review the wording, copy it, then submit it in the helpdesk. A request is not booked until scope and timing are confirmed.</p><pre class="output" id="briefOutput"></pre><div class="actions"><button id="copyBrief" class="button" type="button">Copy request text</button>'''+a(JIRA,'Open helpdesk to submit','button secondary')+'''</div><p id="copyStatus" class="status" role="status"></p></section><h2>What happens next?</h2><ol><li>The team reviews the request and any missing inputs.</li><li>You agree the deliverable, review responsibilities and realistic timing.</li><li>Production and feedback follow the agreed route.</li></ol><p>For event logistics, attendance or registration, use the events team’s route. Creative Production handles the accepted creative materials.</p>'''
contribute='''<p>Choose where your material belongs. Contributing a file starts a review; it does not publish it or make it approved for reuse.</p><div class="route-list">'''
contribute+=callout('Share a presentation','Include the editable deck or its source link, title, audience, event/date, content owner and any reuse restrictions. Use the creative helpdesk to attach the file or provide an approved sharing link.',JIRA,'Submit a deck for review →')
contribute+=callout('Contribute photos or video','Use your authorised Canto upload route if you have one. Include creator credit, date, location and usage/consent information. If upload access is missing, ask through the helpdesk. A library browsing link is not an upload portal.',CANTO,'Open Canto →')
contribute+=callout('Suggest a correction or resource','Send the Hub page link, what needs changing and the source of the corrected information. This is also the route for missing templates and inaccessible files.',JIRA,'Send a correction or suggestion →')
contribute+='''</div><h2>Before sharing</h2><ul><li>Check that the destination and permissions are suitable for the material.</li><li>Include restrictions and missing approvals, rather than assuming they are resolved.</li><li>Use a link to the working source when an attachment would create a competing version.</li></ul><h2>After submission</h2><p>The responsible owner checks suitability, content and rights before release. Accepted presentation releases belong in the Hub; approved media belongs in Canto. The review route and timing are confirmed for the submission.</p>'''
brand='''<p>Use the SKAO Brand Book as the authority for visual identity. Start from existing assets and templates rather than recreating the logo or guessing colours.</p><div class="actions">'''+a(LIVE+'brand-guidelines-381891606.html','Open current brand guidance','button')+'''</div><h2>The essentials</h2><ul><li><strong>Primary colours:</strong> Blueshift Navy, #070068, and Redshift Magenta, #E70068.</li><li><strong>Typeface:</strong> Noto Sans. Use Verdana when Noto Sans is unavailable.</li><li><strong>Logo:</strong> use the supplied artwork unchanged. Keep at least half the logo’s height clear on all sides.</li><li><strong>Language:</strong> use British English, plain wording and sentence-case headings.</li></ul><h2>Colour and accessibility</h2><p>Brand colours do not make every colour pairing accessible. Use navy for body links on white. Keep magenta as an accent and check contrast for the exact foreground, background, size and weight.</p><h2>Co-branding</h2><p>For partners and related programmes, follow the applicable identity and approval guidance. Do not invent a combined logo or assume one set of rules applies to every partner.</p><h2>Source</h2><p>These essentials follow the SKAO Brand Book v2, March 2022. The existing Hub colour page contains provisional values that need reconciling before rollout.</p>'''
events='''<p>Bring the audience, purpose and use date first. Reuse an existing kit where it does the job, then brief only what needs to change.</p><h2>Define the creative package</h2><ul><li>Presentation, stand graphics, print, video or another clearly specified output.</li><li>Venue/supplier specifications, quantity, dimensions, languages and access needs.</li><li>Content owner, final reviewer, proof dates and supplier handoff.</li><li>Confirmed budget and required permissions.</li></ul><h2>Keep responsibilities clear</h2><p>The events team owns event planning, attendance and logistics. Creative Production scopes and delivers the accepted creative materials. Supplier lead times and review dates must be confirmed for the actual job.</p><div class="actions">'''+a('request.html','Brief the creative work','button')+a(LIVE+'events-support-381891637.html','Open event guidance','button secondary')+'</div>'
helptext='''<details><summary>Where are photographs and video?</summary><p>In Canto. Check the asset’s credit and usage information before reuse.</p></details><details><summary>Where should presentations live?</summary><p>Released presentations live in the Creative Hub. Keep draft working files separate and link to the approved source page.</p></details><details><summary>Can I upload directly here?</summary><p>This theme routes submissions to the existing helpdesk or an authorised Canto upload route. It does not create another file store.</p></details><details><summary>Is my request automatically accepted?</summary><p>No. Scope, capacity and delivery dates need to be confirmed by the team.</p></details><details><summary>A link or resource is missing</summary><p>Send the page URL and the problem to the creative helpdesk.</p></details>'''+a(JIRA,'Open the creative helpdesk','button')
PAGES={'index.html':('Creative Hub',home),'resources.html':('Find a resource',resources),'presentations.html':('Prepare a presentation',presentations),'request.html':('Request creative help',request),'contribute.html':('Contribute material',contribute),'brand.html':('Brand guidance',brand),'events.html':('Plan event materials',events),'help.html':('Help with the Hub',helptext)}
from journeys import revise
PAGES=revise(PAGES,JIRA,CANTO,LIVE)
from interiors import revise as revise_interiors, ROUTES
PAGES, INTERIOR_META=revise_interiors(PAGES,JIRA,CANTO)
from polish import revise as revise_polish, text, summary, sidebar as section_sidebar, section_of, SECTIONS, EXTRA, members_of, nav as mega_nav, FULL_WIDTH
PAGES,SOURCE_TITLES=revise_polish(PAGES,INTERIOR_META,JIRA)
home=PAGES['index.html'][1]
request=PAGES['request.html'][1]
production_presentations=PAGES['presentations.html'][1].replace(LIVE+'slide-decks-presentations-381891794.html', '#library-sections').replace('Open the current slide library', 'Browse library sections')
svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"/></svg>'
def header(current):
 links=mega_nav(current)
 return f'''<a href="#main-content" class="skip">Skip to main content</a><header><div class="brandbar"><div class="wrap brandrow"><a class="brand" href="index.html"><img src="images/skao-logo-white.png" width="100" alt="SKA Observatory"><span class="brand-title">Creative <strong>Hub</strong></span></a><div class="brandtools"><span class="staff-label">Resources for staff</span><button id="motionToggle" class="motion-toggle" aria-label="Pause header animation" aria-pressed="false" title="Pause header animation" hidden><span aria-hidden="true">Ⅱ</span></button><button id="themeToggle" class="icon-button" aria-label="Toggle dark mode" aria-pressed="false"><span class="theme-moon">{svg}</span><span class="theme-sun" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg></span></button></div></div></div><div class="wrap navrow"><button id="menuButton" class="mobile-menu" aria-expanded="false" aria-controls="mainNav">Menu</button><nav id="mainNav" class="navlinks" aria-label="Main navigation">{links}</nav><button class="search-trigger" data-search><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><span>Search the Hub</span> <kbd data-shortcut>Ctrl K</kbd></button></div></header>'''
def footer():return '''<footer class="footer"><div class="wrap footer-inner"><div class="footer-identity"><strong>Creative Hub</strong><span>Templates, brand guidance and creative support for everyone at the SKAO.</span></div><nav aria-label="Footer">'''+a('resources.html','Templates and assets')+a('request.html','Request creative help')+a('faq.html','Common questions')+a('contribute.html','Share material')+a(CANTO,'Canto library ↗')+a(JIRA,'Report a problem ↗')+'''</nav></div></footer><dialog id="searchDialog" aria-labelledby="searchTitle"><div class="dialog-title"><h2 id="searchTitle">Search the Hub</h2><button id="closeSearch" class="close-button" aria-label="Close search">×</button></div><p class="search-scope">Searches Hub pages and guidance. Photos and video are in <a href="'''+CANTO+'''">Canto ↗</a>.</p><form id="searchForm" role="search"><label class="field">What do you need?<input id="searchInput" type="search" maxlength="120" autocomplete="off" placeholder="Try presentation, logo or request"></label></form><div id="searchSuggest" class="search-suggest"><div id="recentPages" hidden><h3>Recently viewed</h3><div id="recentList" class="suggest-list"></div></div><div><h3>Quick links</h3><div class="suggest-list"><a href="logos.html">Logo files</a><a href="standard-template.html">Slide template</a><a href="colours-and-type.html">Colours</a><a href="fonts.html">Fonts</a><a href="email-signatures.html">Email signature</a><a href="request.html">Request creative help</a><a href="'''+CANTO+'''">Photos and video in Canto ↗</a></div></div></div><p id="searchStatus" role="status" class="status"></p><div id="searchResults" class="search-results"></div><div class="search-fallback"><a href="resources.html">Browse templates and assets →</a><a href="request.html">Ask for help →</a></div></dialog><p id="copyAnnounce" class="visually-hidden" role="status"></p><script src="js/theme.js" defer></script><script src="js/main.js?v=lists-20260924" defer></script>'''
def shell(title,body,current,home=False):
 sidebar=section_sidebar(current,SOURCE_TITLES)
 sec=section_of(current)
 crumb=(a(sec[2],sec[1])+' / ') if sec and sec[2]!=current else ''
 main=body if home else '<div class="page-band"><div class="breadcrumbs">'+a('index.html','Creative Hub')+' / '+crumb+html.escape(title)+'</div><div class="page-head"><p class="eyebrow">'+html.escape(INTERIOR_META.get(current,{}).get('group','Creative Hub'))+'</p><h1>'+html.escape(title)+'</h1></div></div>'+('<div class="page-grid full-width">' if current in FULL_WIDTH else '<div class="page-grid">'+sidebar)+'<article class="content-body">'+body+'</article></div>'
 return '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+html.escape(title)+' | SKAO Creative Hub</title><link rel="stylesheet" href="css/style.css?v=lists-20260924"><script src="js/boot.js"></script></head><body data-mode="preview">'+header(current)+'<div class="wrap preview-note">Design preview · Guidance is proposed; library links open the current staff services.</div><main id="main-content" class="wrap" tabindex="-1">'+main+'</main>'+footer()+'</body></html>'
for name,(title,body) in PAGES.items():
 (D/name).write_text(shell(title,body,name,name=='index.html'))
 (R/'content'/name.replace('.html','.html')).write_text(body)
for folder in ['css','js','images','fonts']:shutil.copytree(R/folder,D/folder,dirs_exist_ok=True)
index=[{'title':t,'href':name,'group':INTERIOR_META.get(name,{}).get('group',''),'excerpt':{'request.html':'Prepare a brief and submit a creative request.','contribute.html':'Share slides, photos, video or corrections for review.'}.get(name) or summary(body),'keywords':text(re.sub(r'<section class="catalogue".*?</section>','',body,flags=re.S))} for name,(t,body) in PAGES.items() if name!='index.html']
(D/'search-index.json').write_text(json.dumps(index))
# Production uses this same visual shell. Direct task panels are rendered only on home.
prod=shell('$stringEscapeUtils.escapeHtml($page.title)','$page.content','',False)
prod=prod.replace('data-mode="preview"','data-mode="confluence" data-context="$stringEscapeUtils.escapeHtml($contextPath)"')
prod=prod.replace('<div class="wrap preview-note">Design preview · Guidance is proposed; library links open the current staff services.</div>','')
# Replace article and homepage based on immutable ID, and use actual page-tree context.
start=prod.index('<main id="main-content"');end=prod.index('</main>',start)+7
main='''<main id="main-content" class="wrap" tabindex="-1">
#if($page.id == $pages.home.id)
'''+home+'''
#else
<div class="page-band"><div class="breadcrumbs"><a href="$pages.home.absoluteLink">Creative Hub</a>
#foreach($ancestor in $page.ancestors)
#if($ancestor.id != $pages.home.id) / <a href="$ancestor.absoluteLink">$stringEscapeUtils.escapeHtml($ancestor.title)</a>#end
#end
 / $stringEscapeUtils.escapeHtml($page.title)</div>
<div class="page-head"><p class="eyebrow">$displayGroup</p><h1>$stringEscapeUtils.escapeHtml($page.title)</h1></div></div>
'''
ROUTE_IDS={filename:id for id,title,filename,group in ROUTES}
# Sidebar per section; section landings and the catalogue are full width.
wide=' || '.join(f'$page.id.toString() == "{ROUTE_IDS[f]}"' for f in sorted(FULL_WIDTH))
chain=f'#if({wide})\n<div class="page-grid full-width">\n'
for sec in SECTIONS:
 key,landing=sec[0],sec[2]
 members=[m for m in members_of(sec) if section_of(m)[0]==key]+[x for x,k in EXTRA.items() if k==key]
 cond=' || '.join(f'$page.id.toString() == "{ROUTE_IDS[m]}"' for m in members)
 chain+=f'#elseif({cond})\n<div class="page-grid">'+section_sidebar(landing,SOURCE_TITLES)+'\n'
main+=chain+'#else\n<div class="page-grid">'+section_sidebar('',SOURCE_TITLES)+'\n#end\n'
main+='''<article class="content-body">
'''
for i,(id,title,filename,group) in enumerate(ROUTES):
 main+=('#if' if i==0 else '#elseif')+f'($page.id.toString() == "{id}")\n'+PAGES[filename][1]+'\n'
main+='''#else
$page.content
#if($page.children.size() > 0)<section class="section" id="library-sections"><h2>Explore this section</h2><ul class="list">#foreach($child in $page.children)<li><a href="$child.absoluteLink">$stringEscapeUtils.escapeHtml($child.title)</a></li>#end</ul></section>#end
#end
</article></div>
#end
</main>'''
prod=prod[:start]+main+prod[end:]
# Route pages show their Hub section in the breadcrumb, matching the sidebar.
ancestors="""#foreach($ancestor in $page.ancestors)
#if($ancestor.id != $pages.home.id) / <a href="$ancestor.absoluteLink">$stringEscapeUtils.escapeHtml($ancestor.title)</a>#end
#end"""
assert ancestors in prod
crumbs=''
for n,sec in enumerate(SECTIONS):
 key,label,landing=sec[0],sec[1],sec[2]
 members=[m for m in members_of(sec) if section_of(m)[0]==key and m!=landing]+[x for x,k in EXTRA.items() if k==key]
 cond=' || '.join(f'$page.id.toString() == "{ROUTE_IDS[m]}"' for m in members)
 crumbs+=('#if' if n==0 else '#elseif')+f'({cond}) / <a href="{landing}">{label}</a>\n'
crumbs+=f'#elseif($page.id.toString() == "{ROUTE_IDS[SECTIONS[0][2]]}"'+''.join(f' || $page.id.toString() == "{ROUTE_IDS[sec[2]]}"' for sec in SECTIONS[1:])+')\n#else\n'+ancestors+'\n#end'
prod=prod.replace(ancestors,crumbs,1)
PAGE_TITLES={'index.html':'SKAO Creative Hub Home','resources.html':'Templates & Assets','presentations.html':'Slide Decks & Presentations','brand.html':'Brand Guidelines','request.html':'Submitting a Request','contribute.html':'How to Submit Your Deck','events.html':'Events Support','help.html':'Tools & Resources'}
PAGE_TITLES.update({filename:title for id,title,filename,group in ROUTES})
for local,title in PAGE_TITLES.items():
 prod=prod.replace('href="'+local+'"', ("href=\"$link.page('CRH', '"+title+"')\"") if "'" not in title else ('href="$link.page(\"CRH\", \"'+title+'\")"'))
prod=prod.replace('https://confluence.skatelescope.org/crh/document-templates-381891700.html', "$link.page('CRH', 'Document Templates')")
for slug,title in [('Standard+SKAO+Template','Standard SKAO Template'),('About+SKAO+Master+Deck','About SKAO Master Deck'),('Science+Case+Presentations','Science Case Presentations')]:
 prod=prod.replace('https://confluence.skatelescope.org/display/CRH/'+slug, "$link.page('CRH', '"+title+"')")
for folder in ['css','js','images']:prod=prod.replace('"'+folder+'/','"${theme.baseUrl}/'+folder+'/')
prod=prod.replace('<title>$stringEscapeUtils.escapeHtml($page.title) | SKAO Creative Hub</title>','<title>$stringEscapeUtils.escapeHtml($page.title) | SKAO Creative Hub</title>')
prod=prod.replace('<link rel="stylesheet"', '$webPanels\n$page.resources.meta\n$page.resources.css\n$page.resources.js\n<link rel="stylesheet"',1)
prod=prod.replace('</footer>','<div class="wrap footer-platform">$attributionLine</div></footer>')
display_titles={'381891696':'Templates and assets','381891810':'Share material','381891794':'Prepare a presentation','381891661':'Request creative help'}
display_titles.update({id:PAGES[filename][0] for id,title,filename,group in ROUTES})
setup="#set($displayTitle = $page.title)\n#set($displayGroup = \"Creative Hub\")\n"
for id,title,filename,group in ROUTES: setup+=f'#if($page.id.toString() == \"{id}\")#set($displayGroup = \"{group}\")#end\n'
for page_id,title in display_titles.items(): setup+=f'#if($page.id.toString() == "{page_id}")#set($displayTitle = "{title}")#end\n'
prod=setup+prod.replace('$stringEscapeUtils.escapeHtml($page.title)', '$stringEscapeUtils.escapeHtml($displayTitle)')
routes='''<div id="hubRoutes" hidden>
#macro(hubRoute $node)
<a data-page-id="$node.id" href="$node.absoluteLink">$stringEscapeUtils.escapeHtml($node.title)</a>
#foreach($child in $node.children)#hubRoute($child)#end
#end
#hubRoute($pages.home)
</div>'''
prod=prod.replace('</body>',routes+'</body>')
(R/'page.vm').write_text(prod)
for id,title,filename,group in ROUTES: LIVE_LINKS[filename]='https://confluence.skatelescope.org/pages/viewpage.action?pageId='+id
# Copy the exact production article fragments for controlled import into Confluence.
# Each route file is plain HTML for editors, not an automated publication script.
for name,(title,body) in PAGES.items():
 if name=='index.html':continue
 for local,live in LIVE_LINKS.items():body=body.replace('href="'+local+'"','href="'+live+'"')
 (R/'content'/name.replace('.html','-confluence.html')).write_text(body)
(R/'evidence/interior-route-map.json').write_text(json.dumps({name:{**meta,'display_title':PAGES[name][0]} for name,meta in INTERIOR_META.items()},indent=2))
print('Built',len(PAGES),'preview pages and production page.vm')
