from pathlib import Path
import re
import subprocess
import tempfile

p=Path('index.html')
s=p.read_text(encoding='utf-8')
errors=[]

# Validate every inline script independently. External CDN scripts are skipped.
scripts=list(re.finditer(r'<script(?:\s[^>]*)?>(.*?)</script>',s,flags=re.I|re.S))
if not scripts:
    errors.append('no script blocks found')
for i,m in enumerate(scripts,1):
    tag=s[m.start():m.start()+s[m.start():].find('>')+1]
    if re.search(r'\bsrc\s*=',tag,re.I):
        continue
    js=m.group(1)
    # HTML printed inside template literals may contain script tags. Those are
    # content, not application script blocks, so remove them only for parsing.
    js_for_check=re.sub(r'</?script(?:\s[^>]*)?>','',js,flags=re.I)
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f:
        f.write(js_for_check)
        name=f.name
    r=subprocess.run(['node','--check',name],capture_output=True,text=True)
    if r.returncode:
        errors.append(f'inline JavaScript syntax error in script #{i}: {r.stderr.strip()}')

if s.count('CARBONERP_V20_CORE') != 1:
    errors.append('expected exactly one CARBONERP_V20_CORE')
if s.count('CARBONERP_V20_FINAL') != 1:
    errors.append('expected exactly one CARBONERP_V20_FINAL')
if 'CARBONERP_V19_CONTROLS' in s:
    errors.append('legacy V19 control block remains')
if s.count('function v16DateOnly') != 1:
    errors.append(f'expected one v16DateOnly, found {s.count("function v16DateOnly")}')

# Only actual function declarations are checked for duplicates; window assignments
# are intentionally allowed because V20 uses them to replace legacy handlers.
names=re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',s)
seen=set();dups=set()
for n in names:
    if n in seen: dups.add(n)
    seen.add(n)
allowed={'login','logout'}
if dups-allowed:
    errors.append('duplicate function declarations: '+', '.join(sorted(dups-allowed)))

if errors:
    print('\n'.join('ERROR: '+x for x in errors))
    raise SystemExit(1)
print('CarbonERP V20 validation passed')
