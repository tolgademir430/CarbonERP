from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<script>window\.onload=\(\)=>window\.print\(\)<.*?/script>', '', s)
s=re.sub(r'<script\s+src=["\']sales-fix\.js["\']>.*?/script>', '', s)
p.write_text(s,encoding='utf-8')
