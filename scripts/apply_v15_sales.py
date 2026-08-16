from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

start = s.find('function sales(){')
end = s.find('function recentSalesTable(){', start)
if start < 0 or end < 0:
    raise SystemExit('sales function markers not found')

new_sales = r'''function sales(){
 const c0=data.customers?.[0];
 return `<section>
 <div class="toolbar"><div><h1>Satış Ekle</h1><div class="sub">Hızlı satış: müşteri seç, miktar ve fiyatı gir, sonucu anında kontrol et.</div></div><div class="actions" style="margin-top:0"><button class="btn secondary" onclick="show('sales')">Satışlar Listesi</button></div></div>
 <div class="grid">
  <div>
   <div class="panel">
    <h2>Müşteri</h2>
    <div class="formgrid">
     <div class="field" style="grid-column:1/-1"><label>Müşteri Ara</label><input id="s_customer_search" type="search" placeholder="Müşteri adı veya telefon ara..." oninput="filterSaleCustomers()"></div>
     <div class="field" style="grid-column:1/-1"><label>Müşteri</label><select id="s_customer" onchange="updateSaleCustomerInfo()">${(data.customers||[]).map(c=>`<option value="${c.id}">${esc(c.name)}${c.phone?' · '+esc(c.phone):''}</option>`).join('')}</select></div>
    </div>
    <div id="saleCustomerInfo" class="status" style="padding:12px;border:1px solid #d9e6dc;border-radius:8px;background:#f5fbf7"></div>
   </div>
   <div class="panel" style="margin-top:18px">
    <h2>Miktar ve Fiyat</h2>
    <div class="formgrid">
     <div class="field"><label>Miktar (kg)</label><div class="actions" style="justify-content:flex-start;margin:0 0 8px"><button type="button" class="btn secondary" onclick="setSaleKg(10)">10 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(25)">25 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(50)">50 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(100)">100 kg</button></div><input id="s_kg" type="number" min="0" step="0.01" value="100" oninput="previewSale()"></div>
     <div class="field"><label>Birim Fiyat (KDV hariç) TL/kg</label><input id="s_price" type="number" min="0" step="0.01" value="50" oninput="previewSale()"></div>
    </div>
    <div class="status">Mevcut stok: <b>${Number(data.stockQty||0).toLocaleString('tr-TR')} kg</b> · Ortalama maliyet: <b>${money(weightedCost())}/kg</b></div>
   </div>
  </div>
  <div>
   <div class="panel">
    <h2>Satış Bilgileri</h2>
    <div class="formgrid">
     <div class="field"><label>Tarih</label><input id="s_date" type="date" value="${today()}"></div>
     <div class="field"><label>Ürün</label><select id="s_product">${product?`<option value="${product.id}">${esc(product.name||'Mangal Kömürü')}</option>`:'<option value="">Ürün seçin</option>'}</select></div>
     <div class="field"><label>KDV Oranı (%)</label><select id="s_vat" onchange="previewSale()">${vatOptions(20)}</select></div>
     <div class="field"><label>Ödeme</label><select id="s_payment" onchange="toggleSaleDue()"><option>Peşin</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Vadeli</option></select></div>
     <div class="field" id="dueWrap" style="display:none;grid-column:1/-1"><label>Vade Tarihi</label><input id="s_due" type="date"></div>
    </div>
   </div>
   <div class="panel" style="margin-top:18px"><h2>Özet</h2><div>Net (KDV Hariç): <b id="spBase">${money(5000)}</b></div><div style="margin-top:8px">KDV: <b id="spVat">${money(1000)}</b></div><hr><div class="value" id="spTotal">${money(6000)}</div><div class="positive" id="spProfit" style="margin-top:8px"></div><div class="status">Eski bakiye: <b id="spOldBalance">${money(c0?customerBalance(c0.id):0)}</b></div><div class="status">Yeni bakiye: <b id="spNewBalance">${money(c0?customerBalance(c0.id)+6000:6000)}</b></div></div>
  </div>
 </div>
 <div class="panel" style="margin-top:18px"><div class="actions" style="justify-content:flex-start;margin-top:0"><label style="display:flex;align-items:center;gap:8px"><input id="s_make_note" type="checkbox" checked> İrsaliye oluştur</label><button class="btn secondary" onclick="clearSaleForm()">Temizle</button><button class="btn primary" onclick="saveSale()">Satışı Kaydet</button></div></div>
 <div class="panel" style="margin-top:18px"><div class="toolbar"><h2 style="margin:0">Son Satışlar</h2><span class="status">İrsaliye tek tıkla yazdırılabilir.</span></div>${recentSalesTable()}</div>
 </section>`
}
function filterSaleCustomers(){const q=(document.getElementById('s_customer_search')?.value||'').toLocaleLowerCase('tr-TR').trim();const sel=document.getElementById('s_customer');if(!sel)return;[...sel.options].forEach(o=>{o.hidden=!!q&&!o.textContent.toLocaleLowerCase('tr-TR').includes(q)});const first=[...sel.options].find(o=>!o.hidden);if(first){sel.value=first.value;updateSaleCustomerInfo()}}
function updateSaleCustomerInfo(){const el=document.getElementById('saleCustomerInfo'),sel=document.getElementById('s_customer');if(!el||!sel)return;const c=data.customers.find(x=>x.id===sel.value);if(!c){el.textContent='';return}const bal=customerBalance(c.id);el.innerHTML=`<b>${esc(c.name)}</b>${c.phone?' · '+esc(c.phone):''} · Mevcut bakiye: <b>${money(bal)}</b>`;previewSale()}
function setSaleKg(q){const el=document.getElementById('s_kg');if(el){el.value=q;previewSale()}}
function toggleSaleDue(){const p=document.getElementById('s_payment'),w=document.getElementById('dueWrap');if(w&&p)w.style.display=p.value==='Vadeli'?'block':'none'}
function clearSaleForm(){['s_customer_search','s_kg','s_price','s_due'].forEach(id=>{const e=document.getElementById(id);if(e)e.value=id==='s_kg'?'100':id==='s_price'?'50':''});const p=document.getElementById('s_payment');if(p)p.value='Peşin';toggleSaleDue();previewSale()}
'''
s = s[:start] + new_sales + s[end:]

style = r'''<style id="carbonerp-v15-sales">
.sale-fast-card{border:1px solid #d9e6dc;background:#f5fbf7;border-radius:10px;padding:12px}
#s_customer_search{font-size:16px}
@media(max-width:600px){.formgrid{grid-template-columns:1fr!important}.actions .btn{flex:1}.panel{padding:14px}}
</style>
'''
if 'id="carbonerp-v15-sales"' not in s:
    s=s.replace('</head>',style+'</head>')

p.write_text(s,encoding='utf-8')
print('V15 sales UI applied')
# CarbonERP V15 sales trigger validation