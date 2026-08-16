/* CarbonERP V15.1 - payment/cari preview fix */
(function(){
  function moneyLocal(n){return Number(n||0).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+' TL'}

  window.previewSale=function(){
    const q=Number(document.getElementById('s_kg')?.value||0);
    const p=Number(document.getElementById('s_price')?.value||0);
    const vr=Number(document.getElementById('s_vat')?.value||0);
    const payment=document.getElementById('s_payment')?.value||'Peşin';
    const customerId=document.getElementById('s_customer')?.value;
    const base=q*p;
    const vat=base*vr/100;
    const total=base+vat;
    const oldBalance=customerId && typeof customerBalance==='function' ? Number(customerBalance(customerId)||0) : 0;
    const newBalance=payment==='Vadeli' ? oldBalance+total : oldBalance;
    const avg=typeof weightedCost==='function' ? Number(weightedCost()||0) : 0;
    const profit=base-q*avg;

    const set=(id,text)=>{const el=document.getElementById(id);if(el)el.textContent=text};
    set('spBase',moneyLocal(base));
    set('spVat',moneyLocal(vat));
    set('spTotal',moneyLocal(total));
    set('spProfit','Brüt kâr: '+moneyLocal(profit)+' (KDV hariç)');
    set('spOldBalance',moneyLocal(oldBalance));
    set('spNewBalance',moneyLocal(newBalance));

    const due=document.getElementById('dueWrap');
    if(due) due.style.display=payment==='Vadeli'?'block':'none';
  };

  window.sales=function(){
    const c0=data.customers?.[0];
    const old=c0 && typeof customerBalance==='function' ? customerBalance(c0.id) : 0;
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
            <div class="status">Mevcut stok: <b>${Number(data.stockQty||0).toLocaleString('tr-TR')} kg</b> · Ortalama maliyet: <b>${moneyLocal(typeof weightedCost==='function'?weightedCost():0)}/kg</b></div>
          </div>
        </div>
        <div>
          <div class="panel">
            <h2>Satış Bilgileri</h2>
            <div class="formgrid">
              <div class="field"><label>Tarih</label><input id="s_date" type="date" value="${today()}"></div>
              <div class="field"><label>Ürün</label><select id="s_product">${product?`<option value="${product.id}">${esc(product.name||'Mangal Kömürü')}</option>`:'<option value="">Ürün seçin</option>'}</select></div>
              <div class="field"><label>KDV Oranı (%)</label><select id="s_vat" onchange="previewSale()">${vatOptions(20)}</select></div>
              <div class="field"><label>Ödeme</label><select id="s_payment" onchange="previewSale()"><option>Peşin</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Vadeli</option></select></div>
              <div class="field" id="dueWrap" style="display:none;grid-column:1/-1"><label>Vade Tarihi</label><input id="s_due" type="date"></div>
            </div>
          </div>
          <div class="panel" style="margin-top:18px"><h2>Özet</h2><div>Net (KDV Hariç): <b id="spBase">${moneyLocal(5000)}</b></div><div style="margin-top:8px">KDV: <b id="spVat">${moneyLocal(1000)}</b></div><hr><div class="value" id="spTotal">${moneyLocal(6000)}</div><div class="positive" id="spProfit" style="margin-top:8px"></div><div class="status">Eski bakiye: <b id="spOldBalance">${moneyLocal(old)}</b></div><div class="status">Yeni bakiye: <b id="spNewBalance">${moneyLocal(old)}</b></div></div>
        </div>
      </div>
      <div class="panel" style="margin-top:18px"><div class="actions" style="justify-content:flex-start;margin-top:0"><label style="display:flex;align-items:center;gap:8px"><input id="s_make_note" type="checkbox" checked> İrsaliye oluştur</label><button class="btn secondary" onclick="clearSaleForm()">Temizle</button><button class="btn primary" onclick="saveSale()">Satışı Kaydet</button></div></div>
      <div class="panel" style="margin-top:18px"><div class="toolbar"><h2 style="margin:0">Son Satışlar</h2><span class="status">İrsaliye tek tıkla yazdırılabilir.</span></div>${recentSalesTable()}</div>
    </section>`;
  };

  const oldUpdate=window.updateSaleCustomerInfo;
  window.updateSaleCustomerInfo=function(){
    if(typeof oldUpdate==='function') oldUpdate();
    window.previewSale();
  };

  const oldSet=window.setSaleKg;
  window.setSaleKg=function(q){
    if(typeof oldSet==='function') oldSet(q); else {const e=document.getElementById('s_kg');if(e)e.value=q;}
    window.previewSale();
  };
})();
