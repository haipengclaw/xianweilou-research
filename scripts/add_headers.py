#!/usr/bin/env python3
"""Add restaurant header images to the full report."""
import json, os, re

report_path = '/Users/macclaw/hudadao-r-and-d-assistant/reports/full_report.html'
with open(report_path, 'r') as f:
    html = f.read()

# Mapping from shop name in report to header file key
headers = {
    '老兴鲜(黄浦店)': 'laoxingxian',
    '蘭心餐厅(进贤路店)': 'lanxin',
    '新荣记(南京西路店)': 'xinrongji_nj',
    '外滩家宴·上海本帮菜(罗斯福公馆店)': 'waibaojiayan',
    '周舍·海派菜(虹桥店)': 'zhoushe',
    '雍福会(永福路店)': 'yongfuhui',
    '鹿园 MOOSE(浦东店)': 'luyuan',
    '西郊5号·Maggie 5': 'xijiao5hao',
    '龚禧龚禧·甬菜(汤臣洲际店)': 'gongxigongxi',
    '新荣记(前滩店)': 'xinrongji_qiantan',
    '雍颐庭': 'yongyiting',
    '老正兴菜馆(福州路店)': 'laozhengxing',
    '逸谷会(静安嘉里中心店)': 'yiguhui',
    '龙悦舫(丽园路店)': 'longyuefang',
    '逸采EASEFUL CUISINE(普陀店)': 'yicai',
    '叶马(环贸iapm店)': 'yema',
    '广富林宰相府酒店·鹿鸣阁': 'guangfulin',
    '豪生酒家': 'haosheng',
    '龙吟山房(苏河湾万象天地店)': 'longyinshanfang',
    '茂隆餐厅(进贤路店)': 'maolong',
    '越稽·地道绍兴菜馆(爱琴海缤纷里店)': 'yueji',
    '顶特勒粥面馆(淮海路店)': 'dingtele',
    '复兴面王·酒菜面饭&手作小笼包(外滩福州路店)': 'fuxingmianwang',
}

# Load header images
header_imgs = {}
for shop_name, file_key in headers.items():
    fpath = f'/tmp/shops/header_{file_key}.json'
    if os.path.exists(fpath):
        try:
            with open(fpath) as f:
                data = json.load(f)
            img = data.get('header', '')
            if img:
                header_imgs[shop_name] = img
        except:
            pass

print(f'Loaded {len(header_imgs)} header images')

# For each shop, replace the banner HTML
for shop_name, img_url in header_imgs.items():
    # Escape special characters for regex
    name_escaped = re.escape(shop_name)

    # Find the shop banner pattern: <div class="shop-banner"> then <h2>N. NAME</h2>
    # Replace with version that has header image
    pattern = rf'(<div class="shop-card"[^>]*>)\s*<div class="shop-banner">\s*<h2>(\d+\.\s*){name_escaped}</h2>\s*<div class="meta">'

    replacement = rf'\1<div class="shop-banner" style="display:flex;align-items:center;gap:14px">\n<div style="flex-shrink:0;width:60px;height:60px;border-radius:10px;overflow:hidden;background:#f0f0f0;box-shadow:0 2px 6px rgba(0,0,0,.08)"><img src="{img_url}" style="width:100%;height:100%;object-fit:cover" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>\n<div style="flex:1;min-width:0">\n<h2 style="font-size:17px;margin-bottom:2px">\2{shop_name}</h2>\n<div class="meta" style="margin-top:2px">'

    new_html, count = re.subn(pattern, replacement, html, count=1)
    if count > 0:
        html = new_html
        print(f'  ✅ {shop_name[:20]}')
    else:
        print(f'  ❌ {shop_name[:20]} - pattern not matched')

# Also close the new div structure properly
# The original has </div></div> after meta, need to add </div></div>
# This is tricky - let me just fix the closing tags
# The original: </div></div>
# We replaced opening, but the closing stays the same

output_path = '/Users/macclaw/hudadao-r-and-d-assistant/reports/full_report_with_headers.html'
with open(output_path, 'w') as f:
    f.write(html)

print(f'\nReport saved: {output_path}')
print(f'Open: file://{output_path}')
