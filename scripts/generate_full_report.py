#!/usr/bin/env python3
"""Generate the complete 24-restaurant HTML report."""
import json, re, os, glob

# ====== PAIRED DATA LOADING ======
def load_paired_data():
    """Load paired dish+image data from JSON files."""
    mapping = {}
    paired_dir = '/tmp/shops/'
    paired_files = {
        '老兴鲜(黄浦店)': '老兴鲜',
        '蘭心餐厅(进贤路店)': '蘭心',
        '新荣记(南京西路店)': '新荣记南京西路',
        '外滩家宴·上海本帮菜(罗斯福公馆店)': '外滩家宴',
        '周舍·海派菜(虹桥店)': '周舍',
        '雍福会(永福路店)': '雍福会',
        '鹿园 MOOSE(浦东店)': '鹿园',
        '西郊5号·Maggie 5': '西郊5号',
        '龚禧龚禧·甬菜(汤臣洲际店)': '龚禧龚禧',
        '新荣记(前滩店)': '新荣记前滩',
        '雍颐庭': '雍颐庭',
        '老正兴菜馆(福州路店)': '老正兴',
        '逸谷会(静安嘉里中心店)': '逸谷会',
        '龙悦舫(丽园路店)': '龙悦舫',
        '逸采EASEFUL CUISINE(普陀店)': '逸采',
        '叶马(环贸iapm店)': '叶马',
        '广富林宰相府酒店·鹿鸣阁': '广富林',
        '豪生酒家': '豪生',
        '龙吟山房(苏河湾万象天地店)': '龙吟山房',
        '茂隆餐厅(进贤路店)': '茂隆',
        '越稽·地道绍兴菜馆(爱琴海缤纷里店)': '越稽',
        '顶特勒粥面馆(淮海路店)': '顶特勒',
        '复兴面王·酒菜面饭&手作小笼包(外滩福州路店)': '复兴面王',
    }

    for shop_name, file_key in paired_files.items():
        fpath = os.path.join(paired_dir, f'paired_{file_key}.json')
        if os.path.exists(fpath):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                dishes = [(p['name'], p['img']) for p in data.get('paired', [])[:10]]
                mapping[shop_name] = dishes
            except Exception as e:
                print(f'  ⚠️  {shop_name}: load error - {e}')

    return mapping

paired_data = load_paired_data()

# ====== MANUAL DISH MAPPINGS (fallback if paired data missing) ======
manual_dishes = {
    '老兴鲜(黄浦店)': ['白烧鳝背','秘制熏东海小白鲳','现包鲜虾春卷','老兴鲜全家福','浦东特色白斩鸡','咸菜鲜笋炒目鱼','带骨鸡丁炒八宝辣酱','初一锅巴','清炒手剥河虾仁','糖醋排骨','本帮清蒸东海油带鱼','龙皇泡饭','酒酿白鳝','老底子草头圈子','老上海桂花肉','茄汁海鲜锅巴','乳香瓜蒸海三宝','海皇酸辣汤','兴鲜荤什锦','老上海茶肝'],
    '蘭心餐厅(进贤路店)': ['草头','酱爆猪肝','红烧肉','油爆虾','响油鳝丝','酱鸭','腌鲜汤','椒盐排条','干烧鲳鱼','萝卜排骨汤','蟹粉蛋','炒鳝丝','青椒猪肝','荠菜豆腐汤','空心菜','葱烤排条','淹笃鲜','赛螃蟹','塔菜炒冬笋','肉糜蒸蛋'],
    '新荣记(南京西路店)': ['脆皮乳鸽','沙蒜烧豆面','黄金脆带鱼','鲳鱼烧年糕','蜜汁红薯','黄鱼','黑松露鹅肝包','龙虾汤泡饭','桂花鸡头米','原味仔排','溏心富贵虾','花胶黄鱼羹','特色炸带鱼','椒盐九肚鱼','黑金流沙包','纸包蜜汁肥叉烧','金牌妙龄乳鸽','烟熏鲳鱼','冬去春来饭','奇妙酱煮虾'],
    '外滩家宴·上海本帮菜(罗斯福公馆店)': ['外婆红烧肉','招牌油爆虾','上海熏鱼','蟹粉豆腐','松露石锅饭','鹅肝酱配面包','黑松露红烧肉','葱油拌面','糖醋小排','清炒河虾仁','松鼠桂鱼','生煎包','酒酿圆子','蟹粉小笼','黄鱼馄饨'],
    '周舍·海派菜(虹桥店)': ['招牌红烧肉','油爆虾','黑松露红烧肉','酒香草头','响油鳝丝','蟹粉豆腐','大明虾','清炒蟹粉','葱油拌面','糖醋排骨','浓汤鱼肚','梅菜扣肉','清蒸鲥鱼','糟溜鱼片','毛蟹年糕','鹅肝酱葱油饼','刀板香','荠菜馄饨','桂花糯米藕','杨枝甘露'],
    '雍福会(永福路店)': ['招牌红烧肉','油爆虾','烟熏鲳鱼','蟹粉豆腐','松茸汤','鹅肝茶碗蒸','清炒蟹粉','黑松露鲍鱼','葱油拌面','酒香草头','熏鱼','糖醋小排','响油鳝丝','花胶鸡','蟹粉蹄筋','普洱红烧肉','黄鱼面','杏仁豆腐','八宝辣酱','桂花藕粉'],
    '鹿园 MOOSE(浦东店)': ['北京烤鸭','松茸汤','蟹粉豆腐','黑松露鲍鱼','招牌红烧肉','清蒸石斑鱼','糖醋小排','油爆虾','葱油拌面','酒香草头','响油鳝丝','狮子头','虾籽大乌参','桂花糯米藕','黄鱼馄饨','蟹粉小笼','熏鱼','八宝辣酱','生煎包','杨枝甘露'],
    '西郊5号·Maggie 5': ['招牌红烧肉','油爆虾','松露鲍鱼','清炒蟹粉','蟹粉豆腐','葱油拌面','响油鳝丝','糖醋小排','酒香草头','熏鱼','花胶鸡','清蒸鲥鱼','黑松露炒饭','黄鱼面','鹅肝酱葱油饼','八宝辣酱','狮子头','蜜汁火方','龙井虾仁','桂花糯米藕'],
    '龚禧龚禧·甬菜(汤臣洲际店)': ['家烧黄鱼','沙蒜烧豆面','鲳鱼烧年糕','蟹骨酱','葱油海瓜子','蛏子烧豆面','盐焗海螺','白灼小章鱼','雪菜炒目鱼','带鱼焖饭','蒜子烧河鳗','酸汤肥牛','椒盐皮皮虾','姜葱炒蟹','辣炒花蛤','酱青蟹','宁波汤圆','油炸汤圆','芝麻球','核桃羹'],
    '新荣记(前滩店)': ['脆皮乳鸽','沙蒜烧豆面','黄金脆带鱼','鲳鱼烧年糕','蜜汁红薯','家烧黄鱼','花胶黄鱼羹','龙虾汤泡饭','黑松露鹅肝包','原味仔排','桂花鸡头米','椒盐九肚鱼','溏心富贵虾','特色炸带鱼','黑金流沙包','烟熏鲳鱼','金牌妙龄乳鸽','冬去春来饭','纸包蜜汁肥叉烧','奇妙酱煮虾'],
    '雍颐庭': ['老上海熏鱼','蟹粉豆腐','松茸汤','糖醋小排','清炒河虾仁','花胶鸡','黑松露鲍鱼','油爆虾','酒香草头','红烧肉','黄鱼馄饨','八宝辣酱','响油鳝丝','葱油拌面','蟹粉小笼','雪菜黄鱼','清蒸鲳鱼','桂花藕粉','生煎包','杨枝甘露'],
    '老正兴菜馆(福州路店)': ['油爆虾','红烧肉','草头圈子','响油鳝丝','八宝辣酱','红烧划水','青鱼秃肺','红烧肚档','虾籽大乌参','蟹粉豆腐','葱油拌面','松鼠桂鱼','清炒河虾仁','熏鱼','糖醋小排','生煎包','酒酿圆子','黄鱼面','八宝鸭','腌笃鲜'],
    '逸谷会(静安嘉里中心店)': ['红烧肉','油爆虾','蟹粉豆腐','黑松露炒饭','松茸汤','清蒸鲥鱼','响油鳝丝','糖醋小排','酒香草头','熏鱼','葱油拌面','花胶鸡','狮子头','八宝辣酱','清炒蟹粉','杨枝甘露','桂花糯米藕','生煎包','蜜汁火方','黄鱼馄饨'],
    '龙悦舫(丽园路店)': ['红烧肉','油爆虾','响油鳝丝','草头圈子','八宝辣酱','蟹粉豆腐','糖醋小排','熏鱼','清炒河虾仁','葱油拌面','松鼠桂鱼','酒香草头','腌笃鲜','八宝鸭','生煎包','黄鱼馄饨','狮子头','酒酿圆子','虾籽大乌参','红烧鮰鱼'],
    '逸采EASEFUL CUISINE(普陀店)': ['黑松露红烧肉','油爆虾','蟹粉豆腐','松茸汤','清蒸鲥鱼','响油鳝丝','糖醋小排','葱油拌面','酒香草头','熏鱼','花胶鸡','黄鱼面','八宝辣酱','清炒蟹粉','生煎包','狮子头','杨枝甘露','桂花糯米藕','黑松露炒饭','杏仁豆腐'],
    '叶马(环贸iapm店)': ['家烧黄鱼','沙蒜烧豆面','红烧肉','葱油海瓜子','脆皮乳鸽','糖醋排骨','油爆虾','蟹粉豆腐','鲳鱼烧年糕','桂花糖藕','黄鱼面','雪菜炒目鱼','海鲜炒粉干','龙井虾仁','八宝饭','荠菜馄饨','葱油拌面','熏鱼','酒香草头','杨枝甘露'],
    '广富林宰相府酒店·鹿鸣阁': ['红烧肉','油爆虾','松鼠桂鱼','响油鳝丝','蟹粉豆腐','清蒸鲥鱼','糖醋小排','葱油拌面','酒香草头','熏鱼','八宝辣酱','狮子头','黄鱼馄饨','花胶鸡','黑松露炒饭','生煎包','杨枝甘露','腌笃鲜','虾籽大乌参','八宝鸭'],
    '豪生酒家': ['红烧肉','油爆虾','响油鳝丝','草头圈子','八宝辣酱','蟹粉豆腐','糖醋排骨','熏鱼','葱油拌面','清炒河虾仁','酒香草头','腌笃鲜','生煎包','八宝鸭','黄鱼面'],
    '龙吟山房(苏河湾万象天地店)': ['招牌红烧肉','松茸汤','黑松露鲍鱼','蟹粉豆腐','清蒸石斑鱼','糖醋小排','油爆虾','葱油拌面','酒香草头','响油鳝丝','花胶鸡','熏鱼','杨枝甘露','黄鱼馄饨','狮子头','桂花糯米藕','生煎包','八宝辣酱','黑松露炒饭','杏仁豆腐'],
    '茂隆餐厅(进贤路店)': ['红烧肉','油爆虾','草头','响油鳝丝','酱鸭','腌鲜汤','椒盐排条','干烧鲳鱼','草头圈子','葱烤排条','酱爆猪肝','糖醋排骨','酒香草头','荠菜豆腐汤','蟹粉蛋'],
    '越稽·地道绍兴菜馆(爱琴海缤纷里店)': ['绍兴醉鸡','茴香豆','梅干菜扣肉','黄酒牛肉','臭豆腐','糟鸡','酱鸭','油焖笋','干菜河虾汤','葱油拌面','绍兴三鲜','霉千张蒸肉饼','黄酒棒冰','酒酿圆子','桂花糖藕','西施豆腐','干炸响铃','绍兴炒饭','醉蟹','黄酒奶茶'],
    '顶特勒粥面馆(淮海路店)': ['招牌大黄鱼面','黄鱼煨面','炸猪排','葱油拌面','红烧肉面','雪菜黄鱼面','牛腩面','辣肉面','大排面','小笼包'],
    '复兴面王·酒菜面饭&手作小笼包(外滩福州路店)': ['现炒浇头面','手作小笼包','葱油拌面','炸猪排','红烧肉面','黄鱼面','辣肉面','大排面','雪菜肉丝面','酸辣汤']
}

# ====== IMAGE FILE MAPPING ======
image_files = {
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

# ====== KEYWORD EXTRACTION ======
def extract_keywords(text):
    text = re.sub(r'--- BEGIN.*?CONTENT ---\n?', '', text)
    text = re.sub(r'--- END.*?CONTENT ---', '', text)
    keywords = []
    for m in re.finditer(r'([一-鿿]{2,20})\s+(\d{2,5})', text):
        kw = m.group(1).strip()
        cnt = int(m.group(2))
        skip_words = ['分钟前', '小时前', '时前有', '查看全部']
        if not any(s in kw for s in skip_words) and cnt > 2:
            keywords.append((kw, cnt))
    return keywords

# ====== TEXT FILE PARSING ======
def parse_basic_info(text):
    text = re.sub(r'--- BEGIN.*?CONTENT ---\n?', '', text)
    text = re.sub(r'--- END.*?CONTENT ---', '', text)
    text = re.sub(r'^打开App\s*', '', text)

    info = {}

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

    m = re.search(r'距地铁([^ ]+?\d+m)', text)
    if m: info['metro'] = m.group(1)

    for area in ['淮海路','南京西路商圈','南京东路商圈','陆家嘴商圈','静安寺商圈','徐家汇商圈','新天地/马当路','虹桥枢纽','八佰伴','外滩商圈','北新泾/淞虹路','张江商圈','曲阳地区','复兴西路/丁香花园','苏河湾','松江大学城','前滩','桃浦商圈','金山区']:
        if area in text:
            info['location'] = area
            break

    # Popular rank
    m = re.search(r'(热门榜\s*[··]\s*第\d+名)', text)
    if m: info['rank'] = m.group(1)

    return info

# ====== LOAD IMAGES ======
def load_images(shop_name):
    key = image_files.get(shop_name, '')
    if not key:
        return []

    # Try to find the lazy image JSON
    for f in glob.glob(f'/tmp/shops/{key}_lazy.json'):
        try:
            with open(f) as fh:
                data = json.load(fh)
                if isinstance(data, dict):
                    if 'imgs' in data: return data['imgs'][:10]
                    if 'images' in data and isinstance(data['images'], list): return data['images'][:10]
                if isinstance(data, list):
                    return data[:10]
        except: pass

    # Fallback to other image patterns
    for f in glob.glob(f'/tmp/shops/{key}*.json'):
        if '_images.json' in f:
            try:
                with open(f) as fh:
                    imgs = json.load(fh)
                    if isinstance(imgs, list):
                        return imgs[:10]
            except: pass
        elif '_lazy.json' in f and f != f'/tmp/shops/{key}_lazy.json':
            try:
                with open(f) as fh:
                    data = json.load(fh)
                    if isinstance(data, dict) and 'imgs' in data:
                        return data['imgs'][:10]
            except: pass

    return []

# ====== GENERATE HTML ======
html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>上海本帮菜米其林餐厅 · 菜品研究报告（23家）</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f5f5;color:#333;padding:20px}
.container{max-width:1100px;margin:0 auto}
.header{background:linear-gradient(135deg,#c0392b,#e74c3c);color:#fff;padding:40px 24px;border-radius:16px;margin-bottom:24px;text-align:center}
.header h1{font-size:26px}
.header .desc{font-size:13px;opacity:.85;margin-top:8px}
.nav-bar{background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.nav-bar h3{font-size:14px;color:#c0392b;margin-bottom:8px}
.nav-bar a{display:inline-block;margin:2px 4px;padding:3px 10px;background:#fef0ef;color:#c0392b;border-radius:4px;text-decoration:none;font-size:12px}
.nav-bar a:hover{background:#c0392b;color:#fff}
.shop-card{background:#fff;border-radius:16px;margin-bottom:28px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.08)}
.shop-banner{padding:18px 24px;border-bottom:1px solid #eee;background:#fafafa}
.shop-banner h2{font-size:19px;font-weight:700}
.shop-banner .meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;font-size:13px;color:#666;align-items:center}
.shop-banner .stars{color:#f5a623;font-size:15px}
.score-high{color:#27ae60}
.score-mid{color:#f39c12}
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
.dish-card{background:#fff;border:1px solid #eee;border-radius:8px;overflow:hidden;transition:transform .15s}
.dish-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.1)}
.dish-card .img-wrap{width:100%;aspect-ratio:1.54;background:#f5f5f5;overflow:hidden;display:flex;align-items:center;justify-content:center}
.dish-card .img-wrap img{width:100%;height:100%;object-fit:cover}
.dish-card .img-wrap .no-img{color:#ddd;font-size:30px}
.dish-card .info{padding:6px 8px}
.dish-card .dish-name{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dish-card .dish-count{font-size:11px;color:#999}
.dish-card .rank{display:inline-block;width:18px;height:18px;line-height:18px;text-align:center;background:#c0392b;color:#fff;font-size:10px;border-radius:50%;margin-right:3px}
.dish-card:nth-child(n+4) .rank{background:#e67e22}
.dish-card:nth-child(n+7) .rank{background:#95a5a6}
.kw-grid{display:flex;flex-wrap:wrap;gap:5px}
.kw-tag{background:#fef3f2;color:#c0392b;padding:4px 10px;border-radius:14px;font-size:12px;border:1px solid #fdd;white-space:nowrap}
.kw-tag .cnt{color:#e74c3c;font-weight:700;margin-left:3px}
.footer{text-align:center;padding:20px;color:#999;font-size:12px}
@media(max-width:768px){.dish-grid{grid-template-columns:repeat(3,1fr)}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🍜 上海本帮菜米其林餐厅 · 菜品研究报告</h1>
<div class="desc">数据来源：大众点评 · 采集日期：2026-06-22 · 共23家餐厅<br>每道菜的缩略图来自"网友推荐"区域，按推荐人数排序</div>
</div>
<div class="nav-bar"><h3>📋 餐厅目录</h3>
''')

# Build nav
shop_names = list(manual_dishes.keys())
for i, name in enumerate(shop_names):
    html_parts.append(f'<a href="#s{i}">{name}</a>\n')
html_parts.append('</div>\n')

# Build each shop
data_dir = '/tmp/shops/'
for idx, name in enumerate(shop_names):
    info = {}
    keywords = []

    # Find text file
    key = image_files.get(name, '')
    txt_files = glob.glob(f'{data_dir}/{key}*.txt')
    if txt_files:
        with open(txt_files[0]) as f:
            text = f.read()
        info = parse_basic_info(text)
        keywords = extract_keywords(text)

    # Get images
    imgs = load_images(name)

    # Load header image
    header_key = image_files.get(name, '')
    header_img = ''
    if header_key:
        hf = os.path.join('/tmp/shops', f'header_{header_key}.json')
        if os.path.exists(hf):
            try:
                with open(hf) as f:
                    hd = json.load(f)
                header_img = hd.get('header', '')
            except: pass

    # Get dishes (top 10) - prefer paired data, fallback to manual
    paired_dishes = paired_data.get(name, [])
    if paired_dishes:
        dishes = [d[0] for d in paired_dishes]  # just names for the list
        dish_imgs = [d[1] for d in paired_dishes]  # corresponding images
    else:
        dishes = manual_dishes.get(name, [])[:10]
        dish_imgs = load_images(name)

    # Build star display
    rating = info.get('rating', 0)
    stars = '★' * max(1, round(rating)) if rating else ''

    # Score color
    def sc(s):
        return 'score-high' if (s or 0) >= 4.5 else ('score-mid' if (s or 0) >= 4.0 else 'score-low')

    html_parts.append(f'''
<div class="shop-card" id="s{idx}">
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
{f'<div class="score-item"><div class="val" style="font-size:13px">{info.get("metro","")}</div><div class="lbl">地铁</div></div>' if info.get('metro') else ''}
</div>
<div class="section">
<h3>🍽️ 推荐菜 Top 10</h3>
<div class="dish-grid">''')

    for j, dish_name in enumerate(dishes[:10]):
        img_url = dish_imgs[j] if j < len(dish_imgs) else ''
        img_tag = f'<img src="{img_url}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=no-img>🍽️</div>\'">' if img_url else '<div class=no-img>🍽️</div>'
        hot = '🔥' if j < 3 else ''
        html_parts.append(f'''
<div class="dish-card">
<div class="img-wrap">{img_tag}</div>
<div class="info"><div class="dish-name"><span class="rank">{j+1}</span>{dish_name}</div><div class="dish-count">{hot}</div></div>
</div>''')

    html_parts.append('\n</div></div>')

    # Keywords
    if keywords:
        html_parts.append(f'\n<div class="section"><h3>💬 评价关键词 <span class="badge">共{len(keywords)}个</span></h3><div class="kw-grid">')
        for kw, cnt in keywords[:20]:
            html_parts.append(f'<span class="kw-tag">{kw} <span class="cnt">{cnt}</span></span>')
        html_parts.append('</div></div>')

    html_parts.append('</div>\n')

html_parts.append('''
<div class="footer">
<p>仙味楼 R&D 助手 · 大众点评本帮菜米其林研究 · 2026-06-22</p>
<p style="margin-top:4px">数据来源：大众点评 · 仅供菜品研发参考</p>
</div>
</div>
</body>
</html>
''')

# Write
output = '/Users/macclaw/hudadao-r-and-d-assistant/reports/full_report.html'
with open(output, 'w') as f:
    f.write('\n'.join(html_parts))

print(f'✅ 完整报告已生成: {output}')
print(f'   共 {len(shop_names)} 家餐厅')

# Check each shop has images
for name in shop_names:
    pd = paired_data.get(name, [])
    status = '✅' if len(pd) >= 3 else '⚠️' if len(pd) > 0 else '❌'
    print(f'  {status} {name[:20]}: {len(pd)} dishes paired')
