from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='</script>\n</body>'
if marker not in s:
    marker='</body>'
script=r'''<script id="carbonerp-v20-customer-statement">
(function(){
 const E=window.esc||((x)=>String(x??''));
 const M=window.money||((x)=>Number(x||0).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+' TL');
 const activeSale=s=>(s.status||'active')!=='cancelled';
 const activeCol=c=>(c.status||'active')!=='cancelled';
 function stats(id){
   const ss=(data.sales||[]).filter(s=>s.customer_id===id&&activeSale(s));
   const cc=(data.collections||[]).filter(c=>c.customer_id===id&&activeCol(c));
   const sales=ss.reduce((a,s)=>a+Number(s.total||0),0);
   const cols=cc.reduce((a,c)=>a+Number(c.amount||0),0);
   const overdue=ss.filter(s=>s.due_date&&s.due_date<today()&&saleOutstanding(s)>0).reduce((a,s)=>a+saleOutstanding(s),0);
   return {ss,cc,sales,cols,open:Math.max(0,sales-cols),overdue};
 }
 function statementRows(id){
   const rows=[];
   (data.sales||[]).filter(s=>s.customer_id===id).forEach(s=>{
     const cancelled=!activeSale(s), items=s.sale_items||[];
     const qty=items.reduce((a,i)=>a+Number(i.quantity||0),0);
     const collected=(data.collections||[]).filter(c=>c.sale_id===s.id&&activeCol(c)).reduce((a,c)=>a+Number(c.amount||0),0);
     rows.push({date:s.sale_date||'',time:s.created_at||'',type:cancelled?'İptal Satış':'Satış',ref:String(s.id||'').slice(0,8).toUpperCase(),desc:`${qty.toLocaleString('tr-TR')} kg · ${s.payment_type||''}${s.due_date?' · Vade '+s.due_date:''}`,debit:cancelled?0:Number(s.total||0),credit:0,status:cancelled?'İptal':'Aktif',due:s.due_date||'',collected});
   });
   (data.collections||[]).filter(c=>c.customer_id===id).forEach(c=>{
     const cancelled=!activeCol(c);
     rows.push({date:c.collection_date||'',time:c.created_at||'',type:cancelled?'İptal Tahsilat':'Tahsilat',ref:String(c.id||'').slice(0,8).toUpperCase(),desc:c.payment_type||c.description||'Tahsilat',debit:0,credit:cancelled?0:Number(c.amount||0),status:cancelled?'İptal':'Aktif',due:'',collected:0});
   });
   return rows.sort((a,b)=>{const d=String(a.date).localeCompare(String(b.date));return d||String(a.time).localeCompare(String(b.time));});
 }
 function statementHtml(id){
   const rows=statementRows(id); let balance=0;
   if(!rows.length)return '<div class="empty">Henüz cari hareket bulunmuyor.</div>';
   const body=rows.map(r=>{balance+=r.debit-r.credit;const late=r.due&&r.credit===0&&r.debit>0&&r.due<today()&&balance>0?Math.max(0,daysLate(r.due)):0;return `<tr><td>${E(r.date)}</td><td><b>${E(r.type)}</b><br><small>${E(r.ref)}</small></td><td>${E(r.desc)}</td><td>${r.debit?M(r.debit):'-'}</td><td>${r.credit?M(r.credit):'-'}</td><td class="${balance>0?'warning':'positive'}">${M(balance)}</td><td>${r.status==='İptal'?'<span class="danger">İptal</span>':(late?`<span class="danger">${late} gün gecikmiş</span>`:'-')}</td></tr>`}).join('');
   return `<div class="toolbar"><div class="status">${rows.length} hareket</div><button class="btn secondary" onclick="printCustomerStatement('${id}')">🖨️ Ekstre Yazdır</button></div><div style="overflow:auto"><table><tr><th>Tarih</th><th>İşlem</th><th>Açıklama</th><th>Borç</th><th>Alacak</th><th>Bakiye</th><th>Durum</th></tr>${body}</table></div>`;
 }
 window.customerTable=function(){
   const rows=data.customers||[]; if(!rows.length)return '<div class="empty">Henüz müşteri yok.</div>';
   return `<table><tr><th>Müşteri</th><th>Telefon</th><th>Tip</th><th>Toplam Satış</th><th>Tahsilat</th><th>Cari</th><th></th></tr>${rows.map(c=>{const st=stats(c.id);return `<tr><td><b>${E(c.name)}</b><br><small>${E(c.customer_code||'')}</small></td><td>${E(c.phone||'-')}</td><td>${E(c.customer_type||'Diğer')}</td><td>${M(st.sales)}</td><td>${M(st.cols)}</td><td class="${st.open>0?'warning':'positive'}">${M(st.open)}</td><td><button class="btn secondary" onclick="customerDetail('${c.id}')">Detay</button> <button class="btn secondary" onclick="customerEdit('${c.id}')">Düzenle</button></td></tr>`}).join('')}</table>`;
 };
 window.customerDetail=function(id){
   const c=(data.customers||[]).find(x=>x.id===id); if(!c)return alert('Müşteri bulunamadı.');
   const st=stats(id);
   modalbox.innerHTML=`<div class="toolbar"><div><h2 style="margin:0">${E(c.name)}</h2><div class="status">${E(c.customer_code||'Kod yok')} · ${E(c.customer_type||'Diğer')}</div></div><div class="actions" style="margin:0"><button class="btn secondary" onclick="customerEdit('${id}')">Düzenle</button><button class="btn secondary" onclick="openCollectionForCustomer('${id}')">Tahsilat Gir</button><button class="btn secondary" onclick="closeModal()">Kapat</button></div></div>
   <div class="cards"><div class="card"><small>Toplam Satış</small><div class="value">${M(st.sales)}</div></div><div class="card"><small>Toplam Tahsilat</small><div class="value positive">${M(st.cols)}</div></div><div class="card"><small>Güncel Cari</small><div class="value ${st.open>0?'warning':'positive'}">${M(st.open)}</div></div><div class="card"><small>Vadesi Geçmiş</small><div class="value ${st.overdue>0?'danger':'positive'}">${M(st.overdue)}</div></div></div>
   <div class="panel"><h2>Özet Bilgiler</h2><table><tr><td>Yetkili</td><td>${E(c.contact_person||'-')}</td><td>Telefon</td><td>${E(c.phone||'-')}</td></tr><tr><td>E-posta</td><td>${E(c.email||'-')}</td><td>Vergi No</td><td>${E(c.tax_number||'-')}</td></tr><tr><td>Ödeme</td><td>${E(c.default_payment_type||'-')}</td><td>Vade</td><td>${Number(c.default_due_days||0)} gün</td></tr><tr><td>Özel fiyat</td><td>${c.special_price!=null?M(c.special_price)+'/kg':'Yok'}</td><td>Kredi limiti</td><td>${M(c.credit_limit||0)}</td></tr></table></div>
   <div class="panel" style="margin-top:14px"><h2>Cari Ekstre</h2>${statementHtml(id)}</div>`;
   modal.classList.add('open');
 };
 window.printCustomerStatement=function(id){
   const c=(data.customers||[]).find(x=>x.id===id);if(!c)return;
   const st=stats(id),rows=statementRows(id);let b=0;
   const body=rows.map(r=>{b+=r.debit-r.credit;return `<tr><td>${E(r.date)}</td><td>${E(r.type)}</td><td>${E(r.desc)}</td><td>${r.debit?M(r.debit):'-'}</td><td>${r.credit?M(r.credit):'-'}</td><td>${M(b)}</td><td>${E(r.status)}</td></tr>`}).join('');
   const w=window.open('','_blank');if(!w)return;w.document.write(`<html><head><title>${E(c.name)} Cari Ekstre</title><style>@page{size:A4;margin:12mm}body{font-family:Arial;color:#111}h1{margin:0 0 4px}small{color:#666}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}.box{border:1px solid #ddd;padding:10px}.box b{display:block;font-size:16px;margin-top:5px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #ccc;padding:6px;text-align:left}th{background:#f3f3f3}</style></head><body><h1>${E(c.name)}</h1><small>${E(c.phone||'')} · ${E(c.tax_number||'')}</small><div class="summary"><div class="box">Satış<b>${M(st.sales)}</b></div><div class="box">Tahsilat<b>${M(st.cols)}</b></div><div class="box">Cari<b>${M(st.open)}</b></div><div class="box">Vadesi Geçmiş<b>${M(st.overdue)}</b></div></div><table><tr><th>Tarih</th><th>İşlem</th><th>Açıklama</th><th>Borç</th><th>Alacak</th><th>Bakiye</th><th>Durum</th></tr>${body}</table><script>window.print();</script></body></html>`);w.document.close();
 };
})();
</script>'''
if 'carbonerp-v20-customer-statement' not in s:
    s=s.replace(marker,script+'\n'+marker,1)
p.write_text(s,encoding='utf-8')
