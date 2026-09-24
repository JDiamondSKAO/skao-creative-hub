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
 q('[data-search]').click();assert(q('dialog').open);q('#searchInput').value='presentation';q('#searchForm').dispatchEvent(new w.Event('submit',{cancelable:true}));await wait();assert.equal(q('#searchResults a').textContent,'PresentationSlides');pass('Preview search returns actual navigable results');
 q('#closeSearch').click();assert(!q('dialog').open);pass('Search closes');d.window.close();
 const live=dom('index.html','confluence'),v=live.window,el=s=>v.document.querySelector(s);let url;
 v.fetch=async u=>{if(String(u).includes('attachment'))return {ok:true,json:async()=>({results:[]})};url=u;return {ok:true,json:async()=>({results:[{id:'1',title:'<img src=x onerror=alert(1)>',ancestors:[{title:'<script>bad</script>'}],_links:{webui:'/pages/1'}}]})}};
 el('[data-search]').click();el('#searchInput').value='" OR space="OTHER';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();
 assert.equal(el('#searchResults img'),null);assert.equal(el('#searchResults script'),null);assert(el('#searchResults').textContent.includes('<img'));assert(new URL(url,'http://localhost').searchParams.get('cql').includes('\\"'));pass('Production search escapes CQL input and renders metadata as text');
 v.fetch=async()=>({status:403,ok:false});el('#searchInput').value='permission';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();assert(el('#searchStatus').textContent.includes('sign in'));pass('Permission failure is distinguished from no results');
 let complete=[];v.fetch=()=>new Promise(resolve=>complete.push(resolve));el('#searchInput').value='old';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));el('#searchInput').value='new';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));
 complete[1]({ok:true,json:async()=>({results:[{id:'2',title:'New result',_links:{webui:'/new'}}]})});await wait();complete[0]({ok:true,json:async()=>({results:[{id:'1',title:'Old result',_links:{webui:'/old'}}]})});await wait();assert(el('#searchResults').textContent.includes('New result'));assert(!el('#searchResults').textContent.includes('Old result'));pass('Late search responses cannot overwrite newer results');live.window.close();
 const f=dom('request.html'),fw=f.window;fw.document.querySelector('[name=Project]').value='<script>not executable</script>';fw.document.querySelector('#briefForm').dispatchEvent(new fw.Event('submit',{cancelable:true}));assert(!fw.document.querySelector('#draftPanel').hidden);assert(fw.document.querySelector('#briefOutput').textContent.includes('<script>'));assert(!fw.document.querySelector('#briefOutput script'));assert(![...Array(fw.localStorage.length)].some((_,i)=>fw.localStorage.getItem(fw.localStorage.key(i)).includes('not executable')));assert.deepEqual([...Array(fw.localStorage.length)].map((_,i)=>fw.localStorage.key(i)).filter(k=>k!=='crh-recent'),[]);pass('Request composer prepares inert text without persisting or submitting it');f.window.close();
 const t=dom();t.window.matchMedia=()=>({matches:true});t.window.eval(fs.readFileSync(path.join(root,'js/theme.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", function () {",'(function () {').replace(/\}\);\s*$/, '})();'));t.window.document.querySelector('#themeToggle').click();assert(t.window.document.documentElement.classList.contains('dark'));assert.equal(t.window.localStorage.getItem('crh-theme'),'dark');pass('Reduced-motion toggle changes and saves theme without animation');t.window.close();
 const tpl=fs.readFileSync(path.join(root,'page.vm'),'utf8');Velocity.parse(tpl);pass('Velocity template parses');
 const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
 function page(id,title){return {id:String(id),title,absoluteLink:'/crh/'+id,ancestors:[],children:[],resources:{meta:'',css:'',js:''},content:'<p>Confluence content</p>'};}
 const home=page('381887066','Home'),deep=page('99','Quotes " and <markup>');deep.ancestors=[home];deep.parent=home;
 for(const p of [home,deep,page('381891661','Submitting a Request')]){
 const out=Velocity.render(tpl,{page:p,pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution'});
 const doc=new JSDOM(out).window.document;assert.equal(doc.querySelectorAll('h1').length,1);assert(!doc.title.includes('$'));assert(out.includes('Attribution'));
 if(p===deep){assert(doc.querySelector('.content-body').textContent.includes('Confluence content'));assert.equal(doc.title,'Quotes " and <markup> | SKAO Creative Hub');}
 if(p.id==='381891661')assert(doc.querySelector('#briefForm'));
 }
 pass('Home, deep page and request route render with escaping and one H1');
 for(const file of fs.readdirSync(path.join(root,'docs')).filter(f=>f.endsWith('.html'))){const doc=new JSDOM(fs.readFileSync(path.join(root,'docs',file),'utf8')).window.document;assert.equal(doc.querySelectorAll('h1').length,1);for(const e of doc.querySelectorAll('[href],[src]')){const h=e.getAttribute('href')||e.getAttribute('src');assert.notEqual(h,'#');if(!/^(https?:|mailto:|#)/.test(h))assert(fs.existsSync(path.join(root,'docs',h.split('#')[0].split('?')[0])),`${file}: ${h}`);}}
 pass('All preview pages have one H1 and resolve local links/assets');
 const hd=dom(),hw=hd.window,hq=s=>hw.document.querySelector(s);
 assert.equal(hw.document.querySelectorAll('[data-search]').length,1);assert(!hq('#homeSearch'));hq('[data-search]').click();hq('#searchInput').value='presentation';hq('#searchForm').dispatchEvent(new hw.Event('submit',{cancelable:true}));await wait();assert(hq('dialog').open);assert(hq('#searchResults a'));hq('#searchInput').dispatchEvent(new hw.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));assert(!hq('dialog').open);assert.equal(hw.document.activeElement,hq('[data-search]'));assert.equal(hq('.presentation-feature').getAttribute('href'),'presentations.html');hd.window.close();pass('Single navigation search works and restores focus; featured card opens presentations');
 const rd=dom('resources.html'),rw=rd.window,rq=s=>rw.document.querySelector(s);
 assert.equal(rw.document.querySelectorAll('.choice-card').length,0,'no duplicate starting-point cards');assert(rq('.page-grid.full-width .catalogue'));assert(!rq('.sidebar'));
 for(const t of ['presentations','documents','brand','media'])assert(rq(`[data-type-filter="${t}"]`),t);rd.window.close();pass('Templates and assets is one full-width catalogue with type filters instead of duplicate cards');
 const pd=new JSDOM(fs.readFileSync(path.join(root,'docs/presentations.html'),'utf8'));
 const pdoc=pd.window.document,destinations=[...pdoc.querySelectorAll('.directory .dir-row')].map(a=>a.getAttribute('href'));
 for(const f of ['standard-template.html','widescreen-template.html','master-deck.html','science-slides.html','low-slides.html','mid-slides.html','construction-slides.html','specialised-slides.html','formatting-slides.html'])assert(destinations.includes(f),f);
 assert.equal(new Set(destinations).size,destinations.length);assert(!pdoc.querySelector('.content-body details'),'landing content is not hidden');assert(pdoc.querySelector('.source-check'));assert(pdoc.querySelector('.reuse-decision'));
 pass('Presentations landing shows every presentation page, grouped and visible, with freshness/reuse guidance');
 for(const id of ['381891696','381891810']){const out=Velocity.render(tpl,{page:page(id,'Test'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});const doc=new JSDOM(out).window.document;assert(doc.querySelector(id==='381891696'?'.page-grid.full-width .catalogue':'.sharing-paths'));assert(![...doc.querySelectorAll('a')].some(a=>a.getAttribute('href').includes('$link')));}pass('Catalogue and contribution landing pages render in the production template');
 const routes=JSON.parse(fs.readFileSync(path.join(root,'evidence/interior-route-map.json')));
 assert.equal(Object.keys(routes).length,60);
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
 pass('All 60 observed production routes render their reviewed content and resolved links');
 const sd=dom(),sw=sd.window,sq=s=>sw.document.querySelector(s);
 sw.fetch=async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(path.join(root,'docs/search-index.json'),'utf8'))});
 const run=async v=>{sq('#searchInput').value=v;sq('#searchInput').dispatchEvent(new sw.Event('input'));sq('#searchForm').dispatchEvent(new sw.Event('submit',{cancelable:true}));await wait();return [...sw.document.querySelectorAll('#searchResults a strong')].map(e=>e.textContent);};
 sq('[data-search]').click();assert(!sq('#searchSuggest').hidden);assert(sw.document.querySelectorAll('#searchSuggest a').length>=6);
 assert.equal((await run('logo'))[0],'Logos and icons');
 assert((await run('powerpoint template')).some(t=>/template/i.test(t)));
 assert((await run('color')).some(t=>/colour/i.test(t)));assert(sq('#searchResults mark'));assert(sq('#searchSuggest').hidden);
 assert.equal((await run('class')).length,0,'markup must not be searchable');
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
 const cardTitles=[...cw.document.querySelectorAll('.resource-row strong')].map(h=>h.textContent);assert(cardTitles.length>=40);assert.equal(new Set(cardTitles).size,cardTitles.length,'catalogue titles are unique');
 const total=shown();cq('[data-type-filter="brand"]').click();assert(shown()<total&&shown()>0);assert.equal(cq('[data-type-filter="brand"]').getAttribute('aria-pressed'),'true');
 cq('#resourceFilter').value='color';cq('#resourceFilter').dispatchEvent(new cw.Event('input'));assert(shown()>0,'synonyms apply to the catalogue filter');
 cq('#resourceFilter').value='zzzz';cq('#resourceFilter').dispatchEvent(new cw.Event('input'));assert.equal(shown(),0);assert(!cq('#catalogueEmpty').hidden);
 cq('#clearFilters').click();assert.equal(shown(),total);pass('Resource catalogue lists every resource once and filters by type and name');cd.window.close();
 const idx=JSON.parse(fs.readFileSync(path.join(root,'docs/search-index.json'),'utf8'));assert(!idx.find(r=>r.href==='resources.html').keywords.includes('Letterheads'),'catalogue must not flood the search index');
 const hs=dom(),hsw=hs.window,hsq=s=>hsw.document.querySelector(s);hsw.fetch=async()=>({ok:true,json:async()=>idx});
 hsq('#heroSearch').value='l';hsq('#heroSearch').dispatchEvent(new hsw.Event('input'));assert(hsq('dialog').open);assert.equal(hsq('#searchInput').value,'l');assert.equal(hsq('#heroSearch').value,'');
 pass('Homepage search box hands typing over to the search dialog');hs.window.close();
 const resOut=Velocity.render(tpl,{page:page('381891696','Templates & Assets'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});
 const rdoc=new JSDOM(resOut).window.document;const rlinks=[...rdoc.querySelectorAll('.resource-row')].map(a=>a.getAttribute('href'));assert(rlinks.length>=40);assert(rlinks.every(h=>h.startsWith('/crh/')),rlinks.find(h=>!h.startsWith('/crh/')));
 assert(rdoc.querySelector('.page-band h1'));assert.equal(rdoc.querySelectorAll('.footer nav a').length,6);assert(rdoc.querySelector('.page-grid.full-width'));assert(!rdoc.querySelector('.sidebar'));
 pass('Production catalogue, title band and footer render with resolved Confluence links');
 const md=new JSDOM(fs.readFileSync(path.join(root,'docs/master-deck.html'),'utf8')).window.document;
 assert(md.querySelector('.asset-panel .status-pill'));assert(!md.querySelector('.availability-note'));assert(md.querySelector('.section-nav a[href="presentations.html"]'));
 assert.equal(md.querySelectorAll('.section-next .related-card').length,3);assert(md.querySelector('.related-next'));assert(md.querySelector('.breadcrumbs a[href="presentations.html"]'));
 pass('Resource pages show a status panel, section navigation, section breadcrumb and next pages');
 const ck=dom('event-checklist.html'),kw=ck.window,kq=s=>kw.document.querySelector(s),boxes=[...kw.document.querySelectorAll('.check-list input')];
 assert(boxes.length>=6);boxes[0].checked=true;boxes[0].dispatchEvent(new kw.Event('change'));assert(kq('.checklist-progress').textContent.startsWith('1 of'));
 assert(kw.localStorage.getItem('crh-check:event-checklist.html').includes('0'));kq('[data-checklist-reset]').click();assert(kq('.checklist-progress').textContent.startsWith('0 of'));
 pass('Checklists track progress and can be cleared');ck.window.close();
 const rqd=dom("request.html"),rqw=rqd.window,rqq=s=>rqw.document.querySelector(s);
 assert.equal(rqw.document.querySelectorAll('.route-card').length,2);assert(!rqq('#brief-builder').open);rqq('[data-open-details]').click();assert(rqq('#brief-builder').open);
 pass('Request page offers two routes and opens the brief helper');rqd.window.close();
 const pv=dom(),pvq=s=>pv.window.document.querySelector(s);assert.equal(pv.window.document.querySelectorAll('#latestAssets .asset-card').length,3);
 assert(pv.window.document.querySelectorAll('#latestAssets .example-tag').length===3);assert(!pvq('#latestAssets a[href]'),'preview examples must not link to files');pv.window.close();
 const lv=dom('index.html','confluence');await wait();
 const calls=[];const att=(title,extra={})=>({title,version:{when:'2026-09-20T10:00:00Z'},extensions:{fileSize:2048},_links:{download:'/download/'+title},container:{title:'<b>Letterheads</b>',_links:{webui:'/letterheads'}},...extra});
 lv.window.fetch=async u=>{const cql=new URL(u,'http://localhost').searchParams.get('cql');calls.push(cql);return {ok:true,json:async()=>({results:cql.includes('label=')?[]:[att('image-2026.png'),att('Letterhead.dotx'),att('javascript-trick.pdf',{_links:{download:'https://evil.example/x.pdf'}})]})}};
 const box=lv.window.document.querySelector('#latestAssets');await lv.window.eval('0');
 lv.window.document.body.dataset.mode='confluence';
 // Re-run the loader against the mocked API.
 lv.window.eval(fs.readFileSync(path.join(root,'js/main.js'),'utf8').replace("document.addEventListener(\"DOMContentLoaded\", () => {",'(()=>{').replace(/\}\);\s*$/, '})();'));await wait();await wait();
 assert(calls.some(c=>c.includes('label="approved"')));assert(calls.some(c=>!c.includes('label=')));
 const names=[...box.querySelectorAll('.asset-card h3')].map(h=>h.textContent);assert(names.includes('Letterhead'));assert(!names.some(n=>n.includes('image')),'page images are not listed');
 assert.equal(lv.window.document.querySelector('#latestHeading').textContent,'Latest files in the Hub');assert(!box.querySelector('a[href^="https://evil"]'));assert(!box.querySelector('b'));
 pass('Latest assets prefer the approval label, fall back honestly to deliverable files and render safely');lv.window.close();
 const nd=dom('fonts.html'),nw=nd.window,nq=s=>nw.document.querySelector(s);
 const top=[...nw.document.querySelectorAll('#mainNav > a')];assert.equal(top.length,7);assert.equal(nw.document.querySelectorAll('#mainNav a').length,7,'menu has no nested panels');
 assert.equal(nq('#mainNav a[aria-current]').getAttribute('href'),'brand.html');
 const twoClicks=new Set(top.map(a=>a.getAttribute('href')));
 for(const a of top){const land=new JSDOM(fs.readFileSync(path.join(root,'docs',a.getAttribute('href')),'utf8')).window.document;
  assert(land.querySelector('.page-grid.full-width'),'landing is full width');assert(!land.querySelector('.sidebar'),'landing has no repeated list');
  land.querySelectorAll('.dir-row').forEach(c=>twoClicks.add(c.getAttribute('href')));}
 for(const f of Object.keys(routes).filter(f=>!['canto-guide.html','resources.html'].includes(f)))assert(twoClicks.has(f),'two clicks reach '+f);
 assert.equal([...nw.document.querySelectorAll('.section-nav h3')].map(h=>h.textContent).join('|'),'Artwork and files|Using the brand|Partner brands');nd.window.close();
 const fontsOut=new JSDOM(Velocity.render(tpl,{page:page('381891882','Font Downloads'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}})).window.document;
 assert(fontsOut.querySelector('.breadcrumbs').textContent.includes('Brand'));assert.equal(fontsOut.querySelectorAll('.section-nav h3').length,3);
 pass('Seven section links reach every page within two clicks; landings are full width, detail pages share the section groups in sidebar and breadcrumb');
 const result={status:'PASS',checks};fs.writeFileSync(path.join(root,'evidence/tests.json'),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exitCode=1});
