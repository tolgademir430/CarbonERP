from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('<title>CarbonERP V19 - Satış ve Cari Kontrol</title>','<title>CarbonERP V20 - Stabil</title>')

hardening=r'''
<script>
/* CARBONERP_V20_HARDENING */
(function(){
  'use strict';
  const activeSale=s=>!!s&&s.status!=='cancelled';
  const activeCollection=c=>!!c&&c.status!=='cancelled';
  const activeSales=()=> (data.sales||[]).filter(activeSale);
  const activeCollections=()=> (data.collections||[]).filter(activeCollection);
  const qtyOf=s=>(s.sale_items||[]).reduce((a,i)=>a+Number(i.quantity||0),0);

  // Every reporting surface must use the same active-record rule.
  window.receivableAging=function(){
    const buckets=[
      {bucket:'Vadesi gelmemiş',min:0,max:Infinity,count:0,amount:0},
      {bucket:'1-7 gün gecikmiş',min:1,max:7,count:0,amount:0},
      {bucket:'8-30 gün gecikmiş',min:8,max:30,count:0,amount:0},
      {bucket:'31-60 gün gecikmiş',min:31,max:60,count:0,amount:0},
      {bucket:'61+ gün gecikmiş',min:61,max:Infinity,count:0,amount:0}
    ];
    activeSales().forEach(s=>{
      const out=saleOutstanding(s); if(out<=0)return;
      const late=s.due_date&&s.due_date<today()?daysLate(s.due_date):0;
      let b=late===0?buckets[0]:buckets.find(x=>late>=x.min&&late<=x.max);
      if(b){b.count++;b.amount+=out;}
    });
    return buckets;
  };

  window.salesTable=function(arr){
    const rows=(arr||[]).filter(activeSale);
    if(!rows.length)return '<div class="empty">Henüz aktif satış yok.</div>';
    return '<table><tr><th>Tarih</th><th>Müşteri</th><th>Tutar</th><th>Vade</th><th>Kalan</th><th>Kâr</th></tr>'+rows.map(s=>
      '<tr><td>'+esc(s.sale_date||'')+'</td><td>'+esc(customerName(s.customer_id))+'</td><td>'+money(s.total)+'</td><td>'+(s.due_date||'Peşin')+'</td><td>'+(s.due_date?money(saleOutstanding(s)):'-')+'</td><td class="positive">'+money(Number(s.subtotal||s.total)-Number(s.cost_total||0))+'</td></tr>'
    ).join('')+'</table>';
  };

  window.recentSalesTable=function(){
    const rows=activeSales().slice(-8).reverse();
    if(!rows.length)return '<div class="empty">Henüz aktif satış yok.</div>';
    return '<table><tr><th>Tarih</th><th>Müşteri</th><th>Kg</th><th>Tutar</th><th>Kalan</th><th>İşlem</th></tr>'+rows.map(s=>{
      const kg=qtyOf(s);
      return '<tr><td>'+esc(s.sale_date||'')+'</td><td>'+esc(customerName(s.customer_id))+'</td><td>'+kg.toLocaleString('tr-TR')+'</td><td>'+money(s.total)+'</td><td>'+money(saleOutstanding(s))+'</td><td><button class="btn secondary" onclick="printDeliveryNote(\''+s.id+'\')">İrsaliye</button> <button class="btn secondary" onclick="v20SaleEdit(\''+s.id+'\')">Düzenle</button> <button class="btn secondary" onclick="v20CancelSale(\''+s.id+'\')">İptal</button></td></tr>';
    }).join('')+'</table>';
  };

  window.printCustomerStatement=function(customerId){
    const c=(data.customers||[]).find(x=>x.id===customerId); if(!c)return alert('Müşteri bulunamadı');
    const rows=activeSales().filter(x=>x.customer_id===customerId).map(s=>'<tr><td>'+esc(s.sale_date||'')+'</td><td>Satış</td><td>'+esc(s.invoice_no||s.id||'')+'</td><td>'+money(s.total)+'</td><td>'+money(saleOutstanding(s))+'</td></tr>').join('');
    const total=salesActive().filter(x=>x.customer_id===customerId).reduce((a,s)=>a+saleOutstanding(s),0);
    const w=window.open('','_blank'); if(!w)return;
    w.document.write('<html><head><title>Cari Ekstre - '+esc(c.name||'')+'</title><style>body{font-family:Arial;padding:30px}table{width:100%;border-collapse:collapse;margin-top:20px}th,td{border:1px solid #ddd;padding:8px;text-align:left}.total{margin-top:20px;font-size:20px;font-weight:bold}</style></head><body><h1>CarbonERP - Cari Ekstre</h1><div><b>Müşteri:</b> '+esc(c.name||'')+'</div><table><tr><th>Tarih</th><th>İşlem</th><th>Belge</th><th>İşlem Tutarı</th><th>Kalan</th></tr>'+(rows||'<tr><td colspan="5">Kayıt yok</td></tr>')+'</table><div class="total">Toplam Açık Bakiye: '+money(total)+'</div><script>window.onload=()=>window.print()<\/script></body></html>');
    w.document.close();
  };

  // Protect report calculations from cancelled rows and multi-item sales.
  window.monthlySummary=function(){
    const map={};
    activeSales().forEach(s=>{const k=String(s.sale_date||'').slice(0,7);if(!k)return;if(!map[k])map[k]={sales:0,cost:0,kg:0};map[k].sales+=Number(s.subtotal||0);map[k].cost+=Number(s.cost_total||0);map[k].kg+=qtyOf(s)});
    return Object.keys(map).sort().slice(-6).map(k=>{const x=map[k],profit=x.sales-x.cost;return {k,sales:x.sales,cost:x.cost,kg:x.kg,profit,margin:x.sales?profit/x.sales*100:0};});
  };
})();
</script>
'''

if 'CARBONERP_V20_HARDENING' not in s:
    s=re.sub(r'\s*</body>\s*</html>\s*$', hardening+'\n</body>\n</html>\n', s, flags=re.S)

p.write_text(s,encoding='utf-8')
print('V20 hardening applied')
