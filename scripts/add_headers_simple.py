"""Post-process generated HTML report to add header images."""
import json, os, re

report_path = '/Users/macclaw/hudadao-r-and-d-assistant/reports/full_report.html'

with open(report_path, 'r') as f:
    html = f.read()

# Header image mapping
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

# Process each shop
count = 0
for name, key in headers.items():
    fpath = f'/tmp/shops/header_{key}.json'
    if not os.path.exists(fpath):
        continue
    try:
        with open(fpath) as f:
            data = json.load(f)
        img_url = data.get('header', '')
        if not img_url:
            continue
    except:
        continue

    # Find the shop banner in the HTML
    # Pattern: <div class="shop-banner">\n<h2>N. NAME</h2>
    # Insert: <div class="shop-banner" style="display:flex;align-items:center;gap:14px">\n<div>...img...</div>\n<div style="flex:1">\n<h2>...
    shop_pattern = f'<h2>\\d+\\. {re.escape(name)}</h2>'
    match = re.search(shop_pattern, html)
    if not match:
        print(f'  ⚠️  {name}: shop not found in HTML')
        continue

    pos = match.start()
    # Find the start of shop-banner div (go backwards)
    banner_start = html.rfind('<div class="shop-banner">', 0, pos)
    if banner_start < 0:
        print(f'  ⚠️  {name}: banner div not found')
        continue

    # Find the end of the banner div (the </div> that closes the meta div)
    # After the h2 there's the meta div, which closes with </div>
    meta_end = html.find('</div>', pos)
    meta_end2 = html.find('</div>', meta_end + 6)
    if meta_end2 < 0:
        meta_end2 = meta_end

    # The banner structure is:
    # <div class="shop-banner">
    #   <h2>N. NAME</h2>
    #   <div class="meta">...</div>
    # </div>
    banner_content_end = html.find('</div>', meta_end2 + 6) + 6

    # Extract banner content
    banner_content = html[banner_start + len('<div class="shop-banner">'):banner_content_end]

    # Create new banner with header image
    img_html = f'''
<div class="shop-banner" style="display:flex;align-items:center;gap:14px">
<div style="flex-shrink:0;width:60px;height:60px;border-radius:10px;overflow:hidden;background:#f0f0f0;box-shadow:0 2px 6px rgba(0,0,0,.08)"><img src="{img_url}" style="width:100%;height:100%;object-fit:cover" loading="lazy" onerror="this.parentElement.style.display='none'"></div>
<div style="flex:1;min-width:0">{banner_content}
</div>'''

    html = html[:banner_start] + img_html + html[banner_content_end:]
    count += 1
    print(f'  ✅ {name[:20]}')

output_path = '/Users/macclaw/hudadao-r-and-d-assistant/reports/full_report_with_headers.html'
with open(output_path, 'w') as f:
    f.write(html)

print(f'\n✅ {count} headers added')
print(f'📄 {output_path}')
