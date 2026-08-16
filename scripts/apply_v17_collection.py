from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('function collectionSaleOptions(')
end=s.find('function purchases(){', start)
if start < 0 or end < 0: raise SystemExit('V17 collection markers not found')
new=r'''function collectionSaleOptions(customerId, selectedSale=null){
 const arr=data.sales.filter(s=>s.customer_id===customerId&&saleOutstanding(s)>0);
 return `<option value="">Cari genel tahsilat</option>`+arr.map(s=>`<option value="${s.id}" ${s.id===selectedSale?'selected':''}>${s.sale_date} · ${money(s.total)} · kalan ${money(saleOutstanding(s))}${s.due_date?' · vade '+s.due_date:''}</option>`).join('');
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
 hint.innerHTML=saleId?`Bu satışın kalan bakiyesi: <b>${money(max)}</b>. Tahsilat bu tutarı aşamaz.`:`Müşterinin toplam açık cari bakiyesi: <b>${money(max)}</b>.`;
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
 const sale=saleId?data.sales.find(s=>s.id===saleId):null;if(saleId&&!sale)return alert('Satış bulunamadı.');
 const max=sale?saleOutstanding(sale):collectionCustomerOpenBalance(id);if(max<=0)return alert('Bu müşteri için açık bakiye bulunmuyor.');if(a>max+0.0001)return alert('Tahsilat kalan bakiyeyi aşamaz. Maksimum: '+money(max));
 const {error}=await client.from('collections').insert({customer_id:id,sale_id:saleId,collection_date:col_date.value,payment_type:col_method.value,amount:a,created_by:currentUser.id});if(error)throw error;
 await loadData();closeModal();show('collections');
}catch(e){alert(msg(e))}}
'''
s=s[:start]+new+s[end:]
style='''<style id="carbonerp-v17-collection">.sale-fast-card{border:1px solid #d9e6dc;background:#f5fbf7;border-radius:10px;padding:12px}@media(max-width:600px){#modalbox .formgrid{grid-template-columns:1fr!important}#modalbox{padding:16px}.modalbox .actions .btn{flex:1}}</style>'''
if 'id="carbonerp-v17-collection"' not in s:s=s.replace('</head>',style+'</head>')
p.write_text(s,encoding='utf-8')
