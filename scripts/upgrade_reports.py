"""Upgrade reports: mobile CSS, image in research list, PDF export."""
import re

SCRIPT = '/Users/macclaw/hudadao-r-and-d-assistant/scripts/generate_category_reports.py'

with open(SCRIPT, 'r') as f:
    content = f.read()

# 1. Mobile + print CSS
old_css = '@media(max-width:768px){.dish-grid{grid-template-columns:repeat(3,1fr)}}'
new_css = '@media(max-width:768px){.dish-grid{grid-template-columns:repeat(3,1fr)}.shop-banner h2{font-size:15px}.score-grid{gap:6px;padding:8px 12px}.score-item .val{font-size:14px}.section{padding:10px 14px}.dish-card .dish-name{font-size:11px}}@media print{body{background:#fff;padding:0}.shop-card{box-shadow:none;border:1px solid #ddd;break-inside:avoid}.header{background:#c0392b!important;-webkit-print-color-adjust:exact}.select-btn,.select-hint,.btn-print{display:none!important}}'
content = content.replace(old_css, new_css)

# 2. Add data-img attribute to dish card
old_attr = 'data-shop="{name_escaped}" onclick="toggleDish(this,\'{dish_escaped}\',\'{name_escaped}\')"'
new_attr = 'data-shop="{name_escaped}" data-img="{d["img"]}" onclick="toggleDish(this,\'{dish_escaped}\',\'{name_escaped}\',\'{d["img"]}\')"'
content = content.replace(old_attr, new_attr)

# 3. Update toggleDish function
old_func = 'function toggleDish(btn, dishName, shopName) {'
new_func = 'function toggleDish(btn, dishName, shopName, imgUrl) {'
content = content.replace(old_func, new_func)

old_push = 'list.push({shop: shopName, dish: dishName});'
new_push = 'list.push({shop: shopName, dish: dishName, img: imgUrl || \'\'});'
content = content.replace(old_push, new_push)

# 4. Add print button in header after the research list link
old_header_end = '</div>\n</div>\n\n    for idx, (name, shop_id) in enumerate(shops):'
new_header_end = '</div>\n<button class="btn-print" onclick="window.print()" style="float:right;margin-top:8px;padding:4px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#fff;font-size:12px;cursor:pointer">🖨️ 导出PDF</button>\n</div>\n\n    for idx, (name, shop_id) in enumerate(shops):'
content = content.replace(old_header_end, new_header_end)

with open(SCRIPT, 'w') as f:
    f.write(content)

print('Script updated successfully')
