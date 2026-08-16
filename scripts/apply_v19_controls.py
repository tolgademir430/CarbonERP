from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '/* CARBONERP_V19_CONTROLS */'
if marker in s:
    raise SystemExit('V19 already applied')

patch = r'''
<script>
/* CARBONERP_V19_CONTROLS */
function v19SaleEdit(saleId){
  const s=data.sales.find(x=>x.id===saleId);
  if(!s)return alert('Satış bulunamadı.');
  const collected=saleCollected(saleId);
  modalbox.innerHTML=`<h2>Satış Düzenle</h2>
    <div class="status sale-fast-card" style="margin-bottom:14px"><b>${esc(customerName(s.customer_id))}</b><br>Satış tutarı: <b>${money(s.total)}</b> · Tahsilat: <b>${money(collected)}</b></div>
    <div class="formgrid">
      <div class="field"><label>Satış Tarihi</label><input id="v19_date" type="date" value="${esc(s.sale_date||'')}"></div>
      <div class="field"><label>Vade Tarihi</label><input id="v19_due" type="date" value="${esc(s.due_date||'')}"></div>
      <div class="field"><label>Ödeme</label><select id="v19_payment"><option ${s.payment_type==='Peşin'?'selected':''}>Peşin</option><option ${s.payment_type==='Havale/EFT'?'selected':''}>Havale/EFT</option><option ${s.payment_type==='Kredi Kartı'?'selected':''}>Kredi Kartı</option><option ${s.payment_type==='Vadeli'?'selected':''}>Vadeli</option></select></div>
    </div>
    <div class="status" style="margin-top:12px">V19 güvenli düzenleme: tarih, vade ve ödeme bilgileri değiştirilebilir. Miktar/fiyat değişikliği stok ve tahsilat geçmişini bozabileceği için bu sürümde ayrıca korunuyor.</div>
    <div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="saveV19SaleEdit('${saleId}')">Kaydet</button></div>`;
  modal.classList.add('open');
}
async function saveV19SaleEdit(saleId){
 try{
  const s=data.sales.find(x=>x.id===saleId); if(!s)return alert('Satış bulunamadı.');
  const newDate=v19_date.value||s.sale_date;
  const newDue=v19_due.value||null;
  const newPayment=v19_payment.value;
  const collected=saleCollected(saleId);
  if(newPayment==='Vadeli' && !newDue)return alert('Vadeli satış için vade tarihi girin.');
  if(newPayment!=='Vadeli' && newDue)return alert('Peşin/diğer ödeme türlerinde vade tarihi boş bırakılmalı.');
  if(newPayment!==s.payment_type && collected>0 && newPayment==='Vadeli')return alert('Bu satışta tahsilat bulunduğu için ödeme türü Vadeli yapılamaz. Önce ilgili tahsilatları kontrol edin.');
  if(newPayment!==s.payment_type && s.payment_type==='Vadeli' && newPayment!=='Vadeli'){
    const outstanding=Math.max(0,Number(s.total||0)-collected);
    if(outstanding>0){
      const {error}=await client.from('collections').insert({customer_id:s.customer_id,sale_id:s.id,collection_date:newDate,payment_type:newPayment,amount:Number(outstanding.toFixed(2)),created_by:currentUser.id});
      if(error)throw error;
    }
  }
  const {error}=await client.from('sales').update({sale_date:newDate,due_date:newDue,payment_type:newPayment}).eq('id',saleId);
  if(error)throw error;
  await loadData(); closeModal(); show('sales');
 }catch(e){alert(msg(e))}
}
async function v19DeleteSale(saleId){
 const s=data.sales.find(x=>x.id===saleId); if(!s)return alert('Satış bulunamadı.');
 const collected=saleCollected(saleId);
 const ok=confirm(`${customerName(s.customer_id)} müşterisinin ${money(s.total)} tutarındaki satışını silmek istediğine emin misin?\n\nBu işlem satışa bağlı tahsilatları ve stok çıkışını da geri alır.`);
 if(!ok)return;
 try{
   const {error:e1}=await client.from('collections').delete().eq('sale_id',saleId); if(e1)throw e1;
   const {error:e2}=await client.from('stock_movements').delete().eq('reference_id',saleId); if(e2)throw e2;
   const {error:e3}=await client.from('sale_items').delete().eq('sale_id',saleId); if(e3)throw e3;
   const {error:e4}=await client.from('sales').delete().eq('id',saleId); if(e4)throw e4;
   await loadData(); show('sales'); alert('Satış silindi; cari, vade ve stok yeniden hesaplandı.');
 }catch(e){alert('Satış silinemedi: '+msg(e))}
}
async function v19DeleteCollection(collectionId){
 const c=data.collections.find(x=>x.id===collectionId); if(!c)return alert('Tahsilat bulunamadı.');
 if(!confirm(`${money(c.amount)} tutarındaki tahsilatı silmek istiyor musun?\n\nBağlı satışın kalan bakiyesi yeniden açılacaktır.`))return;
 try{
   const {error}=await client.from('collections').delete().eq('id',collectionId); if(error)throw error;
   await loadData(); show('collections'); alert('Tahsilat silindi; cari ve vade yeniden hesaplandı.');
 }catch(e){alert('Tahsilat silinemedi: '+msg(e))}
}
function recentSalesTable(){
 const rows=[...(data.sales||[])].sort((a,b)=>String(b.sale_date).localeCompare(String(a.sale_date))).slice(0,20);
 if(!rows.length)return '<div class="empty">Henüz satış yok.</div>';
 return `<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Ödeme</th><th>İşlemler</th></tr>${rows.map(s=>`<tr><td>${esc(s.sale_date)}</td><td>${esc(customerName(s.customer_id))}</td><td>${money(s.total)}</td><td>${esc(s.payment_type||'')}</td><td><button class="btn secondary" onclick="printDeliveryNote('${s.id}')">🧾 İrsaliye</button> <button class="btn secondary" onclick="v19SaleEdit('${s.id}')">Düzenle</button> <button class="btn secondary" onclick="v19DeleteSale('${s.id}')">Sil</button></td></tr>`).join('')}</table>`;
}
function collections(){
 let overdue=overdueSales(),due=dueTodaySales(),open=data.sales.filter(s=>saleOutstanding(s)>0&&s.due_date);
 return `<section><h1>Tahsilatlar & Vade Takibi</h1><div class="sub">Kısmi tahsilatlar ve satış bazında kalan bakiyeler Supabase'de tutulur.</div><div class="cards"><div class="card"><small>Toplam Cari Alacak</small><div class="value warning">${money(totalReceivable())}</div></div><div class="card"><small>Vadesi Geçen</small><div class="value warning">${money(overdue.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div><div class="card"><small>Bugün Vadesi Gelen</small><div class="value">${money(due.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div></div><div class="panel"><div class="toolbar"><button class="btn primary" onclick="openCollection()">+ Tahsilat Gir</button></div><h2>Açık Vadeli Satışlar</h2>${dueTable(open)}</div><div class="panel"><h2>Tahsilat Geçmişi</h2>${data.collections.length?`<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Yöntem</th><th>Bağlı Satış</th><th>İşlem</th></tr>${data.collections.slice().reverse().map(c=>`<tr><td>${esc(c.collection_date)}</td><td>${esc(customerName(c.customer_id))}</td><td class="positive">${money(c.amount)}</td><td>${esc(c.payment_type)}</td><td>${c.sale_id?'Satış #'+String(c.sale_id).slice(0,8):'Cari genel'}</td><td><button class="btn secondary" onclick="v19DeleteCollection('${c.id}')">Sil</button></td></tr>`).join('')}</table>`:'<div class="empty">Henüz tahsilat yok.</div>'}</div></section>`;
}
</script>
'''

if '</script>\n</body>' not in s:
    raise SystemExit('script insertion point not found')
s=s.replace('</script>\n</body>', patch+'</script>\n</body>', 1)
s=s.replace('<title>CarbonERP V14 - İrsaliye ve Mobil</title>','<title>CarbonERP V19 - Satış ve Cari Kontrol</title>',1)
p.write_text(s,encoding='utf-8')
print('V19 controls applied')
