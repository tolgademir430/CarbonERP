from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='</script>\n</body>'
if marker not in s:
    marker='</body>'
script=r'''<script id="carbonerp-v20-customer-profile">
(function(){
 const escC=window.esc||((x)=>String(x??''));
 const field=(id,label,value='',type='text')=>`<div class="field"><label>${label}</label><input id="${id}" type="${type}" value="${escC(value)}"></div>`;
 const select=(id,label,value,opts)=>`<div class="field"><label>${label}</label><select id="${id}">${opts.map(x=>`<option value="${escC(x)}" ${String(value||'')===String(x)?'selected':''}>${escC(x)}</option>`).join('')}</select></div>`;
 function customerStats(id){
   const ss=(data.sales||[]).filter(s=>(s.status||'active')!=='cancelled'&&s.customer_id===id);
   const cc=(data.collections||[]).filter(c=>(c.status||'active')!=='cancelled'&&c.customer_id===id);
   const sales=ss.reduce((a,s)=>a+Number(s.total||0),0), collections=cc.reduce((a,c)=>a+Number(c.amount||0),0);
   const open=Math.max(0,sales-collections);
   const overdue=ss.filter(s=>s.due_date&&s.due_date<today()&&saleOutstanding(s)>0).reduce((a,s)=>a+saleOutstanding(s),0);
   return {ss,cc,sales,collections,open,overdue};
 }
 window.customerDetail=function(id){
   const c=(data.customers||[]).find(x=>x.id===id); if(!c)return alert('Müşteri bulunamadı.');
   const st=customerStats(id);
   modalbox.innerHTML=`<div class="toolbar"><div><h2 style="margin:0">${escC(c.name)}</h2><div class="status">${escC(c.customer_code||'Kod yok')} · ${escC(c.customer_type||'Diğer')}</div></div><div class="actions" style="margin:0"><button class="btn secondary" onclick="customerEdit('${id}')">Düzenle</button><button class="btn secondary" onclick="closeModal()">Kapat</button></div></div>
   <div class="cards"><div class="card"><small>Toplam Satış</small><div class="value">${money(st.sales)}</div></div><div class="card"><small>Toplam Tahsilat</small><div class="value positive">${money(st.collections)}</div></div><div class="card"><small>Güncel Cari</small><div class="value ${st.open>0?'warning':'positive'}">${money(st.open)}</div></div><div class="card"><small>Vadesi Geçmiş</small><div class="value ${st.overdue>0?'danger':'positive'}">${money(st.overdue)}</div></div></div>
   <div class="panel"><h2>İletişim</h2><table><tr><td>Yetkili</td><td>${escC(c.contact_person||'-')}</td><td>Telefon</td><td>${escC(c.phone||'-')}</td></tr><tr><td>Alternatif</td><td>${escC(c.alternate_phone||'-')}</td><td>WhatsApp</td><td>${escC(c.whatsapp||'-')}</td></tr><tr><td>E-posta</td><td>${escC(c.email||'-')}</td><td>Tercih</td><td>${escC(c.contact_preference||'-')}</td></tr></table></div>
   <div class="panel" style="margin-top:14px"><h2>Fatura / Vergi</h2><table><tr><td>Fatura unvanı</td><td>${escC(c.invoice_title||c.name||'-')}</td><td>Vergi No</td><td>${escC(c.tax_number||'-')}</td></tr><tr><td>Vergi Dairesi</td><td>${escC(c.tax_office||'-')}</td><td>E-Fatura</td><td>${escC(c.e_invoice_type||'-')}</td></tr><tr><td>Fatura adresi</td><td colspan="3">${escC(c.invoice_address||c.address||'-')} ${escC(c.city||'')} ${escC(c.district||'')} ${escC(c.postal_code||'')}</td></tr></table></div>
   <div class="panel" style="margin-top:14px"><h2>Ticari / Teslimat</h2><table><tr><td>Ödeme</td><td>${escC(c.default_payment_type||'-')}</td><td>Vade</td><td>${Number(c.default_due_days||0)} gün</td></tr><tr><td>Kredi limiti</td><td>${money(c.credit_limit||0)}</td><td>İskonto</td><td>%${Number(c.discount_rate||0).toFixed(2)}</td></tr><tr><td>Özel fiyat</td><td>${c.special_price!=null?money(c.special_price)+'/kg':'Yok'}</td><td>Minimum sipariş</td><td>${Number(c.minimum_order_kg||0).toLocaleString('tr-TR')} kg</td></tr><tr><td>Teslimat</td><td colspan="3">${escC(c.delivery_address||c.address||'-')} ${escC(c.delivery_city||c.city||'')} ${escC(c.delivery_district||c.district||'')}</td></tr><tr><td>Teslimat notu</td><td colspan="3">${escC(c.delivery_notes||'-')}</td></tr></table></div>
   <div class="panel" style="margin-top:14px"><h2>Notlar</h2><div class="status" style="white-space:pre-wrap">${escC(c.notes||'Not yok.')}</div></div>
   <div class="panel" style="margin-top:14px"><h2>Son Hareketler</h2>${customerActivity(id)}</div>`;
   modal.classList.add('open');
 };
 function customerActivity(id){
   const rows=[];
   (data.sales||[]).filter(s=>s.customer_id===id).forEach(s=>rows.push({d:s.sale_date,type:(s.status||'active')==='cancelled'?'İptal satış':'Satış',text:money(s.total)}));
   (data.collections||[]).filter(c=>c.customer_id===id).forEach(c=>rows.push({d:c.collection_date,type:(c.status||'active')==='cancelled'?'İptal tahsilat':'Tahsilat',text:money(c.amount)}));
   rows.sort((a,b)=>String(b.d).localeCompare(String(a.d))); if(!rows.length)return '<div class="empty">Hareket yok.</div>';
   return '<table><tr><th>Tarih</th><th>İşlem</th><th>Tutar</th></tr>'+rows.slice(0,30).map(r=>`<tr><td>${escC(r.d)}</td><td>${escC(r.type)}</td><td>${r.text}</td></tr>`).join('')+'</table>';
 }
 window.customerEdit=function(id){
   const c=(data.customers||[]).find(x=>x.id===id);if(!c)return;
   const types=['Restaurant','Kasap','Market','Diğer'], pay=['Peşin','Havale/EFT','Kredi Kartı','Vadeli'];
   modalbox.innerHTML=`<h2>Müşteri Düzenle</h2><div class="formgrid">
   ${field('c_name','İşletme / Müşteri Adı',c.name)}${field('c_code','Müşteri Kodu',c.customer_code)}${field('c_contact','Yetkili Kişi',c.contact_person)}${select('c_type','Müşteri Tipi',c.customer_type,types)}
   ${field('c_phone','Telefon',c.phone,'tel')}${field('c_alt','Alternatif Telefon',c.alternate_phone,'tel')}${field('c_whatsapp','WhatsApp',c.whatsapp,'tel')}${field('c_email','E-posta',c.email,'email')}
   ${field('c_website','Web Sitesi',c.website)}${select('c_pref','İletişim Tercihi',c.contact_preference,['Telefon','WhatsApp','E-posta','Fark etmez'])}${field('c_tax','Vergi No',c.tax_number)}${field('c_office','Vergi Dairesi',c.tax_office)}
   ${field('c_invoice_title','Fatura Unvanı',c.invoice_title)}${select('c_einvoice','E-Fatura Durumu',c.e_invoice_type,['E-Arşiv','E-Fatura','Kağıt Fatura'])}${field('c_city','İl',c.city)}${field('c_district','İlçe',c.district)}${field('c_postal','Posta Kodu',c.postal_code)}
   ${field('c_invoice_address','Fatura Adresi',c.invoice_address||c.address)}${field('c_delivery_address','Teslimat Adresi',c.delivery_address||c.address)}${field('c_delivery_city','Teslimat İl',c.delivery_city||c.city)}${field('c_delivery_district','Teslimat İlçe',c.delivery_district||c.district)}
   ${field('c_delivery_region','Teslimat Bölgesi',c.delivery_region)}${field('c_delivery_days','Teslimat Günleri',c.delivery_days)}${field('c_delivery_time','Tercih Edilen Saat',c.delivery_time)}${field('c_sales_rep','Satış Temsilcisi',c.sales_representative)}
   ${select('c_payment','Varsayılan Ödeme',c.default_payment_type,pay)}${field('c_due','Vade Günü',c.default_due_days,'number')}${field('c_limit','Kredi Limiti',c.credit_limit,'number')}${field('c_discount','İskonto %',c.discount_rate,'number')}
   ${field('c_group','Müşteri Grubu',c.customer_group)}${field('c_price_group','Özel Fiyat Grubu',c.price_group)}${field('c_special_price','Özel Kg Fiyatı',c.special_price,'number')}${field('c_min_kg','Minimum Sipariş Kg',c.minimum_order_kg,'number')}
   ${field('c_delivery_notes','Teslimat Notu',c.delivery_notes)}${field('c_notes','Genel Notlar',c.notes)}</div><div class="actions"><button class="btn secondary" onclick="customerDetail('${id}')">Geri</button><button class="btn primary" onclick="saveCustomerEdit('${id}')">Kaydet</button></div>`;
 };
 window.saveCustomerEdit=async function(id){
   try{
    const v=id=>document.getElementById(id)?.value?.trim()||null;
    const payload={name:v('c_name'),customer_code:v('c_code'),contact_person:v('c_contact'),customer_type:v('c_type'),phone:v('c_phone'),alternate_phone:v('c_alt'),whatsapp:v('c_whatsapp'),email:v('c_email'),website:v('c_website'),contact_preference:v('c_pref'),tax_number:v('c_tax'),tax_office:v('c_office'),invoice_title:v('c_invoice_title'),e_invoice_type:v('c_einvoice'),city:v('c_city'),district:v('c_district'),postal_code:v('c_postal'),invoice_address:v('c_invoice_address'),delivery_address:v('c_delivery_address'),delivery_city:v('c_delivery_city'),delivery_district:v('c_delivery_district'),delivery_region:v('c_delivery_region'),delivery_days:v('c_delivery_days'),delivery_time:v('c_delivery_time'),sales_representative:v('c_sales_rep'),default_payment_type:v('c_payment'),default_due_days:Number(document.getElementById('c_due')?.value||0),credit_limit:Number(document.getElementById('c_limit')?.value||0),discount_rate:Number(document.getElementById('c_discount')?.value||0),customer_group:v('c_group'),price_group:v('c_price_group'),special_price:document.getElementById('c_special_price')?.value?Number(document.getElementById('c_special_price').value):null,minimum_order_kg:Number(document.getElementById('c_min_kg')?.value||0),delivery_notes:v('c_delivery_notes'),notes:v('c_notes'),updated_at:new Date().toISOString(),updated_by:currentUser?.id||null};
    if(!payload.name)throw new Error('Müşteri adı zorunludur.');
    const {error}=await client.from('customers').update(payload).eq('id',id);if(error)throw error;
    await loadData();customerDetail(id);
   }catch(e){alert(e?.message||String(e))}
 };
 window.openCustomer=function(){
   modalbox.innerHTML=`<h2>Yeni Müşteri</h2><div class="formgrid">${field('nc_name','İşletme / Müşteri Adı')}${field('nc_code','Müşteri Kodu')}${field('nc_contact','Yetkili Kişi')}${select('nc_type','Müşteri Tipi','Restaurant',['Restaurant','Kasap','Market','Diğer'])}${field('nc_phone','Telefon','', 'tel')}${field('nc_alt','Alternatif Telefon','', 'tel')}${field('nc_whatsapp','WhatsApp','', 'tel')}${field('nc_email','E-posta','', 'email')}${field('nc_tax','Vergi No')}${field('nc_office','Vergi Dairesi')}${field('nc_invoice_title','Fatura Unvanı')}${select('nc_einvoice','E-Fatura Durumu','E-Arşiv',['E-Arşiv','E-Fatura','Kağıt Fatura'])}${field('nc_city','İl')}${field('nc_district','İlçe')}${field('nc_postal','Posta Kodu')}${field('nc_invoice_address','Fatura Adresi')}${field('nc_delivery_address','Teslimat Adresi')}${field('nc_delivery_city','Teslimat İl')}${field('nc_delivery_district','Teslimat İlçe')}${field('nc_delivery_notes','Teslimat Notu')}${select('nc_payment','Varsayılan Ödeme','Vadeli',['Peşin','Havale/EFT','Kredi Kartı','Vadeli'])}${field('nc_due','Varsayılan Vade Günü','0','number')}${field('nc_limit','Kredi Limiti','0','number')}${field('nc_discount','İskonto %','0','number')}${field('nc_price_group','Özel Fiyat Grubu')}${field('nc_special_price','Özel Kg Fiyatı','','number')}${field('nc_min_kg','Minimum Sipariş Kg','0','number')}${field('nc_notes','Notlar')}</div><div class="actions"><button class="btn secondary" onclick="closeModal()">İptal</button><button class="btn primary" onclick="saveCustomerV20()">Kaydet</button></div>`;modal.classList.add('open');
 };
 window.saveCustomerV20=async function(){
   try{const v=id=>document.getElementById(id)?.value?.trim()||null;const payload={name:v('nc_name'),customer_code:v('nc_code'),contact_person:v('nc_contact'),customer_type:v('nc_type'),phone:v('nc_phone'),alternate_phone:v('nc_alt'),whatsapp:v('nc_whatsapp'),email:v('nc_email'),tax_number:v('nc_tax'),tax_office:v('nc_office'),invoice_title:v('nc_invoice_title'),e_invoice_type:v('nc_einvoice'),city:v('nc_city'),district:v('nc_district'),postal_code:v('nc_postal'),invoice_address:v('nc_invoice_address'),delivery_address:v('nc_delivery_address'),delivery_city:v('nc_delivery_city'),delivery_district:v('nc_delivery_district'),delivery_notes:v('nc_delivery_notes'),default_payment_type:v('nc_payment'),default_due_days:Number(document.getElementById('nc_due')?.value||0),credit_limit:Number(document.getElementById('nc_limit')?.value||0),discount_rate:Number(document.getElementById('nc_discount')?.value||0),price_group:v('nc_price_group'),special_price:document.getElementById('nc_special_price')?.value?Number(document.getElementById('nc_special_price').value):null,minimum_order_kg:Number(document.getElementById('nc_min_kg')?.value||0),notes:v('nc_notes'),is_active:true,updated_at:new Date().toISOString()};if(!payload.name)throw new Error('Müşteri adı zorunludur.');const {error}=await client.from('customers').insert(payload);if(error)throw error;await loadData();closeModal();show('customers');}catch(e){alert(e?.message||String(e))}
 };
})();
</script>'''
if 'carbonerp-v20-customer-profile' not in s:
    s=s.replace(marker,script+'\n'+marker,1)
p.write_text(s,encoding='utf-8')
