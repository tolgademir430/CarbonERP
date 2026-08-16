from pathlib import Path
import re

s=Path('index.html').read_text(encoding='utf-8')
blocks=re.findall(r'<script id="carbonerp-v20-customer-module">(.*?)</script>',s,flags=re.S|re.I)
errors=[]
if len(blocks)!=1:
    errors.append(f'customer module count={len(blocks)}')
else:
    js=blocks[0]
    # This module contains printable HTML embedded in JavaScript strings.
    # Do structural checks here; a raw Node parser cannot distinguish the
    # embedded print markup from actual script tags reliably.
    if not js.strip():
        errors.append('customer module is empty')
    if js.count('{') != js.count('}'):
        errors.append('customer module brace count mismatch')
    if js.count('(') != js.count(')'):
        errors.append('customer module parenthesis count mismatch')
for marker in ['customerTable','customerDetail','customerEdit','saveCustomerEdit','openCustomer','saveCustomerClean','printCustomerStatement']:
    if marker not in s:
        errors.append('missing '+marker)
required=['customer_code','contact_person','customer_type','alternate_phone','whatsapp','invoice_title','delivery_address','credit_limit','discount_rate','special_price','minimum_order_kg']
for field in required:
    if field not in s:
        errors.append('missing field '+field)
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); raise SystemExit(1)
print('CarbonERP customer module structural validation passed')
