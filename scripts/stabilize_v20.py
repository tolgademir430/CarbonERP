from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove any previous generated V20 core and malformed legacy V19 append.
s = re.sub(r'\n<script>\s*/\* CARBONERP_V20_CORE.*?</script>\s*', '\n', s, flags=re.S)
s = re.sub(r'\n<script>\s*/\* CARBONERP_V19_CONTROLS \*/.*', '\n', s, flags=re.S)

# The V16 patch was accidentally appended repeatedly. Keep the first complete
# V16 block and remove all repeated copies between v16DateOnly and customers.
start = s.find('function v16DateOnly')
end = s.find('function customers()', start + 1) if start >= 0 else -1
if start >= 0 and end > start:
    region = s[start:end]
    marker = 'function v16DateOnly'
    parts = region.split(marker)
    if len(parts) > 2:
        first_block = marker + parts[1]
        s = s[:start] + first_block + s[end:]

core = r'''
<script>
/* CARBONERP_V20_CORE */
(function(){
  'use strict';
  const activeSale=s=>!!s && s.status!=='cancelled';
  const activeCollection=c=>!!c && c.status!=='cancelled';
  const salesActive=()=> (data.sales||[]).filter(activeSale);
  const collectionsActive=()=> (data.collections||[]).filter(activeCollection);
  const errText=e=>e?.message||e?.details||String(e);
  const actor=()=>currentUser?.id||null;
  const fail=t=>alert(t);

  window.carbonV20={activeSale,activeCollection,salesActive,collectionsActive};

  window.saleCollected=function(id){
    return collectionsActive().filter(c=>c.sale_id===id).reduce((a,c)=>a+Number(c.amount||0),0);
  };
  window.saleOutstanding=function(s){
    if(!activeSale(s)) return 0;
    return Math.max(0,Number(s.total||0)-saleCollected(s.id));
  };
  window.customerBalance=function(id){
    const debit=salesActive().filter(s=>s.customer_id===id).reduce((a,s)=>a+Number(s.total||0),0);
    const credit=collectionsActive().filter(c=>c.customer_id===id).reduce((a,c)=>a+Number(c.amount||0),0);
    return debit-credit;
  };
  window.totalReceivable=function(){
    return salesActive().reduce((a,s)=>a+Number(s.total||0),0)-collectionsActive().reduce((a,c)=>a+Number(c.amount||0),0);
  };
  window.overdueSales=function(){return salesActive().filter(s=>s.due_date&&saleOutstanding(s)>0&&s.due_date<today())};
  window.dueTodaySales=function(){return salesActive().filter(s=>s.due_date===today()&&saleOutstanding(s)>0)};
  window.v16OpenSales=function(){return salesActive().filter(s=>saleOutstanding(s)>0&&s.due_date)};
  window.v16Summary=function(){
    const rows=v16OpenSales(), t=today();
    const limit=new Date(Date.now()+7*86400000).toISOString().slice(0,10);
    const overdue=rows.filter(s=>s.due_date<t), todayRows=rows.filter(s=>s.due_date===t), next7=rows.filter(s=>s.due_date>t&&s.due_date<=limit);
    return {rows,overdue,todayRows,next7,overdueAmount:overdue.reduce((a,s)=>a+saleOutstanding(s),0),todayAmount:todayRows.reduce((a,s)=>a+saleOutstanding(s),0),next7Amount:next7.reduce((a,s)=>a+saleOutstanding(s),0)};
  };
  window.v16CustomerSummary=function(rows){
    const map={};
    rows.forEach(s=>{const id=s.customer_id;if(!map[id])map[id]={id,amount:0,count:0,oldest:s.due_date};map[id].amount+=saleOutstanding(s);map[id].count++;if(String(s.due_date)<String(map[id].oldest))map[id].oldest=s.due_date;});
    return Object.values(map).sort((a,b)=>b.amount-a.amount);
  };
  window.v16Status=function(s){
    const out=saleOutstanding(s),d=s.due_date;if(out<=0)return {label:'Kapandı',cls:'positive',days:0};if(!d)return {label:'Vade yok',cls:'warning',days:0};
    const diff=Math.round((new Date(d+'T00:00:00')-new Date(today()+'T00:00:00'))/86400000);
    if(diff<0)return {label:Math.abs(diff)+' gün gecikmiş',cls:'danger',days:diff};if(diff===0)return {label:'Bugün vadesi',cls:'warning',days:0};if(diff<=7)return {label:diff+' gün kaldı',cls:'warning',days:diff};return {label:diff+' gün kaldı',cls:'positive',days:diff};
  };

  window.v20CancelSale=async function(id){
    const s=(data.sales||[]).find(x=>x.id===id); if(!s||!activeSale(s))return fail('Bu satış zaten iptal edilmiş veya bulunamadı.');
    const reason=prompt('Satış iptal nedeni:','Hatalı satış'); if(reason===null)return;
    const collected=saleCollected(id);
    if(!confirm(`${customerName(s.customer_id)} müşterisinin ${money(s.total)} tutarındaki satışını iptal etmek istiyor musun?\nTahsilat geçmişi: ${money(collected)}\nSatış silinmeyecek; stok ters hareketi oluşturulacak.`))return;
    try{
      const {error}=await client.rpc('cancel_sale',{p_sale_id:id,p_reason:reason}); if(error)throw error;
      await loadData(); show('sales'); alert('Satış iptal edildi. Geçmiş kayıtları korundu.');
    }catch(e){fail('Satış iptal edilemedi: '+errText(e))}
  };

  window.v20CancelCollection=async function(id){
    const c=(data.collections||[]).find(x=>x.id===id); if(!c||!activeCollection(c))return fail('Bu tahsilat zaten iptal edilmiş veya bulunamadı.');
    const reason=prompt('Tahsilat iptal nedeni:','Hatalı tahsilat'); if(reason===null)return;
    if(!confirm(`${money(c.amount)} tutarındaki tahsilatı iptal etmek istiyor musun?\nTahsilat silinmeyecek; iptal olarak saklanacak.`))return;
    try{
      const {error}=await client.rpc('cancel_collection',{p_collection_id:id,p_reason:reason}); if(error)throw error;
      await loadData(); show('collections'); alert('Tahsilat iptal edildi.');
    }catch(e){fail('Tahsilat iptal edilemedi: '+errText(e))}
  };

  window.v20SaleEdit=async function(id){
    const s=(data.sales||[]).find(x=>x.id===id);if(!s||!activeSale(s))return fail('Aktif satış bulunamadı.');
    modalbox.innerHTML=`<h2>Satış Düzenle</h2><div class="status sale-fast-card"><b>${esc(customerName(s.customer_id))}</b><br>Satış: ${money(s.total)} · Tahsilat: ${money(saleCollected(id))} · Kalan: ${money(saleOutstanding(s))}</div><div class="formgrid" style="margin-top:14px"><div class="field"><label>Satış Tarihi</label><input id="v20_date" type="date" value="${esc(s.sale_date||'')}"></div><div class="field"><label>Vade Tarihi</label><input id="v20_due" type="date" value="${esc(s.due_date||'')}"></div><div class="field"><label>Ödeme</label><select id="v20_payment"><option>Peşin</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Vadeli</option></select></div><div class="field"><label>Açıklama</label><input id="v20_note" value="${esc(s.notes||'')}"></div></div><div class="status">Finansal tutar/miktar burada değiştirilmiyor. Böylece mevcut stok ve tahsilat geçmişi bozulmaz.</div><div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="v20SaveSaleEdit('${id}')">Kaydet</button></div>`;
    v20_payment.value=s.payment_type||'Peşin';modal.classList.add('open');
  };
  window.v20SaveSaleEdit=async function(id){
    try{
      const s=(data.sales||[]).find(x=>x.id===id);if(!s||!activeSale(s))throw new Error('Aktif satış bulunamadı.');
      const payment=v20_payment.value, due=v20_due.value||null;if(payment==='Vadeli'&&!due)throw new Error('Vadeli satış için vade tarihi zorunludur.');if(payment!=='Vadeli'&&due)throw new Error('Vadeli olmayan satışta vade tarihi boş olmalıdır.');
      const {error}=await client.from('sales').update({sale_date:v20_date.value||s.sale_date,due_date:due,payment_type:payment,notes:v20_note.value||null,updated_at:new Date().toISOString()}).eq('id',id);if(error)throw error;
      await loadData();closeModal();show('sales');
    }catch(e){fail(errText(e))}
  };

  window.addCollection=async function(){
    try{
      const customerId=document.getElementById('col_c')?.value,amount=Number(document.getElementById('col_amount')?.value||0),saleId=document.getElementById('col_sale')?.value||null,date=document.getElementById('col_date')?.value||today(),method=document.getElementById('col_method')?.value||'Nakit';
      if(!customerId)throw new Error('Müşteri seçin.');if(!(amount>0))throw new Error('Tahsilat tutarı 0’dan büyük olmalıdır.');
      const {error}=await client.rpc('record_collection',{p_customer_id:customerId,p_amount:Number(amount.toFixed(2)),p_collection_date:date,p_payment_type:method,p_sale_id:saleId,p_notes:null});if(error)throw error;
      await loadData();closeModal();show('collections');
    }catch(e){fail(errText(e))}
  };

  window.recentSalesTable=function(){
    const rows=salesActive().slice().sort((a,b)=>String(b.sale_date).localeCompare(String(a.sale_date))).slice(0,30);if(!rows.length)return '<div class="empty">Henüz aktif satış yok.</div>';
    return `<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Ödeme</th><th>Durum</th><th>İşlem</th></tr>${rows.map(s=>`<tr><td>${esc(s.sale_date)}</td><td>${esc(customerName(s.customer_id))}</td><td>${money(s.total)}</td><td>${esc(s.payment_type||'')}</td><td class="positive">Aktif</td><td><button class="btn secondary" onclick="printDeliveryNote('${s.id}')">🧾 İrsaliye</button> <button class="btn secondary" onclick="v20SaleEdit('${s.id}')">Düzenle</button> <button class="btn secondary" onclick="v20CancelSale('${s.id}')">İptal Et</button></td></tr>`).join('')}</table>`;
  };

  window.customerTable=function(){
    const cs=data.customers||[];if(!cs.length)return '<div class="empty">Henüz müşteri yok.</div>';
    return `<table><tr><th>Müşteri</th><th>Telefon</th><th>Satış</th><th>Tahsilat</th><th>Bakiye</th><th></th></tr>${cs.map(c=>{const ss=salesActive().filter(s=>s.customer_id===c.id),cc=collectionsActive().filter(x=>x.customer_id===c.id),s=ss.reduce((a,x)=>a+Number(x.total||0),0),p=cc.reduce((a,x)=>a+Number(x.amount||0),0),b=s-p;return `<tr><td>${esc(c.name)}</td><td>${esc(c.phone||'')}</td><td>${money(s)}</td><td>${money(p)}</td><td class="${b>0?'warning':'positive'}">${money(b)}</td><td><button class="btn secondary" onclick="customerDetail('${c.id}')">Ekstre</button></td></tr>`}).join('')}</table>`;
  };
  window.customers=function(){return `<section><h1>Müşteriler</h1><div class="sub">Cari hesaplar bulutta tutuluyor.</div><div class="panel"><div class="toolbar"><button class="btn primary" onclick="openCustomer()">+ Müşteri Ekle</button></div>${customerTable()}</div></section>`};

  window.due=function(){
    const x=v16Summary();
    return `<section><div class="toolbar"><div><h1>Vade Takip</h1><div class="sub">Aktif vadeli satışları takip et.</div></div><div class="actions" style="margin-top:0"><button class="btn primary" onclick="openCollection()">+ Tahsilat Gir</button></div></div><div class="cards"><div class="card"><small>Toplam Açık Vadeli</small><div class="value warning">${money(x.rows.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div><div class="card"><small>Vadesi Geçen</small><div class="value danger">${money(x.overdueAmount)}</div></div><div class="card"><small>Bugün Vadesi Gelen</small><div class="value warning">${money(x.todayAmount)}</div></div><div class="card"><small>Önümüzdeki 7 Gün</small><div class="value">${money(x.next7Amount)}</div></div></div><div class="grid"><div class="panel"><h2>Gecikmiş Alacaklar</h2>${v16Table(x.overdue)}</div><div class="panel"><h2>Bugün ve Önümüzdeki 7 Gün</h2>${v16Table([...x.todayRows,...x.next7])}</div></div><div class="panel"><h2>Müşteri Bazında Vade Özeti</h2>${v16CustomerTable(v16CustomerSummary(x.rows))}</div><div class="panel"><h2>Tüm Açık Vadeli Satışlar</h2>${v16Table(x.rows)}</div></section>`;
  };

  window.collections=function(){
    const open=salesActive().filter(s=>saleOutstanding(s)>0&&s.due_date),overdue=overdueSales(),dueRows=dueTodaySales();
    return `<section><h1>Tahsilatlar & Vade Takibi</h1><div class="sub">Tahsilatlar silinmez; iptal edilerek geçmişte tutulur.</div><div class="cards"><div class="card"><small>Toplam Cari Alacak</small><div class="value warning">${money(totalReceivable())}</div></div><div class="card"><small>Vadesi Geçen</small><div class="value warning">${money(overdue.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div><div class="card"><small>Bugün Vadesi Gelen</small><div class="value">${money(dueRows.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div></div><div class="panel"><div class="toolbar"><button class="btn primary" onclick="openCollection()">+ Tahsilat Gir</button></div><h2>Açık Vadeli Satışlar</h2>${dueTable(open)}</div><div class="panel"><h2>Tahsilat Geçmişi</h2>${data.collections?.length?`<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Yöntem</th><th>Bağlı Satış</th><th>Durum</th><th></th></tr>${data.collections.slice().reverse().map(c=>`<tr><td>${esc(c.collection_date)}</td><td>${esc(customerName(c.customer_id))}</td><td>${money(c.amount)}</td><td>${esc(c.payment_type)}</td><td>${c.sale_id?'Satış #'+String(c.sale_id).slice(0,8):'Cari genel'}</td><td class="${activeCollection(c)?'positive':'danger'}">${activeCollection(c)?'Aktif':'İptal'}</td><td>${activeCollection(c)?`<button class="btn secondary" onclick="v20CancelCollection('${c.id}')">İptal Et</button>`:''}</td></tr>`).join('')}</table>`:'<div class="empty">Henüz tahsilat yok.</div>'}</div></section>`;
  };

  // Prevent the old login handler from doing a second load/repair pass and
  // make every unhandled UI error visible instead of silently failing.
  window.addEventListener('error',e=>console.error('CarbonERP:',e.error||e.message));
  window.addEventListener('unhandledrejection',e=>console.error('CarbonERP async:',e.reason));
})();
</script>
'''

insert = core + '\n</body>\n</html>\n'
s = re.sub(r'\s*</body>\s*</html>\s*$', '\n'+insert, s, flags=re.S)
p.write_text(s, encoding='utf-8')
print('stabilize_v20 complete')
