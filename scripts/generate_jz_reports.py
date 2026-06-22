#!/usr/bin/env python3
"""Generate Jiangzhe cuisine reports."""
import json, os, re

# Load data
with open('/Users/macclaw/hudadao-r-and-d-assistant/data/jz_search_results.json') as f:
    searches = json.load(f)

DATA_DIR = '/tmp/shops'
OUTPUT_DIR = '/Users/macclaw/hudadao-r-and-d-assistant/reports'

TOTALS = {
    '江浙菜_精选': 29,
    '江浙菜_必吃榜': 24,
    '江浙菜_排队': 60,
    '江浙菜_老字号': 60,
}
CAP = 60

def find_paired(shop_id):
    fpath = os.path.join(DATA_DIR, f'p_{shop_id}.json')
    if os.path.exists(fpath):
        try: return json.load(open(fpath))
        except: pass
    return None

def get_info(shop_id, shop_name):
    fpath = os.path.join(DATA_DIR, f't_{shop_id}.txt')
    if not os.path.exists(fpath): return {'name': shop_name}
    with open(fpath) as f: text = f.read()
    text = re.sub(r'--- BEGIN.*?CONTENT ---\n?', '', text)
    text = re.sub(r'--- END.*?CONTENT ---', '', text)
    text = re.sub(r'^打开App\s*', '', text)
    info = {'name': shop_name}
    m = re.search(r'★+\s*(\d\.\d)\s*(\d+)\s*条', text)
    if m: info['rating']=float(m.group(1)); info['reviewCount']=int(m.group(2))
    m = re.search(r'¥(\d+)', text)
    if m: info['price']='¥'+m.group(1)
    m = re.search(r'(?:¥\d+/\w+)\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if not m: m = re.search(r'/\w+\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if m: info['category']=m.group(1)
    m = re.search(r'口味:\s*([\d.]+)\s+环境:\s*([\d.]+)\s+服务:\s*([\d.]+)', text)
    if m: info['tasteScore']=float(m.group(1)); info['envScore']=float(m.group(2)); info['serviceScore']=float(m.group(3))
    for a in ['淮海路','南京西路商圈','南京东路商圈','陆家嘴商圈','静安寺商圈','徐家汇商圈','新天地/马当路','虹桥枢纽','八佰伴','外滩商圈','前滩']:
        if a in text: info['location']=a; break
    keywords = []
    for m in re.finditer(r'([一-鿿]{2,20})\s+(\d{2,5})', text):
        kw=m.group(1).strip(); cnt=int(m.group(2))
        if not any(s in kw for s in ['分钟前','小时前','时前有','查看全部']) and cnt>2:
            keywords.append((kw,cnt))
    info['keywords'] = keywords
    return info

CSS='*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;background:#f5f5f5;color:#333;padding:20px}.container{max-width:1100px;margin:0 auto}.header{background:linear-gradient(135deg,#c0392b,#e74c3c);color:#fff;padding:40px 24px;border-radius:16px;margin-bottom:24px;text-align:center}.header h1{font-size:26px}.header .desc{font-size:13px;opacity:.85;margin-top:8px}.shop-card{background:#fff;border-radius:16px;margin-bottom:28px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.08)}.shop-banner{padding:18px 24px;border-bottom:1px solid #eee;background:#fafafa}.shop-banner h2{font-size:17px;font-weight:700;margin-bottom:2px}.shop-banner .meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:2px;font-size:13px;color:#666;align-items:center}.shop-banner .stars{color:#f5a623;font-size:15px}.score-high{color:#27ae60}.score-mid{color:#f39c12}.price-tag{color:#c0392b;font-weight:700;font-size:17px}.award-badge{display:inline-block;background:#c0392b;color:#fff;padding:2px 10px;border-radius:12px;font-size:11px}.score-grid{display:flex;gap:10px;padding:10px 24px;border-bottom:1px solid #eee;flex-wrap:wrap}.score-item{flex:1;min-width:55px;text-align:center}.score-item .val{font-size:16px;font-weight:700}.score-item .lbl{font-size:11px;color:#999}.section{padding:14px 24px;border-bottom:1px solid #eee}.section:last-child{border-bottom:none}.section h3{font-size:14px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px}.section h3 .badge{background:#c0392b;color:#fff;font-size:10px;padding:1px 8px;border-radius:10px}.dish-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.dish-card{background:#fff;border:1px solid #eee;border-radius:8px;overflow:hidden}.dish-card .img-wrap{width:100%;aspect-ratio:1.54;background:#f5f5f5;overflow:hidden;display:flex;align-items:center;justify-content:center}.dish-card .img-wrap img{width:100%;height:100%;object-fit:cover}.dish-card .img-wrap .no-img{color:#ddd;font-size:30px}.dish-card .info{padding:6px 8px}.dish-card .dish-name{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dish-card .dish-count{font-size:11px;color:#999}.dish-card .rank{display:inline-block;width:18px;height:18px;line-height:18px;text-align:center;background:#c0392b;color:#fff;font-size:10px;border-radius:50%;margin-right:3px}.dish-card:nth-child(n+4) .rank{background:#e67e22}.dish-card:nth-child(n+7) .rank{background:#95a5a6}.kw-grid{display:flex;flex-wrap:wrap;gap:5px}.kw-tag{background:#fef3f2;color:#c0392b;padding:4px 10px;border-radius:14px;font-size:12px;border:1px solid #fdd;white-space:nowrap}.kw-tag .cnt{color:#e74c3c;font-weight:700;margin-left:3px}.select-btn{color:#ccc;cursor:pointer;font-size:16px;margin-left:4px;transition:color .2s;user-select:none}.select-btn:hover{color:#f5a623}.select-btn.selected{color:#f5a623}.select-hint{font-size:11px;color:#999;text-align:center;padding:4px 0 8px;border-bottom:1px solid #eee}.footer{text-align:center;padding:20px;color:#999;font-size:12px}@media(max-width:768px){.dish-grid{grid-template-columns:repeat(3,1fr)}.shop-banner h2{font-size:15px}.score-grid{gap:6px;padding:8px 12px}.score-item .val{font-size:14px}.section{padding:10px 14px}.dish-card .dish-name{font-size:11px}}@media print{body{background:#fff;padding:0}.shop-card{box-shadow:none;border:1px solid #ddd;break-inside:avoid}.header{background:#c0392b!important;-webkit-print-color-adjust:exact}.select-btn,.select-hint{display:none!important}}'

for category, shops in searches.items():
    total = TOTALS.get(category, len(shops))
    cap = min(CAP, total)
    shops = shops[:cap]
    shown = len(shops)
    city_label = '上海'
    cat_label = category.replace('江浙菜_', '')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="no-referrer">
<title>上海江浙菜 {cat_label} 餐厅研究报告</title>
<style>{CSS}</style>
<script>
function toggleDish(btn,dishName,shopName,imgUrl){{const list=JSON.parse(localStorage.getItem('researchList')||'[]');const key=shopName+'::'+dishName;const idx=list.findIndex(item=>item.shop+'::'+item.dish===key);if(idx>=0){{list.splice(idx,1);btn.classList.remove('selected');btn.textContent='☆'}}else{{list.push({{shop:shopName,dish:dishName,img:imgUrl||''}});btn.classList.add('selected');btn.textContent='★'}}localStorage.setItem('researchList',JSON.stringify(list));updateCount()}}
function updateCount(){{const el=document.getElementById('researchCount');if(el)el.textContent=(JSON.parse(localStorage.getItem('researchList')||'[]')).length}}
window.addEventListener('load',function(){{updateCount();document.querySelectorAll('.select-btn').forEach(b=>{{const list=JSON.parse(localStorage.getItem('researchList')||'[]');if(list.some(i=>i.shop===b.dataset.shop&&i.dish===b.dataset.dish)){{b.classList.add('selected');b.textContent='★'}}}})}});
</script>
</head>
<body>
<div class="container">
<div class="header">
<div style="float:right;font-size:13px;opacity:.9;background:rgba(255,255,255,.15);padding:4px 14px;border-radius:20px">
<a href="research_list.html" style="color:#fff;text-decoration:none">📋 研究清单 <span id="researchCount" style="font-weight:700">0</span> 道菜</a>
</div>
<h1>🍜 上海江浙菜 · {cat_label}</h1>
<div class="desc">📍 上海 · 2026-06-22 · 已收录 <strong>{shown}/{total}</strong> 家 · 仙味楼 R&D 助手</div>
<button class="btn-print" onclick="window.print()" style="float:right;margin-top:8px;padding:4px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#fff;font-size:12px;cursor:pointer">🖨️ 导出PDF</button>
</div>'''

    for idx, (name, shop_id) in enumerate(shops):
        pd = find_paired(shop_id)
        info = get_info(shop_id, name)
        rating = info.get('rating', 0)
        stars = '★'*max(1,round(rating)) if rating else ''
        def sc(s): return 'score-high' if (s or 0)>=4.5 else ('score-mid' if (s or 0)>=4.0 else '')

        html += f'''
<div class="shop-card">
<div class="shop-banner">
<h2>{idx+1}. {name}</h2>
<div class="meta">
<span class="stars">{stars}</span>
<span class="{sc(rating)}" style="font-weight:700;font-size:16px">{rating}</span>
<span>|</span><span class="price-tag">{info.get('price','')}</span>
<span>|</span><span>{info.get('category','')}</span>
{f'<span>|📍 {info.get("location","")}</span>' if info.get('location') else ''}
</div>
</div>
<div class="score-grid">
<div class="score-item"><div class="val {sc(info.get('tasteScore'))}">{info.get('tasteScore','')}</div><div class="lbl">口味</div></div>
<div class="score-item"><div class="val {sc(info.get('envScore'))}">{info.get('envScore','')}</div><div class="lbl">环境</div></div>
<div class="score-item"><div class="val {sc(info.get('serviceScore'))}">{info.get('serviceScore','')}</div><div class="lbl">服务</div></div>
<div class="score-item"><div class="val">{info.get('reviewCount','')}</div><div class="lbl">评价数</div></div>
</div>'''

        dishes = pd.get('paired', [])[:10] if pd and 'paired' in pd else []
        if dishes:
            html += '\n<div class="section"><h3>🍽️ 推荐菜 Top 10</h3>\n<div class="dish-grid">'
            for j, d in enumerate(dishes):
                de = d["name"].replace("'", "\\'").replace('"', '&quot;')
                ne = name.replace("'", "\\'").replace('"', '&quot;')
                img_tag = f'<img src="{d["img"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=no-img>🍽️</div>\'">'
                hot = '🔥' if j < 3 else ''
                html += f'''
<div class="dish-card">
<div class="img-wrap">{img_tag}</div>
<div class="info">
<div class="dish-name"><span class="rank">{j+1}</span>{d["name"]}</div>
<div class="dish-count">{hot} <span class="select-btn" data-dish="{de}" data-shop="{ne}" data-img="{d["img"]}" onclick="toggleDish(this,\'{de}\',\'{ne}\',\'{d["img"]}\')" style="cursor:pointer;margin-left:6px;font-size:16px">☆</span></div>
</div>
</div>'''
            html += '\n</div>\n<div class="select-hint">💡 点击菜品上的 <span style="color:#f5a623">☆</span> 收藏到研究清单</div></div>'

        keywords = info.get('keywords', [])
        if keywords:
            html += f'\n<div class="section"><h3>💬 评价关键词 <span class="badge">共{len(keywords)}个</span></h3><div class="kw-grid">'
            for kw, cnt in keywords[:20]:
                html += f'<span class="kw-tag">{kw} <span class="cnt">{cnt}</span></span>'
            html += '</div></div>'
        html += '\n</div>\n'

    html += f'''
<div class="footer"><p>仙味楼 R&D 助手 · 上海江浙菜 {cat_label} · 2026-06-22</p></div>
</div>
</body>
</html>'''

    fname = f'上海江浙菜_{cat_label}_20260622.html'
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, 'w') as f: f.write(html)
    dp = os.path.expanduser(f'~/Desktop/{fname}')
    with open(dp, 'w') as f: f.write(html)
    print(f'✅ {fname} ({shown}家)')

print(f'\n所有江浙菜报告已生成')
