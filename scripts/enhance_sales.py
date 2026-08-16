from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

start = s.find('function sales(){')
end = s.find('function recentSalesTable(){', start)
if start < 0 or end < 0:
    raise SystemExit('sales function markers not found')

new_sales = r'''function sales(){return `<section><h1>Yeni Satış</h1><div class="sub">Hızlı satış: müşteri ara, kg seç, fiyat/KDV gir ve tek ekrandan kaydet.</div><div class="grid"><div class="panel"><div class="formgrid"><div class="field"><label>Müşteri Ara</label><input id="s_customer_search" type="search" placeholder="Müşteri adı yazın..." oninput="filterSaleCustomers()"></div><div class="field"><label>Müşteri</label><select id="s_customer" onchange="updateSaleCustomerInfo()">${data.customers.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join('')}</select></div><div class="field"><label>Tarih</label><input id="s_date" type="date" value="${today()}"></div><div class="field"><label>Miktar (kg)</label><input id="s_kg" type="number" min="0" value="100" oninput="previewSale()"></div><div class="field" style="grid-column:1/-1"><label>Hızlı Kg</label><div class="actions" style="justify-content:flex-start;margin-top:0"><button type="button" class="btn secondary" onclick="setSaleKg(10)">10 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(25)">25 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(50)">50 kg</button><button type="button" class="btn secondary" onclick="setSaleKg(100)">100 kg</button></div></div><div class="field"><label>Satış Fiyatı (KDV hariç) TL/kg</label><input id="s_price" type="number" min="0" step=".01" value="50" oninput="previewSale()"></div><div class="field"><label>KDV Oranı</label><select id="s_vat" onchange="previewSale()">${vatOptions(20)}</select></div><div class="field"><label>Ödeme</label><select id="s_payment" onchange="document.getElementById('dueWrap').style.display=this.value==='Vadeli'?'block':'none'"><option>Peşin</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Vadeli</option></select></div><div class="field" id="dueWrap" style="display:none"><label>Vade Tarihi</label><input id="s_due" type="date"></div></div><div id="saleCustomerInfo" class="status" style="margin-top:12px"></div><div class="actions"><button class="btn primary" onclick="saveSale()">Satışı Kaydet</button></div></div><div class="panel"><h2>Kâr Önizleme</h2><div>Ortalama maliyet: <b>${money(weightedCost())}/kg</b></div><div>Mal bedeli (KDV hariç): <b id="spBase">${money(5000)}</b></div><div>Hesaplanan KDV: <b id="spVat">${money(1000)}</b></div><div class="value" id="spTotal">${money(6000)}</div><div class="positive" id="spProfit"></div><div class="status">KDV kâr hesabına dahil edilmez; cari satış toplamı KDV dahil tutardır.</div></div></div><div class="panel" style="margin-top:18px"><div class="toolbar"><h2 style="margin:0">Son Satışlar</h2><span class="status">İrsaliye tek tıkla yazdırılabilir.</span></div>${recentSalesTable()}</div></section>`}
function filterSaleCustomers(){const q=(document.getElementById('s_customer_search')?.value||'').toLocaleLowerCase('tr-TR').trim();const sel=document.getElementById('s_customer');if(!sel)return;[...sel.options].forEach(o=>{o.hidden=!!q&&!o.textContent.toLocaleLowerCase('tr-TR').includes(q)});const first=[...sel.options].find(o=>!o.hidden);if(first){sel.value=first.value;updateSaleCustomerInfo()}}
function updateSaleCustomerInfo(){const el=document.getElementById('saleCustomerInfo'),sel=document.getElementById('s_customer');if(!el||!sel)return;const c=data.customers.find(x=>x.id===sel.value);if(!c){el.textContent='';return}el.textContent=`${c.name} · Mevcut cari bakiye: ${money(customerBalance(c.id))}`}
function setSaleKg(q){const el=document.getElementById('s_kg');if(el){el.value=q;previewSale()}}
'''
s = s[:start] + new_sales + s[end:]

# Add a small style for quick-sale controls once.
style = '''\n<style id="carbonerp-sales-v15">\n.quick-sale-hint{padding:10px;border:1px dashed #cfd4d9;border-radius:8px;background:#fafbfc}\n</style>\n'''
if 'id="carbonerp-sales-v15"' not in s:
    s = s.replace('</head>', style + '</head>')

p.write_text(s, encoding='utf-8')
print('sales screen enhanced')
