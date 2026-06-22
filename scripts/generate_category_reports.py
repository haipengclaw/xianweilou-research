#!/usr/bin/env python3
"""Generate HTML reports for each search category."""
import json, os, re

# Load search data
with open('/Users/macclaw/hudadao-r-and-d-assistant/data/search_results.json') as f:
    searches = json.load(f)

DATA_DIR = '/tmp/shops'
OUTPUT_DIR = '/Users/macclaw/hudadao-r-and-d-assistant/reports'

# Helper: find paired data file for a shop ID
def find_paired(shop_id):
    fpath = os.path.join(DATA_DIR, f'p_{shop_id}.json')
    if os.path.exists(fpath):
        try:
            with open(fpath) as f:
                return json.load(f)
        except:
            pass
    return None

# Helper: extract basic info and keywords from text file
def get_shop_info(shop_id, shop_name):
    text = None
    # Try direct text file (t_<shopId>.txt) first - fastest
    direct_path = os.path.join(DATA_DIR, f't_{shop_id}.txt')
    if os.path.exists(direct_path):
        with open(direct_path) as f:
            text = f.read()
    else:
        # Fallback: search in all text files by shop name
        for fname in os.listdir(DATA_DIR):
            if fname.endswith('.txt') and not fname.startswith('t_'):
                try:
                    with open(os.path.join(DATA_DIR, fname)) as f:
                        content = f.read()
                    if shop_name[:6] in content:
                        text = content
                        break
                except: pass

    info = {'name': shop_name}
    if not text:
        return info

    text = re.sub(r'--- BEGIN.*?CONTENT ---\n?', '', text)
    text = re.sub(r'--- END.*?CONTENT ---', '', text)
    text = re.sub(r'^打开App\s*', '', text)

    m = re.search(r'★+\s*(\d\.\d)\s*(\d+)\s*条', text)
    if m:
        info['rating'] = float(m.group(1))
        info['reviewCount'] = int(m.group(2))

    m = re.search(r'¥(\d+)', text)
    if m: info['price'] = '¥' + m.group(1)

    m = re.search(r'(?:¥\d+/\w+)\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if not m: m = re.search(r'/\w+\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if m: info['category'] = m.group(1)

    m = re.search(r'口味:\s*([\d.]+)\s+环境:\s*([\d.]+)\s+服务:\s*([\d.]+)', text)
    if m:
        info['tasteScore'] = float(m.group(1))
        info['envScore'] = float(m.group(2))
        info['serviceScore'] = float(m.group(3))

    m = re.search(r'(\d{4}上榜[^ ]+)', text)
    if m: info['award'] = m.group(1)

    m = re.search(r'([一-鿿]+路[一-鿿0-9]+号[一-鿿0-9]*(?:商场|广场|大厦|中心|楼|馆|店)?)', text)
    if m: info['address'] = m.group(1)

    for area in ['淮海路','南京西路商圈','南京东路商圈','陆家嘴商圈','静安寺商圈',
                 '徐家汇商圈','新天地/马当路','虹桥枢纽','八佰伴','外滩商圈',
                 '北新泾/淞虹路','张江商圈','曲阳地区','复兴西路/丁香花园',
                 '苏河湾','松江大学城','前滩','桃浦商圈','金山区']:
        if area in text:
            info['location'] = area
            break

    m = re.search(r'(热门榜\s*[··]\s*第\d+名)', text)
    if m: info['rank'] = m.group(1)

    # Keywords
    keywords = []
    for m in re.finditer(r'([一-鿿]{2,20})\s+(\d{2,5})', text):
        kw = m.group(1).strip()
        cnt = int(m.group(2))
        skip_words = ['分钟前', '小时前', '时前有', '查看全部']
        if not any(s in kw for s in skip_words) and cnt > 2:
            keywords.append((kw, cnt))
    info['keywords'] = keywords

    return info

# CSS template
CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f5f5;color:#333;padding:20px}
.container{max-width:1100px;margin:0 auto}
.header{background:linear-gradient(135deg,#c0392b,#e74c3c);color:#fff;padding:40px 24px;border-radius:16px;margin-bottom:24px;text-align:center}
.header h1{font-size:26px}
.header .desc{font-size:13px;opacity:.85;margin-top:8px}
.shop-card{background:#fff;border-radius:16px;margin-bottom:28px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.08)}
.shop-banner{padding:18px 24px;border-bottom:1px solid #eee;background:#fafafa}
.shop-banner h2{font-size:17px;font-weight:700;margin-bottom:2px}
.shop-banner .meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:2px;font-size:13px;color:#666;align-items:center}
.shop-banner .stars{color:#f5a623;font-size:15px}
.score-high{color:#27ae60}.score-mid{color:#f39c12}
.price-tag{color:#c0392b;font-weight:700;font-size:17px}
.award-badge{display:inline-block;background:#c0392b;color:#fff;padding:2px 10px;border-radius:12px;font-size:11px}
.score-grid{display:flex;gap:10px;padding:10px 24px;border-bottom:1px solid #eee;flex-wrap:wrap}
.score-item{flex:1;min-width:55px;text-align:center}
.score-item .val{font-size:16px;font-weight:700}
.score-item .lbl{font-size:11px;color:#999}
.section{padding:14px 24px;border-bottom:1px solid #eee}
.section:last-child{border-bottom:none}
.section h3{font-size:14px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.section h3 .badge{background:#c0392b;color:#fff;font-size:10px;padding:1px 8px;border-radius:10px}
.dish-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.dish-card{background:#fff;border:1px solid #eee;border-radius:8px;overflow:hidden}
.dish-card .img-wrap{width:100%;aspect-ratio:1.54;background:#f5f5f5;overflow:hidden;display:flex;align-items:center;justify-content:center}
.dish-card .img-wrap img{width:100%;height:100%;object-fit:cover}
.dish-card .img-wrap .no-img{color:#ddd;font-size:30px}
.dish-card .info{padding:6px 8px}
.dish-card .dish-name{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dish-card .dish-count{font-size:11px;color:#999}
.select-btn{color:#ccc;cursor:pointer;font-size:16px;margin-left:4px;transition:color .2s;user-select:none}
.select-btn:hover{color:#f5a623}
.select-btn.selected{color:#f5a623}
.dish-card .rank{display:inline-block;width:18px;height:18px;line-height:18px;text-align:center;background:#c0392b;color:#fff;font-size:10px;border-radius:50%;margin-right:3px}
.dish-card:nth-child(n+4) .rank{background:#e67e22}
.dish-card:nth-child(n+7) .rank{background:#95a5a6}
.kw-grid{display:flex;flex-wrap:wrap;gap:5px}
.kw-tag{background:#fef3f2;color:#c0392b;padding:4px 10px;border-radius:14px;font-size:12px;border:1px solid #fdd;white-space:nowrap}
.kw-tag .cnt{color:#e74c3c;font-weight:700;margin-left:3px}
.footer{text-align:center;padding:20px;color:#999;font-size:12px}
@media(max-width:768px){.dish-grid{grid-template-columns:repeat(3,1fr)}.shop-banner h2{font-size:15px}.score-grid{gap:6px;padding:8px 12px}.score-item .val{font-size:14px}.section{padding:10px 14px}.dish-card .dish-name{font-size:11px}}@media print{body{background:#fff;padding:0}.shop-card{box-shadow:none;border:1px solid #ddd;break-inside:avoid}.header{background:#c0392b!important;-webkit-print-color-adjust:exact}.select-btn,.select-hint,.btn-print{display:none!important}}
'''

# Total counts per category
TOTALS = {
    '黑珍珠': 15,
    '必吃榜': 21,
    '排队': 192,
    '老字号': 2103,
}

# Cap at 60 - how many we're displaying
CAP = 60

def generate_report(category, shops):
    name_fn = category.replace('/', '_')
    total_available = TOTALS.get(category, len(shops))
    cap = min(CAP, total_available)
    shops = shops[:cap]  # Only take first `cap` shops
    shown = len(shops)
    remaining_total = total_available - shown
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>上海本帮菜 {category} 餐厅研究报告</title>
<style>{CSS}</style>
<script>
// Selection system - add/remove dishes to research list
function toggleDish(btn, dishName, shopName, imgUrl) {{
  const list = JSON.parse(localStorage.getItem('researchList') || '[]');
  const key = shopName + '::' + dishName;
  const idx = list.findIndex(item => item.shop + '::' + item.dish === key);
  if (idx >= 0) {{
    list.splice(idx, 1);
    btn.classList.remove('selected');
    btn.textContent = '☆';
  }} else {{
    list.push({{shop: shopName, dish: dishName}});
    btn.classList.add('selected');
    btn.textContent = '★';
  }}
  localStorage.setItem('researchList', JSON.stringify(list));
  updateCount();
}}

function updateCount() {{
  const list = JSON.parse(localStorage.getItem('researchList') || '[]');
  const el = document.getElementById('researchCount');
  if (el) el.textContent = list.length;
}}

// Check if a dish is selected
function isSelected(dishName, shopName) {{
  const list = JSON.parse(localStorage.getItem('researchList') || '[]');
  return list.some(item => item.shop === shopName && item.dish === dishName);
}}

window.addEventListener('load', function() {{
  updateCount();
  // Restore selected states
  document.querySelectorAll('.select-btn').forEach(btn => {{
    const dish = btn.dataset.dish;
    const shop = btn.dataset.shop;
    if (isSelected(dish, shop)) {{
      btn.classList.add('selected');
      btn.textContent = '★';
    }}
  }});
}});
</script>
</head>
<body>
<div class="container">
<div class="header">
<div style="float:right;font-size:13px;opacity:.9;background:rgba(255,255,255,.15);padding:4px 14px;border-radius:20px">
<a href="research_list.html" style="color:#fff;text-decoration:none">📋 研究清单 <span id="researchCount" style="font-weight:700">0</span> 道菜</a>
</div>
<h1>🍜 上海本帮菜 · {category}</h1>
<div class="desc">数据来源：大众点评 · 2026-06-22 · 已收录 <strong>{shown}/{total_available}</strong> 家餐厅{f'（全网共{total_available}家，当前展示前{cap}家）' if total_available > cap else ''} · 仙味楼 R&D 助手</div>
</div>'''

    for idx, (name, shop_id) in enumerate(shops):
        # Load paired data
        paired_data = find_paired(shop_id)

        # Get shop info
        info = get_shop_info(shop_id, name)

        rating = info.get('rating', 0)
        stars = '★' * max(1, round(rating)) if rating else ''

        def sc(s):
            return 'score-high' if (s or 0) >= 4.5 else ('score-mid' if (s or 0) >= 4.0 else '')

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
{f'<span class="award-badge">🏅 {info.get("award","")}</span>' if info.get('award') else ''}
</div>
</div>
<div class="score-grid">
<div class="score-item"><div class="val {sc(info.get("tasteScore"))}">{info.get("tasteScore","")}</div><div class="lbl">口味</div></div>
<div class="score-item"><div class="val {sc(info.get("envScore"))}">{info.get("envScore","")}</div><div class="lbl">环境</div></div>
<div class="score-item"><div class="val {sc(info.get("serviceScore"))}">{info.get("serviceScore","")}</div><div class="lbl">服务</div></div>
<div class="score-item"><div class="val">{info.get("reviewCount","")}</div><div class="lbl">评价数</div></div>
{f'<div class="score-item"><div class="val" style="font-size:13px">{info.get("address","")}</div><div class="lbl">地址</div></div>' if info.get('address') else ''}
</div>'''

        # Dishes
        dishes = paired_data.get('paired', [])[:10] if paired_data and 'paired' in paired_data else []
        if dishes:
            html += '\n<div class="section"><h3>🍽️ 推荐菜 Top 10</h3>\n<div class="dish-grid">'
            for j, d in enumerate(dishes):
                img_tag = f'<img src="{d["img"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=no-img>🍽️</div>\'">'
                hot = '🔥' if j < 3 else ''
                dish_escaped = d["name"].replace("'", "\\'").replace('"', '&quot;')
                name_escaped = name.replace("'", "\\'").replace('"', '&quot;')
                html += f'''
<div class="dish-card">
<div class="img-wrap">{img_tag}</div>
<div class="info">
<div class="dish-name"><span class="rank">{j+1}</span>{d["name"]}</div>
<div class="dish-count">{hot} <span class="select-btn" data-dish="{dish_escaped}" data-shop="{name_escaped}" onclick="toggleDish(this,\'{dish_escaped}\',\'{name_escaped}\')" style="cursor:pointer;margin-left:6px;font-size:14px">☆</span></div>
</div>
</div>'''
            html += '\n</div></div>'

        # Keywords
        keywords = info.get('keywords', [])
        if keywords:
            html += f'\n<div class="section"><h3>💬 评价关键词 <span class="badge">共{len(keywords)}个</span></h3><div class="kw-grid">'
            for kw, cnt in keywords[:20]:
                html += f'<span class="kw-tag">{kw} <span class="cnt">{cnt}</span></span>'
            html += '</div></div>'

        html += '\n</div>\n'

    html += f'''
<div class="footer">
<p>仙味楼 R&D 助手 · 上海本帮菜 {category} · 2026-06-22</p>
</div>
</div>
</body>
</html>'''

    # Write
    fname = f'上海本帮菜_{category}_20260622.html'
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, 'w') as f:
        f.write(html)

    # Also copy to desktop
    desktop_path = os.path.expanduser(f'~/Desktop/{fname}')
    with open(desktop_path, 'w') as f:
        f.write(html)

    print(f'✅ {fname} ({len(shops)}家)')
    return fpath

# Generate all 4 reports
for category, shops in searches.items():
    generate_report(category, shops)

print(f'\n所有报告已生成到: {OUTPUT_DIR}')
print('同时已复制到桌面')
