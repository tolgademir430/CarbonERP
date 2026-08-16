from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='<!-- CARBONERP_CUSTOMER_LIST_V20 -->'
if marker in s: raise SystemExit('Customer list enhancement already present')
js=r'''<script>
(function(){
const MARKER='customer-list-enhancement-v20';
const money=v=>new Intl.NumberFormat('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(v||0))+' TL';
function customerPage(){return (document.querySelector('#app')?.innerText||'').toLocaleLowerCase('tr-TR').includes('müşteriler');}
function table(){const ts=[...document.querySelectorAll('#app table')];return ts.find(t=>{const h=(t.querySelector('thead')?.innerText||t.rows?.[0]?.innerText||'').toLocaleLowerCase('tr-TR');return h.includes('müşteri')||h.includes('telefon')||h.includes('cari');})||ts[0];}
async function totalReceivable(){try{if(!window.supabaseClient)return null;const [{data:sales,error:se},{data:collections,error:ce}]=await Promise.all([window.supabaseClient.from('sales').select('customer_id,total,payment_type,status').eq('status','active'),window.supabaseClient.from('collections').select('customer_id,amount,status').eq('status','active')]);if(se||ce)return null;const c=new Map();(collections||[]).forEach(x=>c.set(x.customer_id,(c.get(x.customer_id)||0)+Number(x.amount||0)));let total=0;(sales||[]).forEach(x=>{if(x.payment_type==='Peşin')return;total+=Math.max(0,Number(x.total||0)-(c.get(x.customer_id)||0));});return total;}catch(e){return null;}}
function numberRows(t){if(t.dataset.numbered==='1')return;const h=t.tHead?.rows?.[0];if(h){const th=document.createElement('th');th.textContent='No';h.insertBefore(th,h.firstChild);} [...t.tBodies].forEach(tb=>[...tb.rows].forEach((r,i)=>{const td=document.createElement('td');td.textContent=String(i+1);r.insertBefore(td,r.firstChild);}));t.dataset.numbered='1';}
function filterRows(t,q){const n=(q||'').trim().toLocaleLowerCase('tr-TR');let i=0;[...t.tBodies].forEach(tb=>[...tb.rows].forEach(r=>{const ok=!n||r.innerText.toLocaleLowerCase('tr-TR').includes(n);r.style.display=ok?'':'none';if(ok){i++;if(r.cells[0])r.cells[0].textContent=String(i);}}));}
async function enhance(){if(!customerPage())return;const t=table();if(!t||!t.parentElement)return;const host=t.parentElement;if(!document.getElementById(MARKER)){const box=document.createElement('div');box.id=MARKER;box.style.cssText='display:flex;gap:10px;align-items:center;margin:0 0 14px;flex-wrap:wrap';box.innerHTML='<input id="carbonerpCustomerSearch" type="search" placeholder="Müşteri adı ara..." autocomplete="off" style="flex:1;min-width:240px;padding:11px;border:1px solid #cfd4d9;border-radius:8px"><span style="font-size:12px;color:#68717a">İsim, telefon veya müşteri kodu ile ara</span>';host.parentNode.insertBefore(box,host);box.querySelector('input').addEventListener('input',e=>filterRows(t,e.target.value));}numberRows(t);if(!document.getElementById('carbonerpTotalReceivable')){const card=document.createElement('div');card.id='carbonerpTotalReceivable';card.style.cssText='margin-top:14px;padding:16px 18px;background:#fff;border:1px solid #e1e4e7;border-radius:12px;font-weight:700;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap';card.innerHTML='<span>Müşterilerden Toplam Alacak</span><strong id="carbonerpTotalReceivableValue">Hesaplanıyor...</strong>';host.parentNode.insertBefore(card,host.nextSibling);const v=await totalReceivable();document.getElementById('carbonerpTotalReceivableValue').textContent=v===null?'Hesaplanamadı':money(v);}}
let timer=0;const observer=new MutationObserver(()=>{clearTimeout(timer);timer=setTimeout(enhance,120);});observer.observe(document.getElementById('app')||document.body,{childList:true,subtree:true});setTimeout(enhance,300);
})();
</script>
<!-- CARBONERP_CUSTOMER_LIST_V20 -->
'''
s=s.replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
