"""Make a flat upload set for the space-level theme editor (no global plugin install)."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];out=R/'release/staging-files';out.mkdir(exist_ok=True)
s=(R/'page.vm').read_text()
for d in ['css','js','images']:s=s.replace('${theme.baseUrl}/'+d+'/', '${theme.baseUrl}/')
(out/'page.vm').write_text(s)
css=(R/'css/style.css').read_text().replace('../fonts/','')
(out/'style.css').write_text(css)
for d in ['js','images','fonts']:
 for p in (R/d).iterdir():
  if p.is_file():shutil.copy2(p,out/p.name)
print(out.resolve())
