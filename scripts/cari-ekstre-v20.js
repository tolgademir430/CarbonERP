/* CARBONERP_CARI_EKSTRE_V20 */
(function(){
  'use strict';
  const activeSale=s=>!!s&&s.status!=='cancelled';
  const activeCollection=c=>!!c&&c.status!=='cancelled';
  const salesFor=id=>(data.sales||[]).filter(s=>activeSale(s)&&s.customer_id===id);
  const collectionsFor=id=>(data.collections||[]).filter(c=>activeCollection(c)&&c.customer_id===id);
  const num=v=>Number(v||0);
  const fmt=n=>typeof money==='function'?money(n):num(n).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+' TL';
  const esc2=s=>typeof esc==='function'?esc(s):String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  function statement(id,from,to){
    const rows=[];
    salesFor(id).forEach(s=>{if((!from||String(s.sale_date)>=from)&&(!to||String(s.sale_date)<=to))rows.push({date:s.sale_date,type:'Satış',ref:String(s.id).slice(0,8).toUpperCase(),desc:'Satış / İrsaliye',debit:num(s.total),credit:0,due:s.due_date||'',late:s.due_date&&s.due_date<today()&&num(s.total)-saleCollected(s.id)>0?daysLate(s.due_date):0});});
    collectionsFor(id).forEach(c=>{if((!from||String(c.collection_date)>=from)&&(!to||String(c.collection_date)<=to))rows.push({date:c.collection_date,type:'Tahsilat',ref:String(c.id).slice(0,8).toUpperCase(),desc:c.sale_id?'Satışa bağlı tahsilat':'Cari genel tahsilat',debit:0,credit:num(c.amount),due:'',late:0});});
    rows.sort((a,b)=>String(a.date).localeCompare(String(b.date))||a.type.localeCompare(b.type));
    let balance=0;rows.forEach(r=>{balance+=r.debit-r.credit;r.balance=balance;});
    return {rows,balance,totalDebit:rows.reduce((a,r)=>a+r.debit,0),totalCredit:rows.reduce((a,r)=>a+r.credit,0)};
  }
  window.customerDetail=function(id){
    const c=(data.customers||[]).find(x=>x.id===id);if(!c)return fail('Müşteri bulunamadı.');
    const ss=salesFor(id),cc=collectionsFor(id),bal=ss.reduce((a,s)=>a+num(s.total),0)-cc.reduce((a,x)=>a+num(x.amount),0);
    modalbox.innerHTML=`<div class="toolbar"><div><h2 style="margin:0">${esc2(c.name)}</h2><div class="sub">Detaylı cari ekstre</div></div><div class="actions" style="margin:0"><button class="btn secondary" onclick="editCustomer('${id}')">Düzenle</button><button class="btn secondary" onclick="printCustomerStatement('${id}')">Ekstre Yazdır</button></div></div><div class="cards"><div class="card"><small>Toplam Satış</small><div class="value">${fmt(ss.reduce((a,s)=>a+num(s.total),0))}</div></div><div class="card"><small>Toplam Tahsilat</small><div class="value positive">${fmt(cc.reduce((a,x)=>a+num(x.amount),0))}</div></div><div class="card"><small>Güncel Cari</small><div class="value ${bal>0?'warning':'positive'}">${fmt(bal)}</div></div><div class="card"><small>Vadesi Geçmiş</small><div class="value danger">${fmt(ss.filter(s=>s.due_date&&s.due_date<today()).reduce((a,s)=>a+Math.max(0,num(s.total)-saleCollected(s.id)),0))}</div></div></div><div class="panel"><h3>Ekstre Filtresi</h3><div class="formgrid"><div class="field"><label>Başlangıç</label><input id="stmt_from" type="date"></div><div class="field"><label>Bitiş</label><input id="stmt_to" type="date"></div></div><div class="actions"><button class="btn secondary" onclick="renderCustomerStatement('${id}')">Filtrele</button></div></div><div id="customerStatementBody"></div>`;
    modal.classList.add('open');renderCustomerStatement(id);
  };
  window.renderCustomerStatement=function(id){
    const body=document.getElementById('customerStatementBody');if(!body)return;
    const x=statement(id,document.getElementById('stmt_from')?.value||'',document.getElementById('stmt_to')?.value||'');
    body.innerHTML=`<div class="panel"><div class="toolbar"><h3 style="margin:0">Cari Hareketleri</h3><span class="status">Borç: <b>${fmt(x.totalDebit)}</b> · Alacak: <b>${fmt(x.totalCredit)}</b> · Bakiye: <b>${fmt(x.balance)}</b></span></div>${x.rows.length?`<div style="overflow:auto"><table><tr><th>Tarih</th><th>İşlem</th><th>No</th><th>Açıklama</th><th>Vade</th><th>Gecikme</th><th>Borç</th><th>Alacak</th><th>Bakiye</th></tr>${x.rows.map(r=>`<tr><td>${esc2(r.date)}</td><td>${esc2(r.type)}</td><td>${esc2(r.ref)}</td><td>${esc2(r.desc)}</td><td>${esc2(r.due||'-')}</td><td>${r.late?r.late+' gün':'-'}</td><td>${r.debit?fmt(r.debit):'-'}</td><td>${r.credit?fmt(r.credit):'-'}</td><td class="${r.balance>0?'warning':'positive'}">${fmt(r.balance)}</td></tr>`).join('')}</table></div>`:'<div class="empty">Seçilen dönemde hareket yok.</div>'}</div>`;
  };
  window.printCustomerStatement=function(id){
    const c=(data.customers||[]).find(x=>x.id===id);if(!c)return;
    const x=statement(id,document.getElementById('stmt_from')?.value||'',document.getElementById('stmt_to')?.value||'');
    const w=window.open('','_blank');if(!w)return;
    const printScript='<scr'+'ipt>window.print();</scr'+'ipt>';
    const html=`<html><head><title>Cari Ekstre - ${esc2(c.name)}</title><style>body{font-family:Arial,sans-serif;padding:24px;color:#111}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #ccc;padding:7px;text-align:left}th{background:#f3f3f3}.summary{display:flex;gap:25px;margin:18px 0;font-weight:bold}</style></head><body><h1>CARİ EKSTRE</h1><p><b>${esc2(c.name)}</b> · ${esc2(c.phone||'')} · ${esc2(c.tax_number||'')}</p><div class="summary"><span>Borç: ${fmt(x.totalDebit)}</span><span>Alacak: ${fmt(x.totalCredit)}</span><span>Bakiye: ${fmt(x.balance)}</span></div><table><tr><th>Tarih</th><th>İşlem</th><th>No</th><th>Açıklama</th><th>Vade</th><th>Gecikme</th><th>Borç</th><th>Alacak</th><th>Bakiye</th></tr>${x.rows.map(r=>`<tr><td>${esc2(r.date)}</td><td>${esc2(r.type)}</td><td>${esc2(r.ref)}</td><td>${esc2(r.desc)}</td><td>${esc2(r.due||'-')}</td><td>${r.late?r.late+' gün':'-'}</td><td>${r.debit?fmt(r.debit):'-'}</td><td>${r.credit?fmt(r.credit):'-'}</td><td>${fmt(r.balance)}</td></tr>`).join('')}</table>${printScript}</body></html>`;
    w.document.write(html);w.document.close();
  };
})();
