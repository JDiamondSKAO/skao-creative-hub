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
 v.fetch=async u=>{url=u;return {ok:true,json:async()=>({results:[{id:'1',title:'<img src=x onerror=alert(1)>',ancestors:[{title:'<script>bad</script>'}],_links:{webui:'/pages/1'}}]})}};
 el('[data-search]').click();el('#searchInput').value='" OR space="OTHER';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();
 assert.equal(el('#searchResults img'),null);assert.equal(el('#searchResults script'),null);assert(el('#searchResults').textContent.includes('<img'));assert(new URL(url,'http://localhost').searchParams.get('cql').includes('\\"'));pass('Production search escapes CQL input and renders metadata as text');
 v.fetch=async()=>({status:403,ok:false});el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));await wait();assert(el('#searchStatus').textContent.includes('sign in'));pass('Permission failure is distinguished from no results');
 let complete=[];v.fetch=()=>new Promise(resolve=>complete.push(resolve));el('#searchInput').value='old';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));el('#searchInput').value='new';el('#searchForm').dispatchEvent(new v.Event('submit',{cancelable:true}));
 complete[1]({ok:true,json:async()=>({results:[{id:'2',title:'New result',_links:{webui:'/new'}}]})});await wait();complete[0]({ok:true,json:async()=>({results:[{id:'1',title:'Old result',_links:{webui:'/old'}}]})});await wait();assert(el('#searchResults').textContent.includes('New result'));assert(!el('#searchResults').textContent.includes('Old result'));pass('Late search responses cannot overwrite newer results');live.window.close();
 const f=dom('request.html'),fw=f.window;fw.document.querySelector('[name=Project]').value='<script>not executable</script>';fw.document.querySelector('#briefForm').dispatchEvent(new fw.Event('submit',{cancelable:true}));assert(!fw.document.querySelector('#draftPanel').hidden);assert(fw.document.querySelector('#briefOutput').textContent.includes('<script>'));assert(!fw.document.querySelector('#briefOutput script'));assert.equal(fw.localStorage.length,0);pass('Request composer prepares inert text without persisting or submitting it');f.window.close();
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
 assert.equal(rw.document.querySelectorAll('.choice-card').length,4);assert.equal(new Set([...rw.document.querySelectorAll('.choice-card')].map(a=>a.href)).size,4);rd.window.close();pass('Four resource routes offer distinct starting points');
 const pd=new JSDOM(fs.readFileSync(path.join(root,'docs/presentations.html'),'utf8'));
 const destinations=[...pd.window.document.querySelectorAll('.content-body > .choice-grid > a')].map(a=>a.href);assert.equal(new Set(destinations).size,3);assert(pd.window.document.querySelector('.source-check'));assert(pd.window.document.querySelector('.reuse-decision'));pass('Presentation starting points have distinct source routes and freshness/reuse guidance');
 for(const id of ['381891696','381891810']){const out=Velocity.render(tpl,{page:page(id,'Test'),pages:{home},contextPath:'',theme:{baseUrl:'/theme'},stringEscapeUtils:{escapeHtml:esc},webPanels:'',attributionLine:'Attribution',link:{page:(space,title)=>'/crh/'+encodeURIComponent(title)}});const doc=new JSDOM(out).window.document;assert(doc.querySelector(id==='381891696'?'.choice-grid':'.sharing-paths'));assert(![...doc.querySelectorAll('a')].some(a=>a.getAttribute('href').includes('$link')));}pass('Catalogue and contribution landing pages render in the production template');
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
 const result={status:'PASS',checks};fs.writeFileSync(path.join(root,'evidence/tests.json'),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exitCode=1});
