from pathlib import Path
import zipfile,hashlib,json,xml.etree.ElementTree as ET,shutil
R=Path(__file__).resolve().parents[1]
(R/'release').mkdir(exist_ok=True)
files=[R/'page.vm']+[p for d in ['css','js','images','fonts'] for p in (R/d).rglob('*') if p.is_file()]
plugin=ET.Element('atlassian-plugin',{'key':'skao-creative-hub-v2','name':'SKAO Creative Hub v2 - Scroll Sites Theme','plugins-version':'2'})
info=ET.SubElement(plugin,'plugin-info');ET.SubElement(info,'version').text='2.11.0'
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
print('Packaged separate theme JAR/ZIP and preview ZIP')
