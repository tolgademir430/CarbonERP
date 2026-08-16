# V17 FIFO collection patch
from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('function collectionSaleOptions(')
end=s.find('function purchases(){', start)
if start < 0 or end < 0: raise SystemExit('V17 collection markers not found')
new=r'''async function repairLegacyGeneralCollections(){
 const legacy=data.collections.filter(c=>!c.sale_id&&Number(c.amount||0)>0);
 let changed=false;
 for(const c of legacy){
   let remaining=Number(c.amount||0);
   const openSales=data.sales.filter(s=>s.customer_id===c.customer_id&&saleOutstanding(s)>0).sort((a,b)=>{
     const ad=a.due_date||'9999-12-31',bd=b.due_date||'9999-12-31';
     return ad.localeCompare(bd)||String(a.sale_date||'').localeCompare(String(b.sale_date||''));
   });
   for(let i=0;i<openSales.length&&remaining>0.0001;i++){
     const sale=openSales[i],allocation=Math.min(remaining,saleOutstanding(sale));
     if(allocation<=0)continue;
     if(i===0){
       const {error}=await client.from('collections').update({sale_id:sale.id,amount:Number(allocation.toFixed(2))}).eq('id',c.id);
       if(error)throw error;
     }else{
       const {error}=await client.from('collections').insert({customer_id:c.customer_id,sale_id:sale.id,collection_date:c.collection_date,payment_type:c.payment_type,amount:Number(allocation.toFixed(2)),created_by:c.created_by});
       if(error)throw error;
     }
     remaining-=allocation;changed=true;
   }
 }
 return changed;
}
function collectionSaleOptions(customerId, selectedSale=null){
 const arr=data.sales.filter(s=>s.customer_id===customerId&&saleOutstanding(s)>0);
 return `<option value="">Cari genel tahsilat (otomatik dağıt)</option>`+arr.map(s=>`<option value="${s.id}" ${s.id===selectedSale?'selected':''}>${s.sale_date} · ${money(s.total)} · kalan ${money(saleOutstanding(s))}${s.due_date?' · vade '+s.due_date:''}</option>`).join('');
}
function collectionCustomerOpenBalance(customerId){return Math.max(0,customerBalance(customerId));}
function updateCollectionHint(){
 const id=document.getElementById('col_c')?.value;
 const saleId=document.getElementById('col_sale')?.value||'';
 const hint=document.getElementById('col_hint');
 const amount=document.getElementById('col_amount');
 if(!hint)return;
 const max=saleId?saleOutstanding(data.sales.find(s=>s.id===saleId)):collectionCustomerOpenBalance(id);
 if(amount){amount.max=max.toFixed(2);if(Number(amount.value)>max)amount.value=max.toFixed(2);}
 hint.innerHTML=saleId?`Bu satışın kalan bakiyesi: <b>${money(max)}</b>. Tahsilat bu tutarı aşamaz.`:`Genel tahsilat, en eski açık satıştan başlayarak otomatik dağıtılır. Açık cari: <b>${money(max)}</b>.`;
}
function openCollection(){const cid=data.customers[0]?.id||'';openCollectionForCustomer(cid)}
function openCollectionForCustomer(cid, selectedSale=null){
 const balance=collectionCustomerOpenBalance(cid);
 modalbox.innerHTML=`<h2>V17 — Tahsilat Gir</h2><div class="status sale-fast-card" style="margin-bottom:14px"><b>${esc(customerName(cid))}</b><br>Toplam açık cari: <b class="warning">${money(balance)}</b></div>
 <div class="formgrid"><div class="field"><label>Müşteri</label><select id="col_c" onchange="refreshCollectionSales()">${data.customers.map(c=>`<option value="${c.id}" ${c.id===cid?'selected':''}>${esc(c.name)}</option>`).join('')}</select></div>
 <div class="field"><label>Satış / Vade</label><select id="col_sale" onchange="updateCollectionHint()">${collectionSaleOptions(cid,selectedSale)}</select></div>
 <div class="field"><label>Tarih</label><input id="col_date" type="date" value="${today()}"></div>
 <div class="field"><label>Tahsilat Tutarı</label><input id="col_amount" type="number" min="0" step=".01" oninput="updateCollectionHint()"></div>
 <div class="field"><label>Ödeme Yöntemi</label><select id="col_method"><option>Nakit</option><option>Havale/EFT</option><option>Kredi Kartı</option><option>Diğer</option></select></div></div>
 <div id="col_hint" class="status"></div><div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="addCollection()">Tahsilatı Kaydet</button></div>`;
 modal.classList.add('open');updateCollectionHint();
}
function refreshCollectionSales(){const c=col_c.value;document.getElementById('col_sale').innerHTML=collectionSaleOptions(c);document.getElementById('col_amount').value='';updateCollectionHint()}
function openCollectionForSale(saleId){const s=data.sales.find(x=>x.id===saleId);if(s)openCollectionForCustomer(s.customer_id,saleId)}
async function addCollection(){try{
 const id=col_c.value,a=+col_amount.value,saleId=col_sale.value||null;if(!(a>0))return alert('Tahsilat tutarı girin.');
 if(!id)return alert('Müşteri seçin.');
 const collectionDate=col_date.value,paymentType=col_method.value;
 if(saleId){
   const sale=data.sales.find(s=>s.id===saleId);if(!sale)return alert('Satış bulunamadı.');
   const max=saleOutstanding(sale);if(max<=0)return alert('Bu satışta açık bakiye bulunmuyor.');
   if(a>max+0.0001)return alert('Tahsilat kalan bakiyeyi aşamaz. Maksimum: '+money(max));
   const {error}=await client.from('collections').insert({customer_id:id,sale_id:saleId,collection_date:collectionDate,payment_type:paymentType,amount:Number(a.toFixed(2)),created_by:currentUser.id});
   if(error)throw error;
 }else{
   const openSales=data.sales.filter(s=>s.customer_id===id&&saleOutstanding(s)>0).sort((a,b)=>{
     const ad=a.due_date||'9999-12-31',bd=b.due_date||'9999-12-31';
     return ad.localeCompare(bd)||String(a.sale_date||'').localeCompare(String(b.sale_date||''));
   });
   const totalOpen=openSales.reduce((sum,s)=>sum+saleOutstanding(s),0);
   if(totalOpen<=0)return alert('Bu müşteri için açık bakiye bulunmuyor.');
   if(a>totalOpen+0.0001)return alert('Tahsilat toplam açık bakiyeyi aşamaz. Maksimum: '+money(totalOpen));
   let remaining=a;
   for(const sale of openSales){
     if(remaining<=0.0001)break;
     const allocation=Math.min(remaining,saleOutstanding(sale));if(allocation<=0)continue;
     const {error}=await client.from('collections').insert({customer_id:id,sale_id:sale.id,collection_date:collectionDate,payment_type:paymentType,amount:Number(allocation.toFixed(2)),created_by:currentUser.id});
     if(error)throw error;remaining-=allocation;
   }
   if(remaining>0.01)throw new Error('Tahsilat açık satışlara tam olarak dağıtılamadı.');
 }
 await loadData();closeModal();show('collections');
}catch(e){alert(msg(e))}}
'''
s=s[:start]+new+s[end:]
# Repair the pre-V17 "Cari genel" record once after login. Repaired records get sale_id,
# so subsequent logins skip them. Then reload data so Vade Takibi immediately reflects the fix.
needle="await loadData();show('dashboard')"
replacement="await loadData();await repairLegacyGeneralCollections();await loadData();show('dashboard')"
if needle in s:
    s=s.replace(needle,replacement,1)
else:
    raise SystemExit('login loadData marker not found')
style='''<style id="carbonerp-v17-collection">.sale-fast-card{border:1px solid #d9e6dc;background:#f5fbf7;border-radius:10px;padding:12px}@media(max-width:600px){#modalbox .formgrid{grid-template-columns:1fr!important}#modalbox{padding:16px}.modalbox .actions .btn{flex:1}}</style>'''
if 'id="carbonerp-v17-collection"' not in s:s=s.replace('</head>',style+'</head>')
p.write_text(s,encoding='utf-8')
