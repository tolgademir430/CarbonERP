from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Add a dedicated V16 Vade page to the existing navigation.
old_nav = "function nav(page){const pages=['dashboard','sales','customers','collections','purchases','expenses','stock','reports'];const labels={dashboard:'Dashboard',sales:'Satış',customers:'Müşteriler',collections:'Tahsilatlar',purchases:'Alışlar',expenses:'Giderler',stock:'Stok',reports:'Raporlar'};return pages.map(x=>`<button class=\"${x===page?'active':''}\" onclick=\"show('${x}')\">${labels[x]}</button>`).join('')}"
new_nav = "function nav(page){const pages=['dashboard','sales','customers','collections','due','purchases','expenses','stock','reports'];const labels={dashboard:'Dashboard',sales:'Satış',customers:'Müşteriler',collections:'Tahsilatlar',due:'Vade Takibi',purchases:'Alışlar',expenses:'Giderler',stock:'Stok',reports:'Raporlar'};return pages.map(x=>`<button class=\"${x===page?'active':''}\" onclick=\"show('${x}')\">${labels[x]}</button>`).join('')}"
if old_nav in s:
    s = s.replace(old_nav, new_nav, 1)
elif "pages=['dashboard','sales','customers','collections','due'" not in s:
    raise SystemExit('navigation marker not found')

old_show = "async function show(page){document.getElementById('nav').innerHTML=nav(page);document.getElementById('app').innerHTML=({dashboard,sales,customers,collections,purchases,expenses,stock,reports})[page]()}"
new_show = "async function show(page){document.getElementById('nav').innerHTML=nav(page);document.getElementById('app').innerHTML=({dashboard,sales,customers,collections,due,purchases,expenses,stock,reports})[page]()}"
if old_show in s:
    s = s.replace(old_show, new_show, 1)

marker = 'function customers(){'
if marker not in s:
    raise SystemExit('customers marker not found')

v16 = r'''function v16DateOnly(d){return new Date(d+'T00:00:00')}
function v16DiffDays(from,to){const a=v16DateOnly(from),b=v16DateOnly(to);return Math.round((b-a)/86400000)}
function v16Status(s){
  const out=saleOutstanding(s), d=s.due_date;
  if(out<=0)return {label:'Kapandı',cls:'positive',days:0};
  if(!d)return {label:'Vade yok',cls:'warning',days:0};
  const diff=v16DiffDays(today(),d);
  if(diff<0)return {label:Math.abs(diff)+' gün gecikmiş',cls:'danger',days:diff};
  if(diff===0)return {label:'Bugün vadesi',cls:'warning',days:0};
  if(diff<=7)return {label:diff+' gün kaldı',cls:'warning',days:diff};
  return {label:diff+' gün kaldı',cls:'positive',days:diff};
}
function v16OpenSales(){return (data.sales||[]).filter(s=>saleOutstanding(s)>0 && s.due_date)}
function v16Summary(){
 const rows=v16OpenSales();
 const overdue=rows.filter(s=>s.due_date<today());
 const todayRows=rows.filter(s=>s.due_date===today());
 const next7=rows.filter(s=>s.due_date>today()&&s.due_date<=new Date(Date.now()+7*86400000).toISOString().slice(0,10));
 return {rows,overdue,todayRows,next7,overdueAmount:overdue.reduce((a,s)=>a+saleOutstanding(s),0),todayAmount:todayRows.reduce((a,s)=>a+saleOutstanding(s),0),next7Amount:next7.reduce((a,s)=>a+saleOutstanding(s),0)};
}
function v16CustomerSummary(rows){
 const map={};
 rows.forEach(s=>{const id=s.customer_id;if(!map[id])map[id]={id,amount:0,count:0,oldest:s.due_date};map[id].amount+=saleOutstanding(s);map[id].count++;if(s.due_date<map[id].oldest)map[id].oldest=s.due_date;});
 return Object.values(map).sort((a,b)=>b.amount-a.amount);
}
function v16Table(rows){
 if(!rows.length)return '<div class="empty">Bu filtrede açık vadeli satış yok.</div>';
 return `<table><tr><th>Müşteri</th><th>Satış Tarihi</th><th>Vade</th><th>Satış</th><th>Kalan</th><th>Durum</th><th></th></tr>${rows.slice().sort((a,b)=>String(a.due_date).localeCompare(String(b.due_date))).map(s=>{const st=v16Status(s);return `<tr><td>${esc(customerName(s.customer_id))}</td><td>${esc(s.sale_date||'')}</td><td><b>${esc(s.due_date||'')}</b></td><td>${money(s.total)}</td><td class="warning"><b>${money(saleOutstanding(s))}</b></td><td class="${st.cls}">${st.label}</td><td><button class="btn secondary" onclick="openCollectionForSale('${s.id}')">Tahsilat</button></td></tr>`}).join('')}</table>`;
}
function v16CustomerTable(rows){
 if(!rows.length)return '<div class="empty">Açık müşteri bakiyesi yok.</div>';
 return `<table><tr><th>Müşteri</th><th>Açık Satış</th><th>Toplam Açık</th><th>En Eski Vade</th><th></th></tr>${rows.map(x=>`<tr><td>${esc(customerName(x.id))}</td><td>${x.count}</td><td class="warning"><b>${money(x.amount)}</b></td><td>${x.oldest}</td><td><button class="btn secondary" onclick="openCollectionForCustomer('${x.id}')">Tahsilat</button></td></tr>`).join('')}</table>`;
}
function due(){
 const x=v16Summary();
 return `<section><div class="toolbar"><div><h1>Vade Takip</h1><div class="sub">Vadesi gelen, yaklaşan ve gecikmiş cari satışları tek ekranda takip et.</div></div><div class="actions" style="margin-top:0"><button class="btn primary" onclick="openCollection()">+ Tahsilat Gir</button></div></div>
 <div class="cards"><div class="card"><small>Toplam Açık Vadeli</small><div class="value warning">${money(x.rows.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div><div class="card"><small>Vadesi Geçen</small><div class="value danger">${money(x.overdueAmount)}</div></div><div class="card"><small>Bugün Vadesi Gelen</small><div class="value warning">${money(x.todayAmount)}</div></div><div class="card"><small>Önümüzdeki 7 Gün</small><div class="value">${money(x.next7Amount)}</div></div></div>
 <div class="grid"><div class="panel"><h2>Gecikmiş Alacaklar</h2>${v16Table(x.overdue)}</div><div class="panel"><h2>Bugün ve Önümüzdeki 7 Gün</h2>${v16Table([...x.todayRows,...x.next7])}</div></div>
 <div class="panel"><h2>Müşteri Bazında Vade Özeti</h2>${v16CustomerTable(v16CustomerSummary(x.rows))}</div>
 <div class="panel"><h2>Tüm Açık Vadeli Satışlar</h2>${v16Table(x.rows)}</div>
 </section>`;
}
'''
s = s.replace(marker, v16 + marker, 1)

style = r'''<style id="carbonerp-v16-due">
#carbonerp-v16-due{}
@media(max-width:600px){#app .cards .card{min-width:0}.toolbar .actions{width:100%}}
</style>
'''
if 'id="carbonerp-v16-due"' not in s:
    s=s.replace('</head>', style+'</head>', 1)

p.write_text(s,encoding='utf-8')
print('CarbonERP V16 Vade Takip applied')
