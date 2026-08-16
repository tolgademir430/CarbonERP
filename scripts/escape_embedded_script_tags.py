from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
main_start=s.find('<script>\nconst SUPABASE_URL')
body_pos=s.rfind('</body>')
if main_start<0 or body_pos<=main_start:
    raise SystemExit('main application script not found')
region=s[main_start:body_pos]
last_close=region.rfind('</script>')
if last_close<0:
    raise SystemExit('main application script closing tag not found')
before=region[:last_close].replace('</script>','<\\/script>')
region=before+'</script>'
s=s[:main_start]+region+s[body_pos:]
p.write_text(s,encoding='utf-8')
print('embedded script closers escaped')
