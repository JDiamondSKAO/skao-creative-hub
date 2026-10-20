from pathlib import Path
import zipfile,hashlib,json,xml.etree.ElementTree as ET,shutil,subprocess,sys,os,html
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'));import links
(R/'release').mkdir(exist_ok=True)
# The release carries the internal addresses from the gitignored dev/links.json.
# The committed build never does, so it is rebuilt without them once the zips are made.
def build(with_links):
 env={k:v for k,v in os.environ.items() if k!='HUB_LOCAL_LINKS'}
 if with_links:env['HUB_LOCAL_LINKS']='1'
 subprocess.run([sys.executable,str(R/'scripts/build.py')],check=True,capture_output=True,env=env)
addresses=list(links.load().values())
# Pages carry each address HTML-escaped, so an & in it reads &amp; there.
found=lambda a,text:a in text or html.escape(a,quote=True) in text
build(True)
try:
 files=[R/'page.vm']+[p for d in ['css','js','images','fonts'] for p in (R/d).rglob('*') if p.is_file()]
 plugin=ET.Element('atlassian-plugin',{'key':'skao-creative-hub-v2','name':'SKAO Creative Hub v2 - Scroll Sites Theme','plugins-version':'2'})
 info=ET.SubElement(plugin,'plugin-info');ET.SubElement(info,'version').text='2.20.0'
 theme=ET.SubElement(plugin,'scroll-viewport-theme',{'key':'skao-creative-hub-v2','name':'SKAO Creative Hub v2'})
 for p in files:
  name=str(p.relative_to(R));ET.SubElement(theme,'resource',{'name':name,'location':name})
 manifest=ET.tostring(plugin,encoding='utf-8',xml_declaration=True)
 (R/'atlassian-plugin.xml').write_bytes(manifest)
 for suffix in ['jar','zip']:
  with zipfile.ZipFile(R/f'release/skao-creative-hub-v2.{suffix}','w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('META-INF/MANIFEST.MF','Manifest-Version: 1.0\n\n');z.writestr('atlassian-plugin.xml',manifest)
   for p in files:z.write(p,str(p.relative_to(R)))
 with zipfile.ZipFile(R/'release/skao-creative-hub-v2-preview.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in (R/'docs').rglob('*'):
   if p.is_file():z.write(p,str(p.relative_to(R/'docs')))
 # Flat set for the space-level theme editor: every file at the root, paths rewritten to match.
 import subprocess,sys
 version=info.find('version').text
 subprocess.run([sys.executable,str(R/'scripts/staging_files.py')],check=True,capture_output=True)
 # Other versions' uploads stay, so each branch's release can sit side by side.
 with zipfile.ZipFile(R/f'release/skao-creative-hub-v{version}-flat-upload.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((R/'release/staging-files').iterdir()):
   if p.is_file():z.write(p,p.name)
 flat=zipfile.ZipFile(R/f'release/skao-creative-hub-v{version}-flat-upload.zip').read('page.vm').decode()
 assert '${theme.baseUrl}/css/' not in flat and '${theme.baseUrl}/style.css' in flat, 'flat page.vm must point at root files'
 assert all(found(a,flat) for a in addresses),'release page.vm is missing a link from dev/links.json'
 print(f'Packaged theme JAR/ZIP, preview ZIP and v{version} flat upload with {len(addresses)} local links')
finally:
 build(False)
assert not any(found(a,(R/'page.vm').read_text()) for a in addresses),'committed page.vm must not carry internal links'
