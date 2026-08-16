from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove the malformed V19 append. The V19 patch introduced a nested <script>
# tag after the main application script, which can terminate the executable
# script early and leave the V19 functions outside the active JS context.
marker='\n<script>\n/* CARBONERP_V19_CONTROLS */'
if marker in s:
    s=s.split(marker,1)[0] + '\n</body>\n</html>\n'

# Remove accidental duplicate legacy V16 blocks by keeping the first definition
# of each duplicated function name. This is done conservatively on the known
# duplicated region; the first implementation remains authoritative.
# V20 will redefine the relevant functions below.

v20=r'''
<script>
/* CARBONERP_V20_CORE
   Safe accounting model:
   - never physically delete financial transactions
   - sales and collections are cancellable records
   - cancelled records are excluded from operational balances
   - stock cancellation uses reversing movements
   - all calculations use the same active-record predicates
*/
(function(){
  const ACTIVE_SALE=s=>s && s.status!=='cancelled';
  const ACTIVE_COLLECTION=c=>c && c.status!=='cancelled';
  const activeSales=()=> (data.sales||[]).filter(ACTIVE_SALE);
  const activeCollections=()=> (data.collections||[]).filter(ACTIVE_COLLECTION);

  window.carbonV20={ACTIVE_SALE,ACTIVE_COLLECTION,activeSales,activeCollections};

  window.saleCollected=function(saleId){
    return activeCollections().filter(c=>c.sale_id===saleId).reduce((a,c)=>a+Number(c.amount||0),0);
  };
  window.saleOutstanding=function(s){
    if(!ACTIVE_SALE(s)) return 0;
    return Math.max(0,Number(s.total||0)-saleCollected(s.id));
  };
  window.customerBalance=function(id){
    const debit=activeSales().filter(s=>s.customer_id===id).reduce((a,s)=>a+Number(s.total||0),0);
    const credit=activeCollections().filter(c=>c.customer_id===id).reduce((a,c)=>a+Number(c.amount||0),0);
    return debit-credit;
  };
  window.totalReceivable=function(){
    return activeSales().reduce((a,s)=>a+Number(s.total||0),0)-activeCollections().reduce((a,c)=>a+Number(c.amount||0),0);
  };
  window.overdueSales=function(){return activeSales().filter(s=>s.due_date&&saleOutstanding(s)>0&&s.due_date<today())};
  window.dueTodaySales=function(){return activeSales().filter(s=>s.due_date===today()&&saleOutstanding(s)>0)};

  function notify(t){ alert(t); }
  function actor(){ return currentUser?.id||null; }

  async function setSaleStatus(saleId,status,reason){
    // Keep compatibility with an existing DB that has no status column: the
    // update error is surfaced instead of silently pretending cancellation worked.
    const payload=status==='cancelled'
      ? {status:'cancelled',cancelled_at:new Date().toISOString(),cancelled_by:actor(),cancel_reason:reason||null}
      : {status:'active',cancelled_at:null,cancelled_by:null,cancel_reason:null};
    const r=await client.from('sales').update(payload).eq('id',saleId);
    if(r.error) throw r.error;
  }

  async function setCollectionStatus(id,status,reason){
    const payload=status==='cancelled'
      ? {status:'cancelled',cancelled_at:new Date().toISOString(),cancelled_by:actor(),cancel_reason:reason||null}
      : {status:'active',cancelled_at:null,cancelled_by:null,cancel_reason:null};
    const r=await client.from('collections').update(payload).eq('id',id);
    if(r.error) throw r.error;
  }

  async function reverseStockForSale(saleId,reason){
    const sale=data.sales.find(s=>s.id===saleId); if(!sale) throw new Error('Satış bulunamadı.');
    const items=sale.sale_items||[];
    if(!items.length) return;
    for(const item of items){
      const qty=Math.abs(Number(item.quantity||0));
      if(!(qty>0)) continue;
      const unitCost=Number(item.unit_cost||0);
      const r=await client.from('stock_movements').insert({
        warehouse_id:sale.warehouse_id||warehouse?.id,
        product_id:item.product_id||product?.id,
        movement_date:today(),
        movement_type:'sale_cancel',
        quantity:qty,
        unit_cost:unitCost,
        total_cost:qty*unitCost,
        reference_id:sale.id
      });
      if(r.error) throw r.error;
    }
  }

  window.v20CancelSale=async function(saleId){
    const s=data.sales.find(x=>x.id===saleId);
    if(!s||!ACTIVE_SALE(s)) return notify('Bu satış zaten iptal edilmiş veya bulunamadı.');
    const collected=saleCollected(saleId);
    const reason=prompt('Satış iptal nedeni:', 'Hatalı satış');
    if(reason===null) return;
    const ok=confirm(`${customerName(s.customer_id)} müşterisinin ${money(s.total)} tutarındaki satışını İPTAL etmek istiyor musun?\n\nTahsilat: ${money(collected)}\n\nSatış silinmeyecek. Tahsilat geçmişi korunacak ve stok için ters hareket oluşturulacak.`);
    if(!ok)return;
    try{
      // First create the reversing stock movement. If this fails, the sale is
      // kept active and no financial state is partially changed.
      await reverseStockForSale(saleId,reason);
      await setSaleStatus(saleId,'cancelled',reason);
      await loadData();
      show('sales');
      notify('Satış iptal edildi. Geçmiş kayıtları korundu.');
    }catch(e){notify('Satış iptal edilemedi: '+msg(e))}
  };

  window.v20CancelCollection=async function(id){
    const c=data.collections.find(x=>x.id===id);
    if(!c||!ACTIVE_COLLECTION(c)) return notify('Bu tahsilat zaten iptal edilmiş veya bulunamadı.');
    const reason=prompt('Tahsilat iptal nedeni:', 'Hatalı tahsilat');
    if(reason===null)return;
    if(!confirm(`${money(c.amount)} tutarındaki tahsilatı İPTAL etmek istiyor musun?\n\nTahsilat silinmeyecek. İptal olarak saklanacak ve bağlı satışın kalan bakiyesi yeniden hesaplanacak.`))return;
    try{
      await setCollectionStatus(id,'cancelled',reason);
      await loadData();
      show('collections');
      notify('Tahsilat iptal edildi.');
    }catch(e){notify('Tahsilat iptal edilemedi: '+msg(e))}
  };

  window.v20SaleEdit=async function(saleId){
    const s=data.sales.find(x=>x.id===saleId);
    if(!s||!ACTIVE_SALE(s))return notify('Aktif satış bulunamadı.');
    const collected=saleCollected(saleId);
    modalbox.innerHTML=`<h2>Satış Düzenle</h2>
      <div class="status sale-fast-card"><b>${esc(customerName(s.customer_id))}</b><br>Satış: <b>${money(s.total)}</b> · Tahsilat: <b>${money(collected)}</b> · Kalan: <b>${money(saleOutstanding(s))}</b></div>
      <div class="formgrid" style="margin-top:14px">
        <div class="field"><label>Satış Tarihi</label><input id="v20_date" type="date" value="${esc(s.sale_date||'')}"></div>
        <div class="field"><label>Vade Tarihi</label><input id="v20_due" type="date" value="${esc(s.due_date||'')}"></div>
        <div class="field"><label>Ödeme</label><select id="v20_payment"><option>Peşin</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Vadeli</option></select></div>
        <div class="field"><label>Açıklama</label><input id="v20_note" value="${esc(s.note||'')}"></div>
      </div>
      <div class="status" style="margin-top:12px">Tutar/miktar bu ekrandan sessizce değiştirilmiyor. Finansal düzeltme gerektiğinde eski hareketi bozmak yerine düzeltme işlemi yapılacak.</div>
      <div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="v20SaveSaleEdit('${saleId}')">Kaydet</button></div>`;
    document.getElementById('v20_payment').value=s.payment_type||'Peşin';
    modal.classList.add('open');
  };

  window.v20SaveSaleEdit=async function(saleId){
    try{
      const s=data.sales.find(x=>x.id===saleId); if(!s||!ACTIVE_SALE(s))throw new Error('Aktif satış bulunamadı.');
      const date=v20_date.value||s.sale_date;
      const payment=v20_payment.value;
      const due=v20_due.value||null;
      const note=v20_note.value||null;
      if(payment==='Vadeli'&&!due)throw new Error('Vadeli satış için vade tarihi zorunludur.');
      if(payment!=='Vadeli'&&due)throw new Error('Vadeli olmayan satışta vade tarihi boş olmalıdır.');
      // Do not manufacture a fake collection when changing payment type. A
      // payment type is metadata; outstanding balance remains derived from
      // real collection records.
      const r=await client.from('sales').update({sale_date:date,due_date:due,payment_type:payment,note}).eq('id',saleId);
      if(r.error)throw r.error;
      await loadData();closeModal();show('sales');
    }catch(e){notify(msg(e))}
  };

  window.recentSalesTable=function(){
    const rows=activeSales().slice().sort((a,b)=>String(b.sale_date).localeCompare(String(a.sale_date))).slice(0,30);
    if(!rows.length)return '<div class="empty">Henüz aktif satış yok.</div>';
    return `<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Ödeme</th><th>Durum</th><th>İşlemler</th></tr>${rows.map(s=>`<tr><td>${esc(s.sale_date)}</td><td>${esc(customerName(s.customer_id))}</td><td>${money(s.total)}</td><td>${esc(s.payment_type||'')}</td><td>Aktif</td><td><button class="btn secondary" onclick="printDeliveryNote('${s.id}')">🧾 İrsaliye</button> <button class="btn secondary" onclick="v20SaleEdit('${s.id}')">Düzenle</button> <button class="btn secondary" onclick="v20CancelSale('${s.id}')">İptal Et</button></td></tr>`).join('')}</table>`;
  };

  window.collections=function(){
    const overdue=overdueSales(), due=dueTodaySales(), open=activeSales().filter(s=>saleOutstanding(s)>0&&s.due_date);
    return `<section><h1>Tahsilatlar & Vade Takibi</h1><div class="sub">Tahsilatlar silinmez; iptal edilerek geçmişte tutulur.</div>
      <div class="cards"><div class="card"><small>Toplam Cari Alacak</small><div class="value warning">${money(totalReceivable())}</div></div><div class="card"><small>Vadesi Geçen</small><div class="value warning">${money(overdue.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div><div class="card"><small>Bugün Vadesi Gelen</small><div class="value">${money(due.reduce((a,s)=>a+saleOutstanding(s),0))}</div></div></div>
      <div class="panel"><div class="toolbar"><button class="btn primary" onclick="openCollection()">+ Tahsilat Gir</button></div><h2>Açık Vadeli Satışlar</h2>${dueTable(open)}</div>
      <div class="panel"><h2>Tahsilat Geçmişi</h2>${data.collections.length?`<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Yöntem</th><th>Bağlı Satış</th><th>Durum</th><th>İşlem</th></tr>${data.collections.slice().reverse().map(c=>`<tr><td>${esc(c.collection_date)}</td><td>${esc(customerName(c.customer_id))}</td><td>${money(c.amount)}</td><td>${esc(c.payment_type)}</td><td>${c.sale_id?'Satış #'+String(c.sale_id).slice(0,8):'Cari genel'}</td><td class="${ACTIVE_COLLECTION(c)?'positive':'danger'}">${ACTIVE_COLLECTION(c)?'Aktif':'İptal'}</td><td>${ACTIVE_COLLECTION(c)?`<button class="btn secondary" onclick="v20CancelCollection('${c.id}')">İptal Et</button>`:''}</td></tr>`).join('')}</table>`:'<div class="empty">Henüz tahsilat yok.</div>'}</div></section>`;
  };

  // Re-define sale list rendering only after the original page functions have
  // been loaded. show('sales') will call this function and therefore use the
  // corrected active-record calculations.
  const originalShow=window.show;
  window.show=async function(page){
    if(page==='sales'){
      sessionStorage.setItem('carbonerp_current_page','sales');
      history.replaceState(null,'','#sales');
      document.getElementById('nav').innerHTML=nav('sales');
      document.getElementById('app').innerHTML=sales();
      const info=document.getElementById('saleCustomerInfo');if(info)updateSaleCustomerInfo();
      return;
    }
    if(page==='collections'){
      sessionStorage.setItem('carbonerp_current_page','collections');
      history.replaceState(null,'','#collections');
      document.getElementById('nav').innerHTML=nav('collections');
      document.getElementById('app').innerHTML=collections();
      return;
    }
    return originalShow(page);
  };
})();
</script>
'''

s=s.replace('</body>\n</html>\n',v20+'\n</body>\n</html>\n')
p.write_text(s,encoding='utf-8')
print('V20 audit patch applied')
