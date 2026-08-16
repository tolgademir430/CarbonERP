# V18 page-state patch
from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_show = "async function show(page){document.getElementById('nav').innerHTML=nav(page);document.getElementById('app').innerHTML=({dashboard,sales,customers,collections,due,purchases,expenses,stock,reports})[page]()}"
new_show = """const CARBONERP_PAGES=['dashboard','sales','customers','collections','due','purchases','expenses','stock','reports'];
function savedPage(){const p=sessionStorage.getItem('carbonerp_current_page');return CARBONERP_PAGES.includes(p)?p:'dashboard'}
async function show(page){
  if(!CARBONERP_PAGES.includes(page)) page='dashboard';
  sessionStorage.setItem('carbonerp_current_page',page);
  history.replaceState(null,'','#'+page);
  document.getElementById('nav').innerHTML=nav(page);
  document.getElementById('app').innerHTML=({dashboard,sales,customers,collections,due,purchases,expenses,stock,reports})[page]();
}"""
if old_show not in s:
    raise SystemExit('V18 show() marker not found')
s = s.replace(old_show, new_show, 1)

old_login = "await loadData();await repairLegacyGeneralCollections();await loadData();show('dashboard')"
new_login = "await loadData();await repairLegacyGeneralCollections();await loadData();show(savedPage())"
if old_login in s:
    s = s.replace(old_login, new_login, 1)
else:
    old_login = "await loadData();show('dashboard')"
    if old_login in s:
        s = s.replace(old_login, "await loadData();show(savedPage())", 1)
    else:
        raise SystemExit('V18 auth-state marker not found')

old_init = "try{await loadData();show('dashboard')}catch(e)"
new_init = "try{await loadData();show(savedPage())}catch(e)"
if old_init not in s:
    raise SystemExit('V18 initial-load marker not found')
s = s.replace(old_init, new_init, 1)

p.write_text(s, encoding='utf-8')
print('V18 page state applied')
