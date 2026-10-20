/* Unit/DOM checks. Run with NODE_PATH pointing at dependencies jsdom and velocityjs. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {JSDOM}=require('jsdom'),Velocity=require('velocityjs');
const root=path.resolve(__dirname,'..');let checks=[];
function pass(name){checks.push(name)}
function dom(page='index.html',mode='preview'){
 const d=new JSDOM(fs.readFileSync(path.join(root,'docs',page),'utf8'),{url:'http://localhost/'+page,runScripts:'outside-only'}),w=d.window;
 w.matchMedia=()=>({matches:false});w.HTMLElement.prototype.scrollIntoView=()=>{};
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'))};
 w.document.body.dataset.mode=mode;w.fetch=async()=>({ok:true,json:async()=>[{title:'Presentation',href:'presentations.html',excerpt:'Slides',keywords:'presentation'}]});
 w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));return d;
}
const wait=()=>new Promise(r=>setTimeout(r,10));
(async()=>{
 const d=dom(),w=d.window,q=s=>w.document.querySelector(s);
 q('[data-search]').click();assert(q('dialog').open);q('#searchInput').value='presentation';q('#searchForm').dispatchEvent(new w.Event('submit',{cancelable:true}));await wait();assert.equal(q('#searchResults a:not(.search-answer)').textContent,'PresentationSlides');pass('Preview search returns actual navigable results');assert(q('.search-answer').textContent.includes('Standard SKAO template'),'a quick answer sits above the results');q('#searchInput').value='where can I find a presentation';q('#searchForm').dispatchEvent(new w.Event('submit',{cancelable:true}));await wait();assert.equal(q('#searchResults a:not(.search-answer)')?.textContent,'PresentationSlides','plain questions find pages');q('#searchInput').value='where do I find the letterhead';q('#searchForm').dispatchEvent(new w.Event('submit',{cancelable:true}));await wait();assert(q('.search-answer').textContent.includes('Letterheads'));q('#searchInput').value='zzqx';q('#searchForm').dispatchEvent(new w.Event('submit',{cancelable:true}));await wait();assert(!q('.search-answer'));pass('Quick answers and plain questions in search');
 q('#closeSearch').click();assert(!q('dialog').open);pass('Search closes');d.window.close();
 const live=dom('index.html','confluence'),v=live.window,el=s=>v.document.querySelector(s);let url;
 v.fetch=async u=>{if(String(u).includes('attachment'))return {ok:true,json:async()=>({results:[]})};url=u;return {ok:true,json:async()=>({results:[{id:'1',title:'<img src=x onerror=alert(1)>',ancestors:[{title:'<script>bad</script>'}],_links:{webui:'/pages/1'}}]})}};
 el('[data-search]').click();el('#searchInput').value='" OR space="OTHER';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();
 assert.equal(el('#searchResults img'),null);assert.equal(el('#searchResults script'),null);assert(el('#searchResults').textContent.includes('<img'));assert(new URL(url,'http://localhost').searchParams.get('cql').includes('\\"'));pass('Production search escapes CQL input and renders metadata as text');
 v.fetch=async()=>({status:403,ok:false});el('#searchInput').value='permission';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();assert(el('#searchStatus').textContent.includes('sign in'));pass('Permission failure is distinguished from no results');
 let complete=[];v.fetch=()=>new Promise(resolve=>complete.push(resolve));el('#searchInput').value='old';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));el('#searchInput').value='new';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));
 // Each search asks for files and pages: requests 0-1 are the old search, 2-3 the new one.
 const none={ok:true,json:async()=>({results:[]})};complete[2](none);complete[3]({ok:true,json:async()=>({results:[{id:'2',title:'New result',_links:{webui:'/new'}}]})});await wait();complete[0](none);complete[1]({ok:true,json:async()=>({results:[{id:'1',title:'Old result',_links:{webui:'/old'}}]})});await wait();assert(el('#searchResults').textContent.includes('New result'));assert(!el('#searchResults').textContent.includes('Old result'));pass('Late search responses cannot overwrite newer results');live.window.close();
 const gh=dom('faq.html'),ghd=gh.window.document,ghq=s=>ghd.querySelector(s);
 assert.equal(ghq('.page-head h1').textContent,'Common questions');assert(ghq('.gh-intro a.button[href*="servicedesk"]').textContent.includes('Comms helpdesk'),'the help page opens with the Comms helpdesk');
 assert(ghd.querySelectorAll('.help-answers details').length>=6,'then short answers');assert(ghq('#share h2')&&ghq('details#share-a-deck')&&ghq('details#share-photos'),'and how to share a deck, photos or video');
 assert(!ghq('.brief-card')&&!ghq('.gh-steps')&&!ghq('.copy-template'),'no brief checklist or steps');gh.window.close();
 const hdr=dom('index.html').window.document;assert.deepEqual([...hdr.querySelectorAll('#mainNav a')].map(a=>a.textContent),['Presentations','Documents','Brand','Photos and video','Events','How-to guides'],'six sections in the header; help lives in the footer');
 assert([...hdr.querySelectorAll('.footer a')].some(a=>a.getAttribute('href')==='faq.html'&&a.textContent==='Get help'),'Get help in the footer');
 for(const [old,to] of [['working-with-us.html','faq.html'],['contribute.html','faq.html#share']]){const mv=dom(old).window.document;assert.equal(mv.querySelector('.moved-note a.button').getAttribute('href'),to,old+' now points to Common questions');}
 pass('Get help is one Common questions page in the footer, with sharing folded in');
 for(const [old,to] of [['request.html','faq.html'],['video-request.html','faq.html'],['timing.html','faq.html'],['help.html','faq.html'],['creative-services.html','faq.html'],['canto-guide.html','canto-access.html'],['email-signatures.html','documents.html'],['widescreen-template.html','standard-template.html'],['science-slides.html','master-deck.html'],['reports.html','memos.html'],['hero-images.html','media.html'],['event-safety.html','events.html'],['merchandise.html','stands.html'],['event-checklist.html','events.html#lead-times']]){
  const mv=dom(old).window.document;assert.equal(mv.querySelector('.moved-note a.button').getAttribute('href'),to,old+' points to its new home');}
 assert(dom('email-signatures.html').window.document.querySelector('.moved-note').textContent.includes('managed by IT'),'retired signatures page says why');
 assert(!fs.readdirSync(path.join(root,'docs')).filter(f=>f.endsWith('.html')&&!['request.html','creative-services.html','timing.html','video-request.html','print.html','business-cards.html','help.html','updates.html','archive.html','canto-guide.html','email-signatures.html','working-with-us.html','contribute.html'].includes(f)).some(f=>/href="(request|creative-services|timing|video-request|print|business-cards|help|updates|archive|canto-guide|email-signatures|working-with-us|contribute)\.html["#]/.test(fs.readFileSync(path.join(root,'docs',f),'utf8'))),'no links to moved pages');
 pass('Moved pages point to their new home');
 const t=dom();t.window.matchMedia=()=>({matches:true});t.window.eval(fs.readFileSync(path.join(root,'js/theme.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", function () {",'(function () {').replace(/\}\);\s*$/, '})();'));t.window.document.querySelector('#themeToggle').click();assert(t.window.document.documentElement.classList.contains('dark'));assert.equal(t.window.localStorage.getItem('crh-theme'),'dark');pass('Reduced-motion toggle changes and saves theme without animation');t.window.close();
 const tpl=fs.readFileSync(path.join(root,'page.vm'),'utf8');Velocity.parse(tpl);pass('Velocity template parses');
 const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
 function page(id,title){return {id:String(id),title,absoluteLink:'/crh/'+id,ancestors:[],children:[],resources:{meta:'',css:'',js:''},content:'<p>Confluence content</p>'};}
 const home=page('381887066','Home'),deep=page('99','Quotes " and <markup>');deep.ancestors=[home];deep.parent=home;
 for(const p of [home,deep,page('381891661','Submitting a Request')]){
 const out=Velocity.render(tpl,{page:p,pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution'});
 const doc=new JSDOM(out).window.document;assert.equal(doc.querySelectorAll('h1').length,1);assert(!doc.title.includes('$'));assert(out.includes('Attribution'));
 if(p===deep){assert(doc.querySelector('.content-body').textContent.includes('Confluence content'));assert.equal(doc.title,'Quotes " and <markup> | SKAO Creative Hub');}
 if(p.id==='381891661')assert(doc.querySelector('.moved-note'),'the old request page points to Get help');
 }
 pass('Home, deep page and request route render with escaping and one H1');
 for(const file of fs.readdirSync(path.join(root,'docs')).filter(f=>f.endsWith('.html'))){const doc=new JSDOM(fs.readFileSync(path.join(root,'docs',file),'utf8')).window.document;assert.equal(doc.querySelectorAll('h1').length,1);for(const e of doc.querySelectorAll('[href],[src]')){const h=e.getAttribute('href')||e.getAttribute('src');assert.notEqual(h,'#');if(!/^(https?:|mailto:|#)/.test(h))assert(fs.existsSync(path.join(root,'docs',h.split('#')[0].split('?')[0])),`${file}: ${h}`);}}
 pass('All preview pages have one H1 and resolve local links/assets');
 const hd=dom(),hw=hd.window,hq=s=>hw.document.querySelector(s);
 assert.equal(hw.document.querySelectorAll('[data-search]').length,1);assert(!hq('#homeSearch'));hq('[data-search]').click();hq('#searchInput').value='presentation';hq('#searchForm').dispatchEvent(new hw.Event('submit',{cancelable:true}));await wait();assert(hq('dialog').open);assert(hq('#searchResults a'));hq('#searchInput').dispatchEvent(new hw.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert(!hq('dialog').open);assert.equal(hw.document.activeElement,hq('[data-search]'));assert.equal(hq('.welcome-band .presentation-feature').getAttribute('href'),'presentations.html');assert(!hq('.latest-strip').hidden,'strip shows once examples load');assert(hq('.latest-strip #latestAssets'));assert(!hq('.help-band'),'help lives in the footer, not a second band');assert.equal(hw.document.querySelectorAll('.section-index a').length,6);assert(!hq('.quick-links a[href="working-with-us.html"]'),'help lives in the footer band');assert(hq('.footer-cta a.button[href*="servicedesk"]'),'the footer band opens the helpdesk');hd.window.close();pass('Single navigation search works and restores focus; homepage has search, the presentations feature and a Just added strip without repeating sections or help');
 const rd=dom('resources.html'),rw=rd.window,rq=s=>rw.document.querySelector(s);
 assert.equal(rw.document.querySelectorAll('.choice-card').length,0,'no duplicate starting-point cards');assert(rq('.page-grid.full-width .file-feed'));assert(!rq('.sidebar'));
 assert.equal(rq('.page-head h1').textContent,'Latest files');assert.equal(rw.document.querySelectorAll('.feed-row').length,4,'the preview shows four example files');
 assert(rw.document.querySelectorAll('.feed-row .dl-file[aria-disabled="true"]').length===4&&!rq('.feed-row a[href]'),'preview examples link nowhere');
 for(const t of ['all','presentations','documents','brand'])assert(rq(`.type-chips [data-type-filter="${t}"]`),t);rd.window.close();pass('Latest files is one full-width list of the newest files, with section filters and examples in the preview');
 const pd=new JSDOM(fs.readFileSync(path.join(root,'docs/presentations.html'),'utf8'));
 const pdoc=pd.window.document,destinations=[...pdoc.querySelectorAll('.directory .dir-row')].map(a=>a.getAttribute('href'));
 for(const f of ['standard-template.html','partner-templates.html','master-deck.html','site-progress.html','formatting-slides.html'])assert(destinations.includes(f),f);
 assert.deepEqual([...pdoc.querySelectorAll('.directory .dir-group h2')].map(h=>h.firstChild.textContent.trim()),['Templates','Slide decks','Site progress','How to']);assert(!pdoc.querySelector('.dir-add'),'no separate share row');
 assert(!destinations.includes('recent-talks.html')&&!fs.existsSync(path.join(root,'docs/recent-talks.html')),'Recent talks is folded into Approved slide decks');
 assert.equal(pdoc.querySelector('.dir-row[href="master-deck.html"] strong').textContent,'Approved slide decks');
 assert.equal(new Set(destinations).size,destinations.length);assert(!pdoc.querySelector('details .dir-row'),'page links are never collapsed');const railItems=[...pdoc.querySelectorAll('.landing-rail details.rail-item')];assert.equal(railItems.length,3);assert(railItems.every(d=>!d.open),'several pieces of advice start closed, each one click away');assert(pdoc.querySelector('.landing-main > .task-intro'),'the intro sits beside Before you start');assert(!pdoc.querySelector('.landing-rail a.button'),'no on-request box: help lives in the footer');assert(!pdoc.querySelector('.dir-meta.req,.dir-legend'),'no status dots or legend');assert(pdoc.querySelector('.landing-rail .source-check'));assert(pdoc.querySelector('.landing-rail .reuse-decision'));
 pass('Presentations landing shows every presentation page, grouped and visible, with freshness/reuse guidance');
 for(const id of ['381891696','381891810']){const out=Velocity.render(tpl,{page:page(id,'Test'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});const doc=new JSDOM(out).window.document;assert(doc.querySelector(id==='381891696'?'.page-grid.full-width .file-feed':'.content-body .moved-note a.button'));assert(![...doc.querySelectorAll('a')].some(a=>a.getAttribute('href').includes('$link')));}pass('Latest files and the contribution landing page render in the production template');
 for(const [title,section] of [['Partner templates','Presentations'],['Partner logos','Brand']]){const out=Velocity.render(tpl,{page:page('555001',title),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,t)=>'/crh/'+encodeURIComponent(t)}});const doc=new JSDOM(out).window.document;
  assert.equal(doc.querySelector('.asset-panel').dataset.pageId,'555001',title+' reads its own attachments');assert.equal(doc.querySelector('.sidebar .section-nav h2').textContent,section);assert(!out.includes('99000000'),'no stand-in IDs in production');}
 pass('New partner pages render in production by title, before their page IDs are known');
 const routes=JSON.parse(fs.readFileSync(path.join(root,'evidence/interior-route-map.json')));
 assert.equal(Object.keys(routes).length,63);
 for(const [file,route] of Object.entries(routes)){
  const out=Velocity.render(tpl,{page:page(route.id,route.source_title),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});
  const doc=new JSDOM(out).window.document;
  assert.equal(doc.querySelectorAll('h1').length,1,file);
  assert.equal(doc.querySelector('h1').textContent.trim(),route.display_title,file);
  assert(doc.querySelector('.task-intro, .site-hero'),file);
  assert(!doc.querySelector('.content-body').textContent.includes('Confluence content'),file);
  assert(![...doc.querySelectorAll('a')].some(a=>(a.getAttribute('href')||'').includes('$link')),file);
  assert(!/ASSET TO ADD|jira\.skao\.int|#003366|#00A4A6/.test(out),file);
 }
 pass('All 63 production routes (60 observed, 3 proposed) render their reviewed content and resolved links');
 const sd=dom(),sw=sd.window,sq=s=>sw.document.querySelector(s);
 sw.fetch=async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(path.join(root,'docs/search-index.json'),'utf8'))});
 const run=async v=>{sq('#searchInput').value=v;sq('#searchInput').dispatchEvent(new sw.Event('input'));sq('#searchForm').dispatchEvent(new sw.Event('submit',{cancelable:true}));await wait();return [...sw.document.querySelectorAll('#searchResults a:not(.search-answer) strong')].map(e=>e.textContent);};
 sq('[data-search]').click();assert(!sq('#searchSuggest').hidden);assert(sw.document.querySelectorAll('#searchSuggest a').length>=6);
 assert.equal((await run('logo'))[0],'Logos and icons');
 assert((await run('powerpoint template')).some(t=>/template/i.test(t)));
 assert((await run('color')).some(t=>/colour/i.test(t)));assert(sq('#searchResults mark'));assert(sq('#searchSuggest').hidden);
 assert.equal((await run('href')).length,0,'markup must not be searchable');
 await run('');assert(!sq('#searchSuggest').hidden);
 pass('Preview search ranks titles first, expands synonyms, ignores markup and offers quick links');
 sd.window.close();
 const bd=dom('brand.html'),bw=bd.window;let copied;bw.navigator.clipboard={writeText:async v=>{copied=v}};
 const copyBtn=bw.document.querySelector('[data-copy="#070068"]');assert(copyBtn);copyBtn.click();await wait();assert.equal(copied,'#070068');assert(bw.document.querySelector('#copyAnnounce').textContent.includes('#070068'));
 pass('Brand colour values copy to the clipboard with an announcement');bd.window.close();
 const tpl2=Velocity.render(tpl,{page:page('381887066','Home'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});
 const hdoc=new JSDOM(tpl2).window.document;const quick=[...hdoc.querySelectorAll('.quick-links a, #searchSuggest a')].map(a=>a.getAttribute('href'));
 assert(quick.length>=10);assert(quick.every(h=>h.startsWith('/crh/')||h.startsWith('https://')),quick.join(' '));
 pass('Quick links resolve to Confluence pages in the production template');
 {const lid=routes['letterheads.html'].id,lowId=routes['low-slides.html'].id,calls=[];
  const fd=dom('resources.html','confluence'),fw=fd.window,fdoc=fw.document,fq=s=>fdoc.querySelector(s);
  fw.fetch=async u=>{const s=String(u);calls.push(s);
   if(s.includes('/child/attachment'))return {ok:true,json:async()=>({results:s.includes(`/content/${lowId}/`)?[
    {title:'2026-10 SKA-Low progress.pptx',version:{when:'2026-10-15T10:00:00Z',number:1},extensions:{fileSize:3145728},_links:{download:`/download/attachments/${lowId}/a.pptx`}},
    {title:'site-photo.jpg',version:{when:'2026-10-16T10:00:00Z'},_links:{download:`/download/attachments/${lowId}/site-photo.jpg`}}]:[]})};
   return {ok:true,json:async()=>({results:[
    {title:'SKAO_Letterhead_UNRESTRICTED.docx',container:{id:lid,title:'Letterheads',_links:{webui:'/letterheads.html'}},version:{when:'2026-10-10T09:00:00Z',number:2},extensions:{fileSize:146432},_links:{download:`/download/attachments/${lid}/l.docx`}},
    {title:'SRCNet logos.zip',container:{id:'777',title:'Partner logos',_links:{webui:'/display/CRH/Partner+logos'}},version:{when:'2026-09-02T09:00:00Z',number:1},extensions:{fileSize:2048},_links:{download:'/download/attachments/777/p.zip'}},
    {title:'<img src=x onerror=alert(1)>.pdf',container:{id:lid,title:'Letterheads'},version:{when:'2026-08-01T09:00:00Z'},_links:{download:'//evil.example/x.pdf'}}]})};};
  fdoc.body.dataset.mode='confluence';fw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();await wait();
  assert(calls.some(c=>new URL(c,'http://localhost').searchParams.get('cql')?.includes('label="approved"')),'approved files across the Hub');assert(calls.some(c=>c.includes(`/content/${lowId}/child/attachment`)),'and the site teams\' slides, which need no label');
  assert.deepEqual([...fdoc.querySelectorAll('.feed-month h2')].map(h=>h.firstChild.textContent),['October 2026','September 2026'],'grouped by month, newest first');
  assert.deepEqual([...fdoc.querySelectorAll('.feed-name')].map(n=>n.textContent),['SKA-Low progress','SKAO Letterhead UNRESTRICTED','SRCNet logos'],'site photo and off-site links left out; date prefixes read');
  const lr=[...fdoc.querySelectorAll('.feed-row')][1];assert.equal(lr.querySelector('.feed-where a').getAttribute('href'),'http://localhost/letterheads.html#downloads');assert.equal(lr.querySelector('.feed-section').textContent,'Documents');assert(lr.querySelector('.feed-when').textContent.startsWith('Updated 10 Oct'));
  assert.equal([...fdoc.querySelectorAll('.feed-row')][2].querySelector('.feed-section').textContent,'Brand','a page not yet in the map is placed by its title');assert(!fq('.feed-list img'),'file names render as text');
  assert.deepEqual([...fdoc.querySelectorAll('.type-chips button')].map(b=>b.textContent),['All 3','Presentations 1','Documents 1','Brand 1']);
  fq('.type-chips [data-type-filter="documents"]').click();assert.deepEqual([...fdoc.querySelectorAll('.feed-row:not([hidden]) .feed-name')].map(n=>n.textContent),['SKAO Letterhead UNRESTRICTED']);assert(fdoc.querySelectorAll('.feed-month[hidden]').length===1,'empty months fold away');
  fq('#fileFilter').value='zzzz';fq('#fileFilter').dispatchEvent(new fw.Event('input'));assert(!fq('#feedEmpty').hidden);fq('#clearFeed').click();assert.equal(fdoc.querySelectorAll('.feed-row:not([hidden])').length,3);
  fd.window.close();pass('Latest files lists approved files and site slides by month, placed on their page and section, with filters, and renders safely');}
 const idx=JSON.parse(fs.readFileSync(path.join(root,'docs/search-index.json'),'utf8'));assert(!idx.find(r=>r.href==='resources.html').keywords.includes('Letterheads'),'catalogue must not flood the search index');
 const hs=dom(),hsw=hs.window,hsq=s=>hsw.document.querySelector(s);hsw.fetch=async()=>({ok:true,json:async()=>idx});
 hsq('#heroSearch').value='l';hsq('#heroSearch').dispatchEvent(new hsw.Event('input'));assert(hsq('dialog').open);assert.equal(hsq('#searchInput').value,'l');assert.equal(hsq('#heroSearch').value,'');
 pass('Homepage search box hands typing over to the search dialog');hs.window.close();
 const resOut=Velocity.render(tpl,{page:page('381891696','Templates & Assets'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});
 const rdoc=new JSDOM(resOut).window.document;assert.equal(rdoc.querySelector('.page-band h1').textContent.trim(),'Latest files');
 const feedPages=JSON.parse(rdoc.querySelector('[data-file-feed]').dataset.pages);assert.deepEqual(feedPages['t:poster templates'],['documents','Poster templates'],'files are placed by their Confluence page title');
 assert(feedPages['t:partner templates']&&!Object.keys(feedPages).some(k=>k.startsWith('i:99')),'planned pages are found by title, never by a stand-in ID');
 assert(rdoc.querySelector('.page-band h1'));assert.deepEqual([...rdoc.querySelectorAll('.footer-base nav a')].map(a=>a.textContent.replace(/\s*↗$/,'')),['Latest files','Get help','Give feedback','Canto library'],'footer: latest files, get help, feedback, Canto');assert(rdoc.querySelector('.brandbar a.beta-pill .beta-tag').textContent==='Beta','Beta · Share feedback in the masthead');assert.equal(rdoc.querySelectorAll('.footer-cta-actions a').length,1,'one call to action');assert(rdoc.querySelector('.footer-cta a.button').getAttribute('href').includes('servicedesk'),'it opens the helpdesk');assert(rdoc.querySelector('.footer-brand img').getAttribute('src').startsWith('/theme/'));assert(rdoc.querySelector('#announcement[hidden]'),'banner stays hidden until an announcement loads');assert(rdoc.querySelector('.page-grid.full-width'));assert(!rdoc.querySelector('.sidebar'));
 pass('Production Latest files, title band and footer render with resolved Confluence links');
 const md=new JSDOM(fs.readFileSync(path.join(root,'docs/standard-template.html'),'utf8')).window.document;
 assert(!md.querySelector('.asset-panel .status-pill'),'no status marker');assert(md.querySelector('.asset-panel .how-to-get'));assert(!md.querySelector('.asset-panel .asset-actions .button'),'no request button on the card');assert(md.querySelectorAll('.asset-panel .release-fact[hidden]').length,3);assert(!md.querySelector('.availability-note'));assert(md.querySelector('.section-nav a[href="presentations.html"]'));
 assert.equal(md.querySelectorAll('.section-next .related-card').length,3);assert(!md.querySelector('.related-next'),'More-in cards carry no Next label');assert(md.querySelector('.page-head a.eyebrow-link[href="presentations.html"]')&&!md.querySelector('.breadcrumbs'),'the section label links back; no breadcrumb');
 pass('Resource pages show a status panel, section navigation, a linked section label and next pages');

 const pv=dom(),pvq=s=>pv.window.document.querySelector(s);assert.equal(pv.window.document.querySelectorAll('#latestAssets .strip-item').length,3);
 assert(pv.window.document.querySelectorAll('#latestAssets .strip-item[aria-disabled="true"]').length===3);assert(!pvq('#latestAssets a[href]'),'preview examples must not link to files');pv.window.close();
 const lv=dom('index.html','confluence');await wait();
 const calls=[];const att=(title,extra={})=>({title,version:{when:'2026-09-20T10:00:00Z'},extensions:{fileSize:2048},_links:{download:'/download/'+title},container:{title:'<b>Letterheads</b>',_links:{webui:'/letterheads'}},...extra});
 lv.window.fetch=async u=>{const cql=new URL(u,'http://localhost').searchParams.get('cql');calls.push(cql);return {ok:true,json:async()=>({results:cql.includes('label=')?[]:[att('image-2026.png'),att('Letterhead.dotx'),att('javascript-trick.pdf',{_links:{download:'https://evil.example/x.pdf'}})]})}};
 const box=lv.window.document.querySelector('#latestAssets');await lv.window.eval('0');
 lv.window.document.body.dataset.mode='confluence';
 // Re-run the loader against the mocked API.
 lv.window.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 assert(calls.some(c=>c.includes('label="approved"')));assert(calls.some(c=>!c.includes('label=')));
 const items=[...box.querySelectorAll('.strip-item')];assert.equal(items.length,1,'one row per page');assert.equal(items[0].querySelector('strong').textContent,'<b>Letterheads</b>','page titles render as text');
 assert(items[0].querySelector('.strip-meta').textContent.startsWith('2 new files'));assert(items[0].title.includes('Letterhead.dotx')&&!items[0].title.includes('image'),'page images are not listed');
 assert(items[0].getAttribute('href').endsWith('/letterheads#downloads'),'opens the page downloads, not the file');
 assert.equal(lv.window.document.querySelector('#latestHeading').textContent,'Latest files in the Hub');assert(!box.querySelector('a[href^="https://evil"]'));assert(!box.querySelector('b'));
 pass('Latest assets prefer the approval label, fall back honestly to deliverable files and render safely');lv.window.close();
 const nd=dom('fonts.html'),nw=nd.window,nq=s=>nw.document.querySelector(s);
 const top=[...nw.document.querySelectorAll('#mainNav > a')];assert.equal(top.length,6);assert.equal(nw.document.querySelectorAll('#mainNav a').length,6,'menu has no nested panels');
 assert.equal(nq('#mainNav a[aria-current]').getAttribute('href'),'brand.html');
 const twoClicks=new Set([...top,...nw.document.querySelectorAll('.footer a')].map(a=>a.getAttribute('href')));
 for(const a of top){const land=new JSDOM(fs.readFileSync(path.join(root,'docs',a.getAttribute('href')),'utf8')).window.document;
  assert(land.querySelector('.page-grid.full-width'),'landing is full width');assert(!land.querySelector('.sidebar'),'landing has no repeated list');
  land.querySelectorAll('.dir-row').forEach(c=>twoClicks.add(c.getAttribute('href')));}
 for(const f of Object.keys(routes).filter(f=>!['canto-guide.html','email-signatures.html','widescreen-template.html','science-slides.html','construction-slides.html','specialised-slides.html','reports.html','hero-images.html','telescope-images.html','event-photos.html','b-roll.html','recordings.html','animations.html','event-safety.html','merchandise.html','event-checklist.html','resources.html','request.html','creative-services.html','timing.html','video-request.html','print.html','business-cards.html','help.html','updates.html','archive.html','working-with-us.html','contribute.html',
  // The site pages sit one click under Construction overview, whose tiles lead to them.
  'low-slides.html','mid-slides.html'].includes(f)))assert(twoClicks.has(f),'two clicks reach '+f);
 const navGroups=[...nw.document.querySelectorAll('.section-nav .nav-group')];assert.equal(navGroups.map(g=>g.querySelector('h3').textContent).join('|'),'Artwork and files|Using the brand|Partner brands');
 assert(!nw.document.querySelector('.section-nav details,.section-nav summary'),'section menus hide nothing behind toggles');assert.equal(nq('.section-nav a.section-home').textContent,'Overview');assert.equal(nq('.section-nav > h2').textContent,'Brand');assert.equal(nq('.section-nav a[aria-current]').getAttribute('href'),'fonts.html');nd.window.close();
 const fq=dom('faq.html'),fqq=s=>fq.window.document.querySelector(s),qs=[...fq.window.document.querySelectorAll('.content-body > .help-answers > details.guidance-detail')];
 assert.equal(fqq('.expand-all').textContent,'Expand all');fqq('.expand-all').click();assert(qs.every(d=>d.open));assert.equal(fqq('.expand-all').textContent,'Collapse all');fq.window.close();
 const fontsOut=new JSDOM(Velocity.render(tpl,{page:page('381891882','Font Downloads'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}})).window.document;
 assert(fontsOut.querySelector('.page-head .eyebrow-link').textContent.includes('Brand'));assert.equal(fontsOut.querySelectorAll('.section-nav .nav-group').length,3);
 pass('Six section links and the footer reach every page within two clicks; landings are full width, detail pages share the section groups in sidebar and section label');
 const an=dom(),aw=an.window,aq=s=>aw.document.querySelector(s);
 assert(!aq('#announcement').hidden);assert(aq('#announcementLink').textContent.startsWith('Example announcement'));
 aq('.announce-close').click();assert(aq('#announcement').hidden);assert.equal(aw.localStorage.getItem('crh-announce-dismissed'),'example:1');an.window.close();
 const lp=dom('index.html','confluence');const lpw=lp.window;let annCql;
 lpw.fetch=async u=>{const cql=new URL(u,'http://localhost').searchParams.get('cql');if(cql.includes('announcement')){annCql=cql;return {ok:true,json:async()=>({results:[{id:'42',title:'<b>Brand Book 2026</b> is out',version:{number:3},_links:{webui:'/display/CRH/Brand'}}]})}}return {ok:true,json:async()=>({results:[]})}};
 lpw.localStorage.setItem('crh-announce-dismissed','42:2');lpw.document.body.dataset.mode='confluence';
 lpw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 const lq=s=>lpw.document.querySelector(s);assert(annCql.includes('label="announcement"'));assert(!lq('#announcement').hidden,'a newer version of a dismissed announcement shows again');
 assert.equal(lq('#announcementLink').textContent,'<b>Brand Book 2026</b> is out');assert(!lq('#announcementLink b'));assert(lq('#announcementLink').href.endsWith('/display/CRH/Brand'));lp.window.close();
 pass('Announcement banner shows the newest labelled page as text, dismisses per version and stays hidden without one');
 const es=dom('index.html','confluence'),ew=es.window;ew.fetch=async()=>({ok:true,json:async()=>({results:[]})});ew.document.body.dataset.mode='confluence';
 ew.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 assert(ew.document.querySelector('#latestStrip').hidden,'no empty Just added strip');es.window.close();pass('Just added strip stays hidden when there are no new files');
 const read=f=>new JSDOM(fs.readFileSync(path.join(root,'docs',f),'utf8')).window.document;
 const st=read('standard-template.html');assert.deepEqual([...st.querySelectorAll('.variant-list li')].map(l=>l.textContent),['Unrestricted','Staff Resources','SKAO Staff Only','For Project Use','Confidential','Strictly Confidential']);
 assert.deepEqual([...read('poster-templates.html').querySelectorAll('.variant-list li')].map(l=>l.textContent),['A0','A1','A2']);
 const decks=read('master-deck.html');assert.equal(decks.querySelector('.page-head h1').textContent,'Approved slide decks');assert(!decks.querySelector('.asset-panel'),'a library, not a resource card');
 assert(decks.querySelector('.deck-library #deckFilter')&&decks.querySelector('.deck-library #deckSort')&&decks.querySelector('[data-deck-list]'),'search, sort and the list');assert(decks.querySelector('.deck-reuse a[href="formatting-slides.html"]'),'reuse advice links to the formatting guide');
 assert.equal(read('memos.html').querySelector('.page-head h1').textContent,'Memo and report templates');assert(read('stands.html').body.textContent.includes('Existing designs to reuse'));
 assert(read('standard-template.html').querySelector('[data-fact="google slides"] .pending-link'),'the review build shows what still needs a link');
 const low=read('low-slides.html');assert(!low.querySelector('.live-link, .progress-links, details.guidance-detail'),'no status box, link row or folded team notes on the site pages');
 assert.deepEqual([...low.querySelectorAll('.live-status .link-card [data-link]')].map(e=>e.dataset.link),['LOW_STATUS','CONSTRUCTION_DASHBOARD'],'live status: the site status slides and the dashboard');
 assert(low.querySelector('.progress-files + .live-status + .site-photos [data-link="ALLHANDS"]'),'earlier slides follow the panel, then live status, then the all-hands photos in their own band');
 assert(low.querySelector('.site-hero [data-site-photo]')&&low.querySelector('.progress-files[data-site-files][hidden]'),'the latest deck leads in the telescope panel; earlier decks wait until there are some');
 assert(!low.querySelector('.team-note, [data-add-note]'),'no notes for the site team on the page');
 assert.equal(low.querySelector('.page-head .eyebrow-link').getAttribute('href'),'site-progress.html','the site pages sit under Construction overview');
 const sp=read('site-progress.html');assert.equal(sp.querySelector('.page-head h1').textContent,'Construction overview');
 assert.deepEqual([...sp.querySelectorAll('a.scope-tile')].map(a=>[a.getAttribute('href'),a.querySelector('strong').textContent]),[['low-slides.html','SKA-Low'],['mid-slides.html','SKA-Mid']],'a tile for each telescope');
 assert.deepEqual([...sp.querySelectorAll('.live-status [data-link]')].map(e=>e.dataset.link),['CONSTRUCTION_DASHBOARD','CONSTRUCTION_STATUS']);assert(sp.querySelector('.live-status + .site-photos'),'the all-hands photos have their own band');
 const pres=read('presentations.html');assert(pres.querySelector('.dir-row[href="site-progress.html"]')&&!pres.querySelector('.dir-row[href="low-slides.html"]'),'the section list shows the overview, which leads to the sites');
 assert.deepEqual([...low.querySelectorAll('.nav-children a')].map(a=>a.textContent),['SKA-Low','SKA-Mid'],'the side menu nests the sites under it');
 assert.equal(read('index.html').querySelector('.quick-links a[href="site-progress.html"]').textContent,'Site progress');
 const nt=dom('fonts.html'),ntd=nt.window.document;ntd.addEventListener('click',e=>e.preventDefault());
 const gf=ntd.querySelector('a[href^="https://fonts.google.com"]');assert.equal(gf.target,'_blank','another site opens in a new tab');assert(gf.rel.includes('noopener'));assert.equal(gf.getAttribute('aria-describedby'),'newTabHint');
 assert(![...ntd.querySelectorAll('a[href$=".html"], a[href^="#"]')].some(a=>a.target),'Hub pages open in place');
 const later=(href,dl)=>{const a=ntd.createElement('a');a.href=href;if(dl)a.setAttribute('download','');ntd.body.append(a);a.click();return a.target;};
 assert.equal(later('https://example.org/x'),'_blank','links added later are caught when used');assert.equal(later('/display/SIG/Artificial+Intelligence'),'_blank','another Confluence space');
 assert.equal(later('/display/CRH/Brand'),'','the Hub space opens in place');assert.equal(later('https://example.org/f.pdf',true),'','downloads stay put');nt.window.close();
 pass('Links that leave the Hub open in a new tab; Hub pages and downloads open in place');
 const committed=[path.join(root,'page.vm'),...fs.readdirSync(path.join(root,'docs')).filter(f=>/\.(html|json)$/.test(f)).map(f=>path.join(root,'docs',f))];
 assert.deepEqual(committed.filter(f=>fs.readFileSync(f,'utf8').includes('docs.google.com')),[],'internal document links stay out of the public repo');
 const prodVm=fs.readFileSync(path.join(root,'page.vm'),'utf8');assert(!prodVm.includes('pending-link')&&!prodVm.includes('link to follow')&&!prodVm.includes('data-fact="google slides"'),'production leaves out content still waiting for a link');assert(!prodVm.includes('Weekly all-hands photos'),'site photo links stay out until the albums exist');
 const ct=read('colours-and-type.html');assert.equal(ct.querySelectorAll('.accent-palettes .swatch').length,30);assert(ct.querySelector('[data-copy="2745 C"]')&&ct.querySelector('[data-copy="3, 100, 35, 0"]'));
 assert(read('logo-guidance.html').body.textContent.includes('20 mm'));
 for(const f of fs.readdirSync(path.join(root,'docs')).filter(f=>f.endsWith('.html')))assert(!fs.readFileSync(path.join(root,'docs',f),'utf8').includes('Brand Book v2'),f);
 pass('Resource and brand pages carry the confirmed brand-bank details (versions, sizes, colour values, logo rules)');
 const sid=routes['standard-template.html'].id;
 const approved=[{title:'SKAO_PPT_Unrestricted.pptx',container:{id:sid},version:{number:3,when:'2026-03-12T10:00:00Z'},extensions:{fileSize:3145728},_links:{download:'/download/attachments/'+sid+'/SKAO_PPT_Unrestricted.pptx'}},{title:'evil.pptx',container:{id:sid},_links:{download:'//evil.example/x'}}];
 const runLive=async(file)=>{const d=dom(file,'confluence'),w=d.window;w.fetch=async u=>({ok:true,json:async()=>({results:new URL(u,'http://localhost').searchParams.get('cql').includes('type=attachment')?approved:[]})});w.document.body.dataset.mode='confluence';w.document.body.dataset.pageId=routes[file]?.id||sid;
  w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();return d;};
 const lpres=await runLive("presentations.html"),pq=s=>lpres.window.document.querySelector(s);
 assert(!pq('.dir-meta.ready,.dir-meta.req'),'landing rows carry no status dots');lpres.window.close();
 const lst=await runLive('standard-template.html'),tq=s=>lst.window.document.querySelector(s);
 const links=[...lst.window.document.querySelectorAll('.downloads a.dl-file')];assert.equal(links.length,1,'off-site download links are dropped');assert(links[0].href.startsWith('http://localhost/download/'));
 assert(!tq('.asset-panel .status-pill'));assert(!tq('.how-to-get'));assert(!tq('[data-fact=versions]'),'version chips give way to the real files');assert(tq('.asset-panel + .dl-layout > .downloads'),'downloads sit under the panel');
 assert.equal(tq('.dl-layout > .dl-aside h2').textContent,'Before you use the file');assert(!tq('.content-body > .reading-section h2')||[...lst.window.document.querySelectorAll('.content-body > .reading-section h2')].every(h=>h.textContent!=='Before you use the file'),'the checks move beside the downloads');
 const fact=k=>{const el=tq(`[data-fact="${k}"]`);return el.hidden?'':el.querySelector('dd').textContent;};
 assert.deepEqual(['version','updated','approved'].map(fact),['Version 3','12 March 2026','Communications'],'release details come from the approved files');lst.window.close();
 pass('Approved attachments become downloads and clear on-request markers; only same-site links are shown');
 const mk=(t,kb)=>({title:t,container:{id:sid},extensions:{fileSize:kb*1024},_links:{download:'/download/attachments/'+sid+'/'+encodeURIComponent(t)}});
 approved.splice(0,approved.length,...['SKAO_Letterhead_STRICTLY CONFIDENTIAL.docx','SKAO_Letterhead_UNRESTRICTED.docx','SKAO_Letterhead_CONFIDENTIAL.docx','skao_wordletterhead_Bradford Office.docx','skao_wordletterhead_Landscape.docx','SKAO A0 poster template.pdf','SKAO A0 poster template.ai','SKAO_RCN_KeynoteTemplate.key','SKAO_RCN_PowerPointTemplate.pptx','SKAO_ukSRC_logofiles.zip'].map(t=>mk(t,120)));
 const gd=await runLive('standard-template.html'),gq=gd.window.document,groupsOf=()=>Object.fromEntries([...gq.querySelectorAll('.dl-group')].map(g=>[g.querySelector('h3')?.textContent,[...g.querySelectorAll('.dl-row')].map(r=>r.querySelector('.dl-label').textContent+':'+[...r.querySelectorAll('.dl-file b')].map(b=>b.textContent).join('/'))]));
 const gs=groupsOf();
 assert.deepEqual(gs['By information classification'],['Unrestricted:DOCX','Confidential:DOCX','Strictly Confidential:DOCX'],'classification in order, canonical labels');
 assert.deepEqual(gs['By office and layout'],['Bradford Office:DOCX','Landscape:DOCX']);
 assert(gs['Files'].some(r=>r.endsWith(':PDF/AI')),'one row per version with a button per format');
 assert(gs['Partner versions'].includes('RCN Template:PPTX/KEY')&&gs['Partner versions'].some(r=>r.startsWith('SKAO ukSRC')||r.startsWith('ukSRC')),JSON.stringify(gs['Partner versions']));
 assert(gq.querySelector('.dl-file').getAttribute('aria-label').startsWith('Download '));gd.window.close();
 const runGroups=async(file,titles)=>{approved.splice(0,approved.length,...titles.map(t=>({...mk(t,120),container:{id:routes[file].id}})));const d=await runLive(file),q=d.window.document;
  const out=Object.fromEntries([...q.querySelectorAll('.dl-group')].map(g=>[g.querySelector('h3')?.textContent,[...g.querySelectorAll('.dl-row')].map(r=>r.querySelector('.dl-label').textContent)]));
  const notes=[...q.querySelectorAll('.dl-note')].map(n=>n.textContent);d.window.close();return {out,notes};};
 const lh=await runGroups('letterheads.html',['SKAO_Letterhead_UNRESTRICTED.docx','skao_wordletterhead_Bradford Office_V2.docx','skao_wordletterhead_Chapman Office_V2.docx','skao_wordletterhead_Kensington Office_SKAO:CSIRO.docx','skao_wordletterhead_Landscape_V2.docx']);
 assert.deepEqual(Object.keys(lh.out),['By information classification','United Kingdom','Australia'],'letterheads by classification, then by site');
 assert.deepEqual(lh.out['Australia'],['Bradford Office, Geraldton','Chapman Office, Geraldton','Kensington Office, Perth (with CSIRO)']);assert.deepEqual(lh.out['United Kingdom'],['Landscape layout']);assert(lh.notes.includes('Geraldton and Perth offices'));
 const cs=await runGroups('co-branding-csiro.html',['SKAO_CSIRO_Co-brand_Guidelines.pdf']);assert.deepEqual(cs.out,{undefined:['SKAO and CSIRO co-branding guidelines']},'the CSIRO page keeps the guidelines; the office letterheads are on Letterheads');
 const vp=read('video.html');assert(!vp.querySelector('[data-dl-groups]'),'no video downloads');assert(!/Brand video kit|Need new video/.test(vp.body.textContent),'no brand video kit or new-video box');
 assert(vp.querySelector('.content-body > .task-intro + .media-handoff + .canto-show'),'the slideshow comes straight after the intro, once Canto replaces the search box');
 const runCards=async(file,titles,pics=[])=>{const id=routes[file].id;approved.splice(0,approved.length,...titles.map(t=>({...mk(t,120),container:{id},_links:{download:`/download/attachments/${id}/${encodeURIComponent(t)}`}})));
  const d=dom(file,'confluence'),w=d.window;w.fetch=async u=>{const s=String(u);if(s.includes('/child/attachment'))return {ok:true,json:async()=>({results:pics.map(t=>({title:t,_links:{download:`/download/attachments/${id}/${encodeURIComponent(t)}`}}))})};
   return {ok:true,json:async()=>({results:new URL(s,'http://localhost').searchParams.get('cql')?.includes('type=attachment')?approved:[]})};};
  w.document.body.dataset.mode='confluence';w.document.body.dataset.pageId=id;w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();await wait();
  const q=w.document,cards=[...q.querySelectorAll('.file-card')].map(c=>({title:c.querySelector('.file-card-title').textContent,month:c.querySelector('.file-card-kicker')?.textContent||'',files:[...c.querySelectorAll('.dl-file b')].map(b=>b.textContent).join('/'),cover:(c.querySelector('.file-cover img')?.getAttribute('src')||'').split('/').pop()}));
  const tiles=[...q.querySelectorAll('.logo-tile')].map(t=>[t.querySelector('strong').textContent,t.querySelector('.logo-tile-body > small')?.textContent||'',[...t.querySelectorAll('.dl-file b')].map(b=>b.textContent).join('/'),t.dataset.tone||'',!!t.querySelector('.logo-preview img')].join('|'));
  const heads=[...q.querySelectorAll('.dl-group h3')].map(h=>h.textContent);d.window.close();return {cards,tiles,heads};};
 const pt=await runCards('partner-templates.html',['SKAO - SARAO Presentation template v2.pptx','SKAO_RCN_KeynoteTemplate.key','SKAO_RCN_PowerPointTemplate.pptx'],['SKAO - SARAO Presentation template v2.jpg','unrelated.jpg']);
 assert.deepEqual(pt.cards,[{title:'SKAO and SARAO',month:'',files:'PowerPoint',cover:'SKAO%20-%20SARAO%20Presentation%20template%20v2.jpg'},{title:'SRCNet',month:'',files:'PowerPoint/Keynote',cover:''}],'partner templates as cards: plain names, a cover under the file\'s own name, one button per format');assert.deepEqual(pt.heads,[],'one group, no heading');
 const pl=await runCards('partner-logos.html',['SKAO_SRCnet_logo_colour_rgb.png','SKAO_SRCnet_logo_colour_rgb.ai','SKAO_SRCnet_avatar_monowhite_rgb.eps','SKAO_ukSRC_logofiles.zip','SKAO_zaSRC_logofiles.zip']);
 assert.deepEqual(pl.heads,['SRCNet logo','SRCNet avatar','Regional centres']);
 assert.deepEqual(pl.tiles,['Full colour||AI/PNG||true','White||EPS|dark|false','ukSRC|United Kingdom|ZIP||false','zaSRC|South Africa|ZIP||false'],'logo tiles: a preview from the PNG, white versions on navy, regional packs by centre and country');
 pass('Downloads group by classification, office and partner and merge formats; templates show as cards with covers, partner logos as tiles; no video downloads');
 {const id=routes['master-deck.html'].id,dl=(t)=>`/download/attachments/${id}/${encodeURIComponent(t)}`,lab=(...n)=>({labels:{results:n.map(name=>({name}))}});
  const files=[
   {id:'att11',title:'2025-11 A journey through time, de Laeter Colloquium.pptx',version:{number:1,when:'2025-11-20T09:00:00Z',by:{displayName:'Communications'}},extensions:{fileSize:3*1073741824,comment:'Speaker: Director-General · Event: de Laeter Colloquium, Perth · Slides: 52'},metadata:lab('approved'),_links:{download:dl('a.pptx')}},
   {id:'att12',title:'2024-08 SKA-Mid construction, IAU General Assembly.pptx',version:{number:2,when:'2024-09-01T09:00:00Z'},extensions:{fileSize:300*1048576,comment:'Event: IAU General Assembly, Cape Town\nAudience: Media\nClassification: Unrestricted'},metadata:lab('approved'),_links:{download:dl('b.pptx')}},
   {id:'att13',title:'2024-08 SKA-Mid construction, IAU General Assembly.jpg',metadata:lab(),_links:{download:dl('b.jpg')}},
   {id:'att14',title:'Draft deck.pptx',metadata:lab(),_links:{download:dl('c.pptx')}},
   {id:'att15',title:'<img src=x onerror=alert(1)>.pptx',metadata:lab('approved'),_links:{download:'//evil.example/x'}}];
  const d=dom('master-deck.html','confluence'),w=d.window,doc=w.document,q=s=>doc.querySelector(s);let asked='';
  w.fetch=async u=>{const s=String(u);if(s.includes('/child/attachment')){asked=s;return {ok:true,json:async()=>({results:files})};}return {ok:true,json:async()=>({results:[]})};};
  doc.body.dataset.mode='confluence';doc.body.dataset.pageId=id;w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();await wait();
  assert(asked.includes('metadata.labels'),'labels come with the files');
  const rowsNow=()=>[...doc.querySelectorAll('.deck:not([hidden])')].map(r=>r.querySelector('.deck-title').textContent);
  assert.deepEqual(rowsNow(),['A journey through time, de Laeter Colloquium','SKA-Mid construction, IAU General Assembly'],'approved decks only, newest first; drafts, pictures and off-site links left out');
  const first=q('.deck'),facts=Object.fromEntries([...first.querySelectorAll('.deck-facts div')].map(x=>[x.querySelector('dt').textContent,x.querySelector('dd').textContent]));
  assert.deepEqual(facts,{Speaker:'Director-General',Slides:'52',Added:'20 Nov 2025 by Communications'},'details from the attachment comment, and who added it');
  assert.equal(first.querySelector('.deck-event').textContent,'de Laeter Colloquium, Perth');assert.equal(first.querySelector('.deck-kicker').textContent,'About the SKAONovember 2025');
  assert(first.querySelector('.deck-download small').textContent.includes('PowerPoint · 3.0 GB'),'the size before you download');
  assert.equal(first.querySelector('a.deck-cover').getAttribute('href'),`/master-deck.html?preview=/${id}/11/`+encodeURIComponent(files[0].title),'the cover opens Confluence\'s preview');
  const second=[...doc.querySelectorAll('.deck')][1];assert(second.querySelector('.deck-cover img').getAttribute('src').endsWith('/b.jpg'),'a picture under the deck\'s own name is its cover');
  assert.equal(second.querySelector('.is-class dd').textContent,'Unrestricted');assert(second.querySelector('.deck-facts').textContent.includes('Updated'),'a new version says Updated');
  assert.deepEqual([...doc.querySelectorAll('.type-chips button')].map(b=>b.textContent),['All 2','About the SKAO 1','Construction progress 1']);
  q('.type-chips [data-topic-filter="Construction progress"]').click();assert.deepEqual(rowsNow(),['SKA-Mid construction, IAU General Assembly']);
  q('#clearDecks').click();q('#deckSort').value='az';q('#deckSort').dispatchEvent(new w.Event('change'));assert.equal(rowsNow()[0],'A journey through time, de Laeter Colloquium');
  q('#deckFilter').value='media';q('#deckFilter').dispatchEvent(new w.Event('input'));assert.deepEqual(rowsNow(),['SKA-Mid construction, IAU General Assembly'],'search reads the details too');
  assert(!q('.deck-list-cards img[onerror]'),'titles render as text');d.window.close();
  const pv=dom('master-deck.html');assert.equal(pv.window.document.querySelectorAll('.deck').length,2,'the preview shows two examples');pv.window.close();
  pass('Approved slide decks is a library: approved decks newest first, each with cover, preview, details from its comment and size, with topics, search and sort');}
 {const d=dom('fonts.html','confluence'),w=d.window,doc=w.document,dlg=doc.querySelector('#welcomeDialog');
  assert(dlg&&dlg.querySelector('a.button[href*="servicedesk"]'),'Share feedback opens the helpdesk until the form exists');
  await new Promise(r=>setTimeout(r,800));assert(dlg.open,'the welcome opens on a first visit');
  dlg.querySelector('[data-welcome-close]').click();assert(!dlg.open);assert.equal(w.localStorage.getItem('crh-welcome-1'),'1','and once only');
  const again=new JSDOM(fs.readFileSync(path.join(root,'docs/fonts.html'),'utf8'),{url:'http://localhost/fonts.html',runScripts:'outside-only',beforeParse(win){win.localStorage.setItem('crh-welcome-1','1');}}),aw=again.window;
  aw.matchMedia=()=>({matches:false});aw.HTMLDialogElement.prototype.showModal=function(){this.open=true};aw.document.body.dataset.mode='confluence';aw.fetch=async()=>({ok:true,json:async()=>({results:[]})});aw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await new Promise(r=>setTimeout(r,800));
  assert(![...aw.document.querySelectorAll('#welcomeDialog')].some(x=>x.open),'not again once seen');again.window.close();d.window.close();
  const pre=dom('fonts.html');await new Promise(r=>setTimeout(r,800));assert(!pre.window.document.querySelector('#welcomeDialog').open,'never in the design preview');pre.window.close();
  pass('A first-visit welcome says the Hub is new and in development, links to feedback and shows once');}
 {const page=fs.readFileSync(path.join(root,'docs/fonts.html'),'utf8'),form='https://airtable.com/appTest/shrTest';
  const f=new JSDOM(page.replace(/<a href="[^"]*"(?=[^>]*data-feedback)/g,`<a href="${form}"`),{url:'http://localhost/fonts.html',runScripts:'outside-only',beforeParse(win){win.localStorage.setItem('crh-welcome-1','1');}}),fw=f.window;
  fw.matchMedia=()=>({matches:false});fw.HTMLDialogElement.prototype.showModal=function(){this.open=true};fw.document.body.dataset.mode='confluence';fw.fetch=async()=>({ok:true,json:async()=>({results:[]})});fw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));
  const ls=[...fw.document.querySelectorAll('a[data-feedback]')],title=fw.document.querySelector('.page-head h1').textContent.trim();
  assert.equal(ls.length,3,'header, welcome and footer');assert(title);
  ls.forEach(l=>{const u=new URL(l.href);assert.equal(u.origin+u.pathname,form);assert.equal(u.searchParams.get('prefill_Page'),title,'the form opens with the page filled in');});f.window.close();
  const h=dom('fonts.html','confluence');[...h.window.document.querySelectorAll('a[data-feedback]')].forEach(l=>{assert(l.href.includes('servicedesk'));assert(!l.href.includes('prefill'),'the helpdesk fallback stays as it is');});h.window.close();
  pass('Share feedback opens the feedback form with the page it came from filled in; until the form is set, the helpdesk');}
 const lowId=routes['low-slides.html'].id,midId=routes['mid-slides.html'].id,deck=(id,t,m)=>({title:t,version:{when:m},extensions:{fileSize:3145728},_links:{download:`/download/attachments/${id}/${encodeURIComponent(t)}`}});
 const lowFiles=[deck(lowId,'2026-09 SKA-Low progress.pptx','2026-09-15T10:00:00Z'),deck(lowId,'2026-10 SKA-Low progress.pptx','2026-10-15T10:00:00Z'),deck(lowId,'site-photo.jpg','2026-10-16T10:00:00Z')];
 const files=u=>{const s=String(u);return s.includes(`/content/${lowId}/child/attachment`)?lowFiles:[];};
 const spg=dom('site-progress.html','confluence'),spw=spg.window;spw.fetch=async u=>({ok:true,json:async()=>({results:files(u)})});
 spw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 const tiles=[...spw.document.querySelectorAll('a.scope-tile')];
 assert.equal(tiles[0].querySelector('[data-latest-line]').textContent,'Latest slides: October 2026','the SKA-Low tile names the month of the newest slides');
 assert(tiles[0].querySelector('.scope-photo img').getAttribute('src').endsWith('/site-photo.jpg'),'and shows the telescope photo from the site page');
 assert.equal(tiles[1].querySelector('[data-latest-line]').textContent,'Progress slides','a site with no slides yet keeps the plain label');spg.window.close();
 const lw=dom('low-slides.html','confluence'),lww=lw.window;lww.document.body.dataset.pageId=lowId;lww.fetch=async u=>({ok:true,json:async()=>({results:files(u)})});
 lww.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 const progQ=s=>lww.document.querySelector(s);
 assert.equal(progQ('[data-hero-title]').textContent,'October 2026','the panel names the month of the newest deck');assert.equal(progQ('.site-hero-file').textContent,'SKA-Low progress');
 assert(progQ('[data-hero-actions] a.button[download]').getAttribute('href').includes('2026-10'),'with its download');
 assert.deepEqual([...lww.document.querySelectorAll('.deck-row strong')].map(e=>e.textContent),['SKA-Low progress'],'earlier decks follow, and the photo is not listed as a file');assert(!progQ('.progress-files').hidden);
 assert.deepEqual([...progQ('.deck-row .deck-date').children].map(e=>e.textContent),['Sep','2026'],'each earlier deck has a month tile');assert.equal(progQ('[data-file-count]').textContent,'1 deck');assert(progQ('.deck-row a.deck-get[download]').getAttribute('aria-label').startsWith('Download SKA-Low progress, September 2026'));
 assert(progQ('[data-site-photo] img'),'the telescope photo loads into the panel');lw.window.close();
 pass('Construction overview tiles show each telescope and the month of its newest slides; site pages lead with the latest deck, then a dated list of earlier ones');
 // Events: lead times and request steps on the landing; the kit on Stands and merchandise.
 const ev=read('events.html');
 assert.equal(ev.querySelectorAll('.landing-main .lead-table tbody tr').length,6,'lead times sit in the main column');
 assert.equal(ev.querySelectorAll('.landing-main .request-flow .guide-steps li').length,5,'then how a request runs');
 assert(!ev.querySelector('.landing-rail .lead-table, .landing-rail .guide-steps'),'neither moves into the rail');assert.equal(ev.querySelectorAll('.landing-rail details.rail-item').length,3,'the rail keeps its three items');
 assert(!ev.querySelector('a.dir-row[href="event-checklist.html"]')&&!ev.querySelector('.check-list'),'no tick-list checklist');
 const standsId=routes['stands.html'].id,sk=dom('stands.html','confluence'),skw=sk.window;skw.document.body.dataset.pageId=standsId;
 skw.fetch=async u=>{if(String(u).includes('/child/attachment'))return {ok:true,json:async()=>({results:[
  {title:'kit-fabrilux-3m.webp',_links:{download:`/download/attachments/${standsId}/kit-fabrilux-3m.webp`}},
  {title:'KIT-KIOSK.PNG',_links:{download:`/download/attachments/${standsId}/KIT-KIOSK.PNG`}},
  {title:'kit-pull-up-banners.webp',_links:{download:'//evil.example/x.webp'}},
  {title:'kit-table-cloths.pdf',_links:{download:`/download/attachments/${standsId}/kit-table-cloths.pdf`}}]})};return {ok:true,json:async()=>({results:[]})};};
 skw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 const pics=Object.fromEntries([...skw.document.querySelectorAll('[data-kit-image]')].map(p=>[p.dataset.kitImage,p.querySelector('img')?.getAttribute('src')||'']));
 assert.deepEqual(Object.keys(pics),['kit-fabrilux-3m','kit-fabrilux-2m','kit-pull-up-banners','kit-kiosk','kit-table-cloths']);
 assert(pics['kit-fabrilux-3m'].endsWith('/kit-fabrilux-3m.webp')&&pics['kit-kiosk'].endsWith('/KIT-KIOSK.PNG'),'pictures are matched by file name');
 assert.equal(pics['kit-pull-up-banners'],'','off-site links are dropped');assert.equal(pics['kit-table-cloths'],'','only image files count');assert.equal(pics['kit-fabrilux-2m'],'','a missing picture keeps the outline');sk.window.close();
 const skp=dom('stands.html');assert(!skp.window.document.querySelector('.kit-pic img'),'the preview shows outlines');skp.window.close();
 pass('Events: lead times and request steps under the section list; the kit shows pictures attached to Stands and merchandise, or outlines until then');
 const mediaId=routes['media.html'].id;
 const cantoManifest={version:1,albums:[
  {id:'a1',name:'Telescopes',path:'Asset library - Staff / Telescopes',count:40,href:'https://skao.canto.global/album/a1',assets:[
   {title:'SKA-Low at dawn',credit:'SKAO',src:`/download/attachments/${mediaId}/canto-1.jpg`,href:'https://skao.canto.global/asset/1',width:640,height:480},
   {title:'<img src=x onerror=alert(1)>',src:`/download/attachments/${mediaId}/canto-2.jpg`,href:'https://skao.canto.global/asset/2'},
   {title:'Off-site image',src:'https://evil.example/x.jpg',href:'https://skao.canto.global/asset/3'},
   {title:'Off-site link',src:`/download/attachments/${mediaId}/canto-4.jpg`,href:'https://evil.example/asset/4'}]},
  {id:'a2',name:'Future visions',path:'Asset library - Staff / Future visions',count:5,href:'https://skao.canto.global/album/a2',assets:[
   {title:'SKA Africa concept',src:`/download/attachments/${mediaId}/canto-5.jpg`,href:'https://skao.canto.global/asset/5'}]}]};
 const curatedManifest={...cantoManifest,highlights:['h1','h2','h3','h4'].map(i=>({title:'Pick '+i,alt:'Curated '+i+' alt text',src:`/download/attachments/${mediaId}/canto-${i}.jpg`,href:'https://skao.canto.global/smartalbum/image?column=image&id='+i})),href:'https://skao.canto.global/folder/STAFF'};
 const runCanto=async(file,m)=>{const d=dom(file,'confluence'),w=d.window;
  w.fetch=async u=>{const s=String(u);if(s.includes('/rest/api/content/search')){const cql=new URL(s,'http://localhost').searchParams.get('cql');return {ok:true,json:async()=>({results:cql.includes('canto-showcase.json')&&m?[{title:'canto-showcase.json',_links:{download:`/download/attachments/${mediaId}/canto-showcase.json`}}]:[]})};}
   if(s.includes('canto-showcase.json'))return {ok:true,json:async()=>m};return {ok:false,json:async()=>({})};};
  w.document.body.dataset.mode='confluence';w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();await wait();return d;};
 {const d=dom('stands.html'),w=d.window,doc=w.document,g=doc.querySelector('.page-grid');
  assert(!doc.querySelector('.toc-rail').hidden&&g.classList.contains('has-toc')&&doc.querySelectorAll('.toc-rail #toc a').length>=4,'On this page sits in its own column on the right on long pages');
  const short=dom('low-slides.html');assert(short.window.document.querySelector('.toc-rail').hidden,'pages with three sections or fewer go without');short.window.close();
  assert(!doc.querySelector('.sidebar #toc'),'and no longer under the section menu');
  doc.querySelector('[data-rail="nav"]').click();doc.querySelector('[data-rail="toc"]').click();
  assert(g.classList.contains('nav-closed')&&g.classList.contains('toc-closed'),'both side menus fold away');assert.equal(doc.querySelector('[data-rail="nav"]').getAttribute('aria-expanded'),'false');
  assert.equal(w.localStorage.getItem('crh-toc-closed'),'1','the choice is remembered');w.close();
  const few=dom('making-a-poster.html');assert(few.window.document.querySelector('.toc-rail').hidden&&!few.window.document.querySelector('.page-grid').classList.contains('has-toc'),'short pages keep two columns');few.window.close();
  const pg=dom('partner-templates.html').window.document;assert.deepEqual([...pg.querySelectorAll('.page-pager a')].map(x=>x.getAttribute('href')),['standard-template.html','master-deck.html'],'previous and next follow the sidebar order');
  pass('Side menus: On this page on the right, and both fold away for more room');}
 const cMedia=await runCanto('media.html',cantoManifest),kq2=s=>cMedia.window.document.querySelector(s),kqa=s=>[...cMedia.window.document.querySelectorAll(s)];
 assert(!kq2('.canto-show.wide').hidden);assert.equal(kqa('.show-slide').length,3,'off-site images and links are dropped');assert(!kq2('.canto-show a:not(.button)'),'the slideshow is view only');
 assert(kqa('.show-slide img').every(i=>(i.getAttribute('src')||i.dataset.src||'').startsWith('http://localhost/download/attachments/')));assert(kqa('.show-slide img').filter(i=>i.getAttribute('src')).length===2,'large slideshow images load as they come up, not all at once');assert(!kq2('.show-slide img[onerror]')&&!kq2('.show-caption img'));
 assert.equal(kq2('.show-caption small').textContent,'© SKAO');assert(!kq2('.show-collections'),'no list of library collections under the slideshow');
 assert.equal(kqa('.show-slide.is-on').length,1);assert.equal(kqa('.show-slide[aria-hidden="false"]').length,1);
 kq2('.show-next').click();assert.equal(kqa('.show-dots button')[1].getAttribute('aria-current'),'true');assert.equal(kq2('.show-play').getAttribute('aria-pressed'),'true','moving by hand pauses the slideshow');
 kq2('.show-play').click();assert.equal(kq2('.show-play').getAttribute('aria-pressed'),'false');
 assert(kq2('.show-foot a.button[href*="canto.global"]'),'the Canto button sits under the slideshow');assert(!kq2('.content-body > .task-intro a.button'));
 assert(!kq2('.media-handoff'),'slideshow replaces the generic Canto box');cMedia.window.close();
 const videoManifest={...cantoManifest,albums:[...cantoManifest.albums,{id:'a3',name:'Promo videos',path:'Asset library - Staff / Promo videos',count:3,href:'https://skao.canto.global/album/a3',assets:[{title:'Promo cut',src:`/download/attachments/${mediaId}/canto-6.jpg`,href:'https://skao.canto.global/asset/6'}]}]};
 const cVid=await runCanto('video.html',videoManifest),vd=cVid.window.document;assert(!vd.querySelector('.canto-show').hidden);assert.equal(vd.querySelector('.show-foot a.button').href,'https://skao.canto.global/album/a3');
 assert(vd.querySelector('.show-note').textContent.startsWith('Search for the topic'),'the page search tip moves under the slideshow');cVid.window.close();
 const cNoVid=await runCanto('video.html',cantoManifest);assert(cNoVid.window.document.querySelector('.canto-show').hidden,'no matching album, nothing shown');assert(cNoVid.window.document.querySelector('.content-body > .task-intro a.button'),'the button stays with the intro');cNoVid.window.close();
 const cNone=await runCanto('media.html',null);assert(cNone.window.document.querySelector('.canto-show').hidden,'no cantoManifest, nothing shown');cNone.window.close();
 require('child_process').execFileSync('python3',[path.join(root,'scripts/canto_sync.py'),'--self-test'],{stdio:'pipe'});
 const cCur=await runCanto('media.html',curatedManifest),cc=cCur.window.document;
 assert.deepEqual([...cc.querySelectorAll('.show-slide img')].map(i=>i.alt),['Curated h1 alt text','Curated h2 alt text','Curated h3 alt text','Curated h4 alt text'],'the slideshow shows the curated list, with description alt text');
 assert.equal(cc.querySelector('.show-foot a.button').href,'https://skao.canto.global/folder/STAFF','Open the Canto library goes to the staff folder');cCur.window.close();
 pass('Canto slideshow renders synced albums safely and view only, matches topic pages by album, docks the Canto button and stays hidden without data; sync self-test passes');
 const result={status:'PASS',checks};fs.writeFileSync(path.join(root,'evidence/tests.json'),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exitCode=1});
