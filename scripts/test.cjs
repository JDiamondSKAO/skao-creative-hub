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
 for(const [old,to] of [['request.html','faq.html'],['video-request.html','faq.html'],['timing.html','faq.html'],['help.html','faq.html'],['creative-services.html','faq.html'],['canto-guide.html','canto-access.html'],['email-signatures.html','documents.html'],['widescreen-template.html','standard-template.html'],['science-slides.html','master-deck.html'],['reports.html','memos.html'],['hero-images.html','media.html'],['event-safety.html','events.html'],['merchandise.html','stands.html']]){
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
 assert.equal(rw.document.querySelectorAll('.choice-card').length,0,'no duplicate starting-point cards');assert(rq('.page-grid.full-width .catalogue'));assert(!rq('.sidebar'));
 for(const t of ['presentations','documents','brand','media'])assert(rq(`[data-type-filter="${t}"]`),t);rd.window.close();pass('Templates and assets is one full-width catalogue with type filters instead of duplicate cards');
 const pd=new JSDOM(fs.readFileSync(path.join(root,'docs/presentations.html'),'utf8'));
 const pdoc=pd.window.document,destinations=[...pdoc.querySelectorAll('.directory .dir-row')].map(a=>a.getAttribute('href'));
 for(const f of ['standard-template.html','partner-templates.html','master-deck.html','low-slides.html','mid-slides.html','recent-talks.html','formatting-slides.html'])assert(destinations.includes(f),f);
 assert.deepEqual([...pdoc.querySelectorAll('.directory .dir-group h2')].map(h=>h.firstChild.textContent.trim()),['Templates','Decks to reuse','Site progress','Shared by staff','How to']);assert(!pdoc.querySelector('.dir-add'),'no separate share row: Recent talks covers it');
 assert.equal(new Set(destinations).size,destinations.length);assert(!pdoc.querySelector('details .dir-row'),'page links are never collapsed');const railItems=[...pdoc.querySelectorAll('.landing-rail details.rail-item')];assert.equal(railItems.length,3);assert(railItems.every(d=>!d.open),'several pieces of advice start closed, each one click away');assert(pdoc.querySelector('.landing-main > .task-intro'),'the intro sits beside Before you start');assert(!pdoc.querySelector('.landing-rail a.button'),'no on-request box: help lives in the footer');assert(!pdoc.querySelector('.dir-meta.req,.dir-legend'),'no status dots or legend');assert(pdoc.querySelector('.landing-rail .source-check'));assert(pdoc.querySelector('.landing-rail .reuse-decision'));
 pass('Presentations landing shows every presentation page, grouped and visible, with freshness/reuse guidance');
 for(const id of ['381891696','381891810']){const out=Velocity.render(tpl,{page:page(id,'Test'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});const doc=new JSDOM(out).window.document;assert(doc.querySelector(id==='381891696'?'.page-grid.full-width .catalogue':'.content-body .moved-note a.button'));assert(![...doc.querySelectorAll('a')].some(a=>a.getAttribute('href').includes('$link')));}pass('Catalogue and contribution landing pages render in the production template');
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
  assert(doc.querySelector('.task-intro'),file);
  assert(!doc.querySelector('.content-body').textContent.includes('Confluence content'),file);
  assert(![...doc.querySelectorAll('a')].some(a=>(a.getAttribute('href')||'').includes('$link')),file);
  assert(!/ASSET TO ADD|jira\.skao\.int|#003366|#00A4A6/.test(out),file);
 }
 pass('All 62 production routes (60 observed, 2 proposed) render their reviewed content and resolved links');
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
 const cd=dom('resources.html'),cw=cd.window,cq=s=>cw.document.querySelector(s),shown=()=>[...cw.document.querySelectorAll('[data-resource]')].filter(c=>!c.closest('li').hidden).length;
 const cardTitles=[...cw.document.querySelectorAll('.resource-row strong')].map(h=>h.textContent);assert(cardTitles.length>=30&&cardTitles.length<=40,"the catalogue lists the fuller page set");assert.equal(new Set(cardTitles).size,cardTitles.length,'catalogue titles are unique');
 const total=shown();cq('[data-type-filter="brand"]').click();assert(shown()<total&&shown()>0);assert.equal(cq('[data-type-filter="brand"]').getAttribute('aria-pressed'),'true');
 cq('#resourceFilter').value='color';cq('#resourceFilter').dispatchEvent(new cw.Event('input'));assert(shown()>0,'synonyms apply to the catalogue filter');
 cq('#resourceFilter').value='zzzz';cq('#resourceFilter').dispatchEvent(new cw.Event('input'));assert.equal(shown(),0);assert(!cq('#catalogueEmpty').hidden);
 cq('#clearFilters').click();assert.equal(shown(),total);pass('Resource catalogue lists every resource once and filters by type and name');cd.window.close();
 const idx=JSON.parse(fs.readFileSync(path.join(root,'docs/search-index.json'),'utf8'));assert(!idx.find(r=>r.href==='resources.html').keywords.includes('Letterheads'),'catalogue must not flood the search index');
 const hs=dom(),hsw=hs.window,hsq=s=>hsw.document.querySelector(s);hsw.fetch=async()=>({ok:true,json:async()=>idx});
 hsq('#heroSearch').value='l';hsq('#heroSearch').dispatchEvent(new hsw.Event('input'));assert(hsq('dialog').open);assert.equal(hsq('#searchInput').value,'l');assert.equal(hsq('#heroSearch').value,'');
 pass('Homepage search box hands typing over to the search dialog');hs.window.close();
 const resOut=Velocity.render(tpl,{page:page('381891696','Templates & Assets'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});
 const rdoc=new JSDOM(resOut).window.document;const rlinks=[...rdoc.querySelectorAll('.resource-row')].map(a=>a.getAttribute('href'));assert(rlinks.length>=30);assert(rlinks.every(h=>h.startsWith('/crh/')),rlinks.find(h=>!h.startsWith('/crh/')));
 assert(rdoc.querySelector('.page-band h1'));assert.equal(rdoc.querySelectorAll('.footer-base nav a').length,3,'footer: all resources, get help, Canto');assert.equal(rdoc.querySelectorAll('.footer-cta-actions a').length,1,'one call to action');assert(rdoc.querySelector('.footer-cta a.button').getAttribute('href').includes('servicedesk'),'it opens the helpdesk');assert(rdoc.querySelector('.footer-brand img').getAttribute('src').startsWith('/theme/'));assert(rdoc.querySelector('#announcement[hidden]'),'banner stays hidden until an announcement loads');assert(rdoc.querySelector('.page-grid.full-width'));assert(!rdoc.querySelector('.sidebar'));
 pass('Production catalogue, title band and footer render with resolved Confluence links');
 const md=new JSDOM(fs.readFileSync(path.join(root,'docs/master-deck.html'),'utf8')).window.document;
 assert(!md.querySelector('.asset-panel .status-pill'),'no status marker');assert(md.querySelector('.asset-panel .how-to-get'));assert(!md.querySelector('.asset-panel .asset-actions .button'),'no request button on the card');assert(md.querySelectorAll('.asset-panel .release-fact[hidden]').length,3);assert(!md.querySelector('.availability-note'));assert(md.querySelector('.section-nav a[href="presentations.html"]'));
 assert.equal(md.querySelectorAll('.section-next .related-card').length,3);assert(!md.querySelector('.related-next'),'More-in cards carry no Next label');assert(md.querySelector('.page-head a.eyebrow-link[href="presentations.html"]')&&!md.querySelector('.breadcrumbs'),'the section label links back; no breadcrumb');
 pass('Resource pages show a status panel, section navigation, a linked section label and next pages');
 const ck=dom('event-checklist.html'),kw=ck.window,kq=s=>kw.document.querySelector(s),boxes=[...kw.document.querySelectorAll('.check-list input')];
 assert(boxes.length>=6);boxes[0].checked=true;boxes[0].dispatchEvent(new kw.Event('change'));assert(kq('.checklist-progress').textContent.startsWith('1 of'));
 assert(kw.localStorage.getItem('crh-check:event-checklist.html').includes('0'));kq('[data-checklist-reset]').click();assert(kq('.checklist-progress').textContent.startsWith('0 of'));
 pass('Checklists track progress and can be cleared');ck.window.close();

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
 for(const f of Object.keys(routes).filter(f=>!['canto-guide.html','email-signatures.html','widescreen-template.html','science-slides.html','construction-slides.html','specialised-slides.html','reports.html','hero-images.html','telescope-images.html','event-photos.html','b-roll.html','recordings.html','animations.html','event-safety.html','merchandise.html','resources.html','request.html','creative-services.html','timing.html','video-request.html','print.html','business-cards.html','help.html','updates.html','archive.html','working-with-us.html','contribute.html'].includes(f)))assert(twoClicks.has(f),'two clicks reach '+f);
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
 const decks=read('master-deck.html');assert.deepEqual([...decks.querySelectorAll('.asset-actions a')].map(a=>a.getAttribute('href')),['formatting-slides.html','low-slides.html','mid-slides.html','recent-talks.html']);assert(decks.querySelector('[data-fact="planned"]'));
 assert.equal(read('memos.html').querySelector('.page-head h1').textContent,'Memo and report templates');assert(read('stands.html').body.textContent.includes('Existing designs to reuse'));
 assert(read('standard-template.html').querySelector('[data-fact="google slides"] .pending-link'),'the review build shows what still needs a link');
 const low=read('low-slides.html');assert(low.querySelector('.live-link [data-link="CONSTRUCTION_DASHBOARD"][data-class="button"]')&&low.querySelector('.live-link [data-link="LOW_STATUS"]')&&low.querySelector('.live-link [data-link="CONSTRUCTION_STATUS"]'),'progress pages lead with the dashboard, then the site status slides and the overall status');
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
 const lh=await runGroups('letterheads.html',['SKAO_Letterhead_UNRESTRICTED.docx','skao_wordletterhead_Bradford Office.docx','skao_wordletterhead_Chapman Office.docx','skao_wordletterhead_Landscape.docx']);
 assert.deepEqual(Object.keys(lh.out),['By information classification','United Kingdom','Australia'],'letterheads by classification, then by site');
 assert.deepEqual(lh.out['Australia'],['Bradford Office','Chapman Office']);assert.deepEqual(lh.out['United Kingdom'],['Landscape layout']);assert(lh.notes.includes('Geraldton offices'));
 const vid=await runGroups('video.html',['LOGO_FLARE.mp4','LOGO_FLARE_STATEMENT_1.mp4','LOGO_FLARE_PORTRAIT.mp4','LOGO_FLARE_PORTRAIR_TITLE_SPACE.mp4','SKAO logo animation 6 seconds.mp4','SKAO_LOWER_THIRDS.mogrt','SAFE_ZONE_REEL.png']);
 assert.deepEqual(Object.keys(vid.out),['Logo intros and outros: landscape','Logo intros and outros: portrait','Logo animations','Lower thirds','Framing guides']);
 assert.deepEqual(vid.out['Logo intros and outros: portrait'],['Logo flare','Logo flare title space']);assert.deepEqual(vid.out['Logo intros and outros: landscape'],['Logo flare','Logo flare statement 1']);
 const pt=await runGroups('partner-templates.html',['SKAO - SARAO Presentation template v2.pptx','SKAO_RCN_KeynoteTemplate.key','SKAO_RCN_PowerPointTemplate.pptx']);
 assert.deepEqual(pt.out,{'SKAO–SARAO':['Presentation template'],'SRCNet':['Presentation template']});
 const pl=await runGroups('partner-logos.html',['SKAO_SRCnet_logo_colour_rgb.png','SKAO_SRCnet_logo_colour_rgb.ai','SKAO_SRCnet_avatar_monowhite_rgb.eps','SKAO_ukSRC_logofiles.zip','SKAO_zaSRC_logofiles.zip']);
 assert.deepEqual(pl.out,{'SRCNet':['Logo colour','Avatar white'],'SRCNet regional centres':['ukSRC','zaSRC']});
 pass('Downloads group by classification, office and partner, merge formats into one row and use readable labels; page rules group by site, format and partner');
 const talksId=routes['recent-talks.html'].id;let talkUrl='';
 const tk=dom('recent-talks.html','confluence'),tw=tk.window;tw.document.body.dataset.pageId=talksId;
 tw.fetch=async u=>{const s=String(u);if(s.includes('/child/attachment')){talkUrl=s;return {ok:true,json:async()=>({results:[
  {title:'2026-07 Name SRCNet update.key',version:{when:'2026-07-15T10:00:00Z'},extensions:{fileSize:2097152},_links:{download:`/download/attachments/${talksId}/a.key`}},
  {title:'2026-10 Name Science overview.pptx',version:{when:'2026-10-15T10:00:00Z'},extensions:{fileSize:4194304},_links:{download:`/download/attachments/${talksId}/b.pptx`}},
  {title:'canto-123.jpg',version:{when:'2026-10-16T10:00:00Z'},_links:{download:`/download/attachments/${talksId}/c.jpg`}},
  {title:'off-site.pptx',version:{when:'2026-10-17T10:00:00Z'},_links:{download:'//evil.example/x'}}]})};}
  return {ok:true,json:async()=>({results:[]})};};
 tw.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 const talkQ=s=>tw.document.querySelector(s),trows=[...tw.document.querySelectorAll('.file-row')];
 assert(talkUrl.includes(`/rest/api/content/${talksId}/child/attachment`),'every file on the page, no label needed');
 assert.deepEqual(trows.map(r=>r.querySelector('strong').firstChild.textContent),['Name Science overview','Name SRCNet update'],'newest first, Canto thumbnails and off-site links dropped, date prefix read');
 assert.equal(talkQ('.file-latest').textContent,'Latest');assert(talkQ('.file-meta').textContent.startsWith('October 2026, added'));
 assert(talkQ('.attachments-add').href.includes('/pages/viewpageattachments.action?pageId='+talksId));assert.equal(talkQ('.attachments-add').textContent,'Add your talk');tk.window.close();
 const tp=dom('recent-talks.html');assert(tp.window.document.querySelector('.attachments-note').textContent.startsWith('Preview'));tp.window.close();
 pass('Recent talks and site progress list every file on their page, newest first, with an add link for the people who keep them current');
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
 {const d=dom('resources.html','confluence'),w=d.window,doc=w.document,rows=[...doc.querySelectorAll('.resource-row')],idOf=h=>rows.find(r=>r.getAttribute('href')===h).dataset.pageId;
  const lid=idOf('letterheads.html'),fid=idOf('fonts.html');
  w.fetch=async u=>{const cql=new URL(String(u),'http://localhost').searchParams.get('cql')||'';return {ok:true,json:async()=>({results:cql.includes('type=attachment')?[{title:'a.dotx',container:{id:lid},version:{when:'2026-10-10T09:00:00Z'}}]:[{id:fid,version:{when:'2026-10-12T09:00:00Z'}},{id:lid,version:{when:'2026-01-01T09:00:00Z'}}]})};};
  doc.body.dataset.mode='confluence';w.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();await wait();
  const titles=()=>[...doc.querySelectorAll('.resource-row')].map(r=>r.getAttribute('href'));
  assert.deepEqual(titles().slice(0,2),['fonts.html','letterheads.html'],'All resources lists the newest first');
  assert.equal(doc.querySelector('.resource-row[href="letterheads.html"] .resource-when').textContent,'Added 10 Oct 2026','a new approved file dates its page');
  assert.equal(doc.querySelector('.resource-row[href="fonts.html"] .resource-when').textContent,'Updated 12 Oct 2026','otherwise the page edit does');
  const sel=doc.querySelector('#resourceSort');assert(!doc.querySelector('.resource-sort').hidden);sel.value='az';sel.dispatchEvent(new w.Event('change'));
  const az=[...doc.querySelectorAll('.resource-row strong')].map(s=>s.textContent.toLowerCase());assert.deepEqual(az,[...az].sort((a,b)=>a.localeCompare(b)),'A to Z sorts by title');
  w.close();pass('All resources is dated and sorted newest first, with an A to Z option');}
 {const d=dom('video.html'),w=d.window,doc=w.document,g=doc.querySelector('.page-grid');
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
