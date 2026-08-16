from pathlib import Path
import re
import subprocess
import tempfile

p=Path('index.html')
s=p.read_text(encoding='utf-8')
errors=[]
main_start=s.find('<script>\nconst SUPABASE_URL')
body_pos=s.rfind('</body>')
if main_start<0 or body_pos<=main_start:
    errors.append('main application script not found')
else:
    region=s[main_start:body_pos]
    last_close=region.rfind('</script>')
    if last_close<0:
        errors.append('main application script closing tag not found')
    else:
        embedded=region[:last_close].count('</script>')
        if embedded:
            errors.append(f'unescaped </script> inside application JavaScript: {embedded}')
        js=region[len('<script>'):last_close]
        with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as f:
            f.write(js); name=f.name
        r=subprocess.run(['node','--check',name],capture_output=True,text=True)
        if r.returncode:
            errors.append('application JavaScript syntax error: '+r.stderr.strip())

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
if errors:
    print('\n'.join('ERROR: '+x for x in errors))
    raise SystemExit(1)
print('CarbonERP V20 validation passed')
