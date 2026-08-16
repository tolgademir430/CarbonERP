from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,flags=re.S|re.I)
for i,body in enumerate(scripts,1):
    print(f'--- SCRIPT {i} chars={len(body)} ---')
    lines=body.splitlines()
    for n,line in list(enumerate(lines,1))[-25:]: print(f'{n}: {line[:240]}')
    print('backticks=',body.count('`'),'braces=',body.count('{')-body.count('}'),'parens=',body.count('(')-body.count(')'))
