from pathlib import Path
import re
import subprocess
import tempfile

p=Path('index.html')
s=p.read_text(encoding='utf-8')
errors=[]

def inline_scripts(html):
    out=[]; pos=0; n=len(html); lower=html.lower()
    while True:
        start=lower.find('<script',pos)
        if start<0: break
        gt=lower.find('>',start)
        if gt<0:
            out.append((html[start:],'')); break
        tag=html[start:gt+1]
        end=lower.find('</script>',gt+1)
        if end<0:
            out.append((tag,html[gt+1:])); break
        out.append((tag,html[gt+1:end])); pos=end+len('</script>')
    return out

scripts=inline_scripts(s)
if not scripts:
    errors.append('no script blocks found')
for i,(tag,js) in enumerate(scripts,1):
    if re.search(r'\bsrc\s*=',tag,re.I):
        continue
    with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f:
        f.write(js)
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
