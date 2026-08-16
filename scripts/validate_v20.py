from pathlib import Path
import re
import subprocess
import tempfile

p=Path('index.html')
s=p.read_text(encoding='utf-8')
errors=[]
if s.count('<script') != s.count('</script>'):
    errors.append(f'script tag balance: {s.count("<script")} open vs {s.count("</script>")} close')
if s.count('CARBONERP_V20_CORE') != 1:
    errors.append('expected exactly one CARBONERP_V20_CORE')
if 'CARBONERP_V19_CONTROLS' in s:
    errors.append('legacy V19 control block remains')
if s.count('function v16DateOnly') != 1:
    errors.append(f'expected one v16DateOnly, found {s.count("function v16DateOnly")}')
# Duplicate classic function declarations are a maintenance/runtime hazard in this single-file app.
names=re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',s)
seen=set();dups=set()
for n in names:
    if n in seen: dups.add(n)
    seen.add(n)
allowed={'login','logout'}
if dups-allowed:
    errors.append('duplicate function declarations: '+', '.join(sorted(dups-allowed)))
# Syntax-check every inline executable script with Node.js.
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)
for i,js in enumerate(scripts,1):
    if not js.strip() or 'src=' in s[:0]:
        continue
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f:
        f.write(js); name=f.name
    r=subprocess.run(['node','--check',name],capture_output=True,text=True)
    if r.returncode:
        errors.append(f'inline script #{i} syntax error: {r.stderr.strip()}')
if errors:
    print('\n'.join('ERROR: '+x for x in errors))
    raise SystemExit(1)
print('CarbonERP V20 validation passed')
