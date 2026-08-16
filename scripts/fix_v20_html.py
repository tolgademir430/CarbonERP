from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='\n<script>\n/* CARBONERP_V20_CORE'
if marker not in s:
    raise SystemExit('V20 marker not found')
prefix, rest=s.split(marker,1)
# The first patch temporarily inserted </body></html> before V20. Remove it,
# close the original application script, then place V20 before body/html.
prefix=prefix.rstrip()
if prefix.endswith('</html>'):
    prefix=prefix[:prefix.rfind('</html>')].rstrip()
if prefix.endswith('</body>'):
    prefix=prefix[:prefix.rfind('</body>')].rstrip()
# Keep exactly one V20 script and exactly one document closing sequence.
if '\n</script>' in rest:
    v20=rest.rsplit('\n</script>',1)[0]+'\n</script>'
else:
    raise SystemExit('V20 closing script not found')
s=prefix+'\n</script>\n'+v20+'\n</body>\n</html>\n'
p.write_text(s,encoding='utf-8')
print('V20 HTML structure fixed')
