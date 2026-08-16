from pathlib import Path
from html.parser import HTMLParser
import re
import subprocess
import tempfile

class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts=[]
        self.in_script=False
        self.current=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='script':
            self.in_script=True
            self.current=[]
    def handle_data(self,data):
        if self.in_script:self.current.append(data)
    def handle_entityref(self,name):
        if self.in_script:self.current.append('&'+name+';')
    def handle_charref(self,name):
        if self.in_script:self.current.append('&#'+name+';')
    def handle_endtag(self,tag):
        if tag.lower()=='script' and self.in_script:
            self.scripts.append(''.join(self.current))
            self.in_script=False

p=Path('index.html')
s=p.read_text(encoding='utf-8')
errors=[]
parser=ScriptCollector();parser.feed(s);parser.close()
actual_script_tags=len(parser.scripts)
if actual_script_tags<2:
    errors.append(f'expected application scripts, found {actual_script_tags}')
if s.count('CARBONERP_V20_CORE') != 1:
    errors.append('expected exactly one CARBONERP_V20_CORE')
if 'CARBONERP_V19_CONTROLS' in s:
    errors.append('legacy V19 control block remains')
if s.count('function v16DateOnly') != 1:
    errors.append(f'expected one v16DateOnly, found {s.count("function v16DateOnly")}')
names=re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',s)
seen=set();dups=set()
for n in names:
    if n in seen: dups.add(n)
    seen.add(n)
allowed={'login','logout'}
if dups-allowed:
    errors.append('duplicate function declarations: '+', '.join(sorted(dups-allowed)))
for i,js in enumerate(parser.scripts,1):
    if not js.strip():
        continue
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f:
        f.write(js); name=f.name
    r=subprocess.run(['node','--check',name],capture_output=True,text=True)
    if r.returncode:
        errors.append(f'inline script #{i} syntax error: {r.stderr.strip()}')
if errors:
    print('\n'.join('ERROR: '+x for x in errors))
    raise SystemExit(1)
print(f'CarbonERP V20 validation passed: {actual_script_tags} inline script blocks parsed')
