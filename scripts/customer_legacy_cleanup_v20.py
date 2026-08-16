from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
replacements=[
    '<script>window.onload=()=>window.print()<\\/script>',
    '<script>window.onload=()=>window.print()</script>',
    '<script src="sales-fix.js"><\\/script>',
    '<script src="sales-fix.js"></script>',
]
for old in replacements:
    s=s.replace(old,'')
p.write_text(s,encoding='utf-8')
