from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '/* CARBONERP_V20_CUSTOMER_MANAGEMENT */'
if marker in s:
    raise SystemExit('Customer management block already present; refusing duplicate injection.')

block = r'''<script>
/* CARBONERP_V20_CUSTOMER_MANAGEMENT */
(function(){
  'use strict';
  const activeSale = s => !!s && s.status !== 'cancelled';
  const activeCollection = c => !!c && c.status !== 'cancelled';
  const escC = s => String(s ?? '').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const cust = id => (data.customers||[]).find(c=>c.id===id);
  const salePaid = id => (data.collections||[]).filter(c=>activeCollection(c)&&c.sale_id===id).reduce((a,c)=>a+Number(c.amount||0),0);
  const saleRemain = s => activeSale(s) ? Math.max(0,Number(s.total||0)-salePaid(s.id)) : 0;
  const salesFor = id => (data.sales||[]).filter(s=>activeSale(s)&&s.customer_id===id);
  const collectionsFor = id => (data.collections||[]).filter(c=>activeCollection(c)&&c.customer_id===id);
  const fmtDate = d => d ? new Date(d).toLocaleDateString('tr-TR') : '-';
  const total = (arr,key) => arr.reduce((a,x)=>a+Number(x[key]||0),0);

  window.openCustomer = function(editId=null){
    const c = editId ? cust(editId) : null;
    modalbox.innerHTML = `<h2>${c?'Müşteri Düzenle':'Yeni Müşteri'}</h2>
      <div class="formgrid">
        <div class="field"><label>Ad / Firma Ünvanı *</label><input id="cm_name" value="${escC(c?.name||'')}"></div>
        <div class="field"><label>Telefon</label><input id="cm_phone" value="${escC(c?.phone||'')}"></div>
        <div class="field"><label>E-posta</label><input id="cm_email" type="email" value="${escC(c?.email||'')}"></div>
        <div class="field"><label>Vergi No</label><input id="cm_tax" value="${escC(c?.tax_number||'')}"></div>
        <div class="field"><label>Vergi Dairesi</label><input id="cm_tax_office" value="${escC(c?.tax_office||'')}"></div>
        <div class="field"><label>Varsayılan Ödeme</label><select id="cm_payment">
          ${['Peşin','Havale/EFT','Kredi Kartı','Vadeli'].map(x=>`<option ${x===(c?.default_payment_type||'Peşin')?'selected':''}>${x}</option>`).join('')}
        </select></div>
        <div class="field"><label>Varsayılan Vade (gün)</label><input id="cm_due_days" type="number" min="0" step="1" value="${Number(c?.default_due_days||0)}"></div>
        <div class="field" style="grid-column:1/-1"><label>Adres</label><textarea id="cm_address" rows="3" style="width:100%;padding:11px;border:1px solid #cfd4d9;border-radius:8px">${escC(c?.address||'')}</textarea></div>
        <div class="field" style="grid-column:1/-1"><label>Notlar</label><textarea id="cm_notes" rows="3" style="width:100%;padding:11px;border:1px solid #cfd4d9;border-radius:8px">${escC(c?.notes||'')}</textarea></div>
      </div>
      <div class="status">${c?'Müşteri bilgileri güncellenebilir. Cari hareketler ve geçmiş satışlar korunur.':'Müşteri kaydedildikten sonra tüm bilgilerini bu ekrandan tekrar düzenleyebilirsin.'}</div>
      <div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="saveCustomer('${editId||''}')">${c?'Değişiklikleri Kaydet':'Müşteriyi Kaydet'}</button></div>`;
    modal.classList.add('open');
  };

  window.saveCustomer = async function(id){
    try{
      const name = document.getElementById('cm_name')?.value.trim();
      if(!name) throw new Error('Müşteri adı / firma ünvanı zorunludur.');
      const dueDaysRaw = document.getElementById('cm_due_days')?.value;
      const dueDays = dueDaysRaw==='' ? null : Number(dueDaysRaw);
      if(dueDays!==null && (!Number.isInteger(dueDays)||dueDays<0)) throw new Error('Varsayılan vade günü 0 veya daha büyük tam sayı olmalıdır.');
      const payload={
        name,
        phone:document.getElementById('cm_phone')?.value.trim()||null,
        email:document.getElementById('cm_email')?.value.trim()||null,
        address:document.getElementById('cm_address')?.value.trim()||null,
        tax_number:document.getElementById('cm_tax')?.value.trim()||null,
        tax_office:document.getElementById('cm_tax_office')?.value.trim()||null,
        default_payment_type:document.getElementById('cm_payment')?.value||null,
        default_due_days:dueDays,
        notes:document.getElementById('cm_notes')?.value.trim()||null,
        updated_at:new Date().toISOString()
      };
      let error;
      if(id){({error}=await client.from('customers').update(payload).eq('id',id));}
      else {({error}=await client.from('customers').insert({...payload,is_active:true}));}
      if(error) throw error;
      await loadData(); closeModal(); show('customers');
    }catch(e){alert(e?.message||String(e));}
  };

  window.customerDetail = function(id){
    const c=cust(id); if(!c){alert('Müşteri bulunamadı.');return;}
    const ss=salesFor(id), cc=collectionsFor(id);
    const salesTotal=total(ss,'total'), collectionTotal=total(cc,'amount'), balance=salesTotal-collectionTotal;
    const overdue=ss.filter(s=>saleRemain(s)>0&&s.due_date&&s.due_date<today()).reduce((a,s)=>a+saleRemain(s),0);
    const recent=[
      ...ss.map(s=>({date:s.sale_date,type:'Satış',detail:`${money(s.total)} · ${s.payment_type||''}${s.due_date?' · Vade '+s.due_date:''}`,amount:Number(s.total||0),ref:s.id})),
      ...cc.map(x=>({date:x.collection_date,type:'Tahsilat',detail:x.payment_type||'',amount:-Number(x.amount||0),ref:x.id}))
    ].sort((a,b)=>String(b.date).localeCompare(String(a.date))).slice(0,30);
    const recentHtml=recent.length ? `<table><tr><th>Tarih</th><th>İşlem</th><th>Açıklama</th><th>Tutar</th></tr>${recent.map(x=>`<tr><td>${escC(x.date)}</td><td>${x.type}</td><td>${escC(x.detail)}</td><td class="${x.amount>=0?'':'positive'}">${money(Math.abs(x.amount))}</td></tr>`).join('')}</table>` : '<div class="empty">Henüz hareket yok.</div>';
    const openSales=ss.filter(s=>saleRemain(s)>0).sort((a,b)=>String(a.due_date||'9999').localeCompare(String(b.due_date||'9999')));
    const openHtml=openSales.length ? `<table><tr><th>Tarih</th><th>Vade</th><th>Satış</th><th>Kalan</th><th></th></tr>${openSales.map(s=>`<tr><td>${escC(s.sale_date)}</td><td>${escC(s.due_date||'Peşin')}</td><td>${money(s.total)}</td><td class="warning">${money(saleRemain(s))}</td><td><button class="btn secondary" onclick="openCollectionForSale('${s.id}')">Tahsilat</button></td></tr>`).join('')}</table>` : '<div class="empty">Açık satış yok.</div>';
    modalbox.innerHTML=`<div class="toolbar"><div><h2 style="margin:0">${escC(c.name)}</h2><div class="status">Müşteri kartı · oluşturulma: ${fmtDate(c.created_at)}</div></div><div class="actions" style="margin:0"><button class="btn secondary" onclick="openCustomer('${c.id}')">✏️ Düzenle</button><button class="btn secondary" onclick="printCustomerStatement('${c.id}')">🖨️ Ekstre</button></div></div>
      <div class="cards">
        <div class="card"><small>Toplam Satış</small><div class="value">${money(salesTotal)}</div></div>
        <div class="card"><small>Toplam Tahsilat</small><div class="value positive">${money(collectionTotal)}</div></div>
        <div class="card"><small>Açık Bakiye</small><div class="value ${balance>0?'warning':'positive'}">${money(balance)}</div></div>
        <div class="card"><small>Vadesi Geçen</small><div class="value ${overdue>0?'danger':'positive'}">${money(overdue)}</div></div>
      </div>
      <div class="panel"><h2>İletişim ve Ticari Bilgiler</h2><div class="formgrid">
        <div><b>Telefon</b><br>${escC(c.phone||'-')}</div><div><b>E-posta</b><br>${escC(c.email||'-')}</div>
        <div><b>Vergi No</b><br>${escC(c.tax_number||'-')}</div><div><b>Vergi Dairesi</b><br>${escC(c.tax_office||'-')}</div>
        <div><b>Varsayılan Ödeme</b><br>${escC(c.default_payment_type||'-')}</div><div><b>Varsayılan Vade</b><br>${c.default_due_days!=null?c.default_due_days+' gün':'-'}</div>
        <div style="grid-column:1/-1"><b>Adres</b><br>${escC(c.address||'-')}</div>
        <div style="grid-column:1/-1"><b>Notlar</b><br>${escC(c.notes||'-')}</div>
      </div></div>
      <div class="panel" style="margin-top:14px"><h2>Açık Satışlar</h2>${openHtml}</div>
      <div class="panel" style="margin-top:14px"><h2>Son Hareketler</h2>${recentHtml}</div>
      <div class="actions"><button class="btn secondary" onclick="openCollectionForCustomer('${c.id}')">+ Tahsilat Gir</button><button class="btn primary" onclick="closeModal()">Kapat</button></div>`;
    modal.classList.add('open');
  };

  window.customers = function(){
    return `<section><div class="toolbar"><div><h1>Müşteriler</h1><div class="sub">Müşteri kartı, iletişim bilgileri, cari hareketler ve açık bakiyeyi buradan yönet.</div></div><div class="actions" style="margin:0"><button class="btn primary" onclick="openCustomer()">+ Müşteri Ekle</button></div></div><div class="panel">${customerTable()}</div></section>`;
  };

  window.customerTable = function(){
    const cs=data.customers||[]; if(!cs.length)return '<div class="empty">Henüz müşteri yok.</div>';
    return `<table><tr><th>Müşteri</th><th>Telefon</th><th>E-posta</th><th>Satış</th><th>Tahsilat</th><th>Bakiye</th><th>İşlem</th></tr>${cs.map(c=>{
      const ss=salesFor(c.id),cc=collectionsFor(c.id),s=total(ss,'total'),p=total(cc,'amount'),b=s-p;
      return `<tr><td><b>${escC(c.name)}</b></td><td>${escC(c.phone||'-')}</td><td>${escC(c.email||'-')}</td><td>${money(s)}</td><td>${money(p)}</td><td class="${b>0?'warning':'positive'}">${money(b)}</td><td><button class="btn secondary" onclick="customerDetail('${c.id}')">Detay</button> <button class="btn secondary" onclick="openCustomer('${c.id}')">Düzenle</button></td></tr>`;
    }).join('')}</table>`;
  };
})();
</script>
'''

idx = s.lower().rfind('</body>')
if idx < 0:
    raise SystemExit('Cannot find closing body tag.')
s = s[:idx] + block + s[idx:]
p.write_text(s, encoding='utf-8')
print('Injected V20 customer management block.')
