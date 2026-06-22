#!/usr/bin/env python3
"""Save all search results and generate the combined report."""
import json, os

data = {
    '黑珍珠': [
        '上海滩餐厅(BFC外滩金融中心店)', '福1088', '老兴鲜(黄浦店)', '福1015(愚园路店)',
        '西郊5号·Maggie 5', '甬府·北外滩', '荣府宴(南阳路店)', '永·江臻(思南公馆店)',
        '随堂里', '鹿园 MOOSE(长宁店)', '南麓·荟馆(国金中心店)', '醉东Oriental House(静安嘉里中心店)',
        '海味观(老西门店)', '中国菜·头灶', '福廬 FULL HOUSE'
    ],
    '必吃榜': [
        '人和馆·上海菜(徐汇店)', '兴兴·海派本帮菜', 'HOMES上海本帮菜(襄阳公园店)',
        '南麓·浙里(外滩店)', '圆苑(淮海路店)', '新苑私房菜·本帮菜(嘉善路店)',
        '帥帥精致家常味(长乐路店)', '聪菜馆(六合大厦店)', '吉品小鲜Jhouse(静安店)',
        '钱塘秋荷·新江浙菜(大华店)', '绿雅酒家(江西中路店)', '瑞福园联谊餐室(茂名南路店)',
        '荟廷·晶萃(陆家嘴尚悦湾店)', '玫瑰厅上海菜(兴国路店)', '沪碟·摩登时代(虹口店)'
    ],
    '排队': [
        '品筵•本帮菜•海鲜(中华路店)', '兴兴·海派本帮菜', '沪上馨和小馆·海派上海菜(新会路店)',
        '沪上馨和小馆•海派上海菜(四川北路店)', '福源沁本帮江浙菜(静安店)', '权茂上海菜(南京东路店)',
        '醉庐·新上海菜(鑫耀·光环Live店)', '吉品小鲜Jhouse(静安店)', '醉庐·新上海菜(环球港店)',
        '妈妈家·本帮菜(蒙自东路店)', '御延公馆·上海菜(第一百货店)', '和记小菜·精菜坊(金虹桥店)',
        '醉庐·新上海菜(长宁龙之梦店)', '醉庐·新上海菜(天山汇金店)', '钱珑·江浙菜(真如大都会店)'
    ],
    '老字号': [
        '人和馆·上海菜(徐汇店)', '和记小菜(九亭店)', '老兴鲜(黄浦店)',
        '外滩家宴·上海本帮菜(罗斯福公馆店)', '转角·老弄堂上海菜(淮海路店)',
        '沪上馨和小馆·海派上海菜(新会路店)', '兴兴·海派本帮菜', 'HOMES上海本帮菜(襄阳公园店)',
        '荣福轩·本帮菜.粤菜(静安寺洋房店)', '荣申府·本帮菜.粤菜(延安路静安寺店)',
        '上海老饭店(豫园店)', '圆苑(淮海路店)', '老吉士酒家(天平路店)', '润苑(徐汇店)',
        '荣申府·本帮菜.粤菜(四安里古建店)'
    ]
}

# Save search data
out = {'searches': data}
with open('/Users/macclaw/hudadao-r-and-d-assistant/data/search_results.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# Count unique restaurants
all_shops = set()
for cat, shops in data.items():
    for s in shops:
        all_shops.add(s)

print(f'Categories: {len(data)}')
print(f'Total entries: {sum(len(v) for v in data.values())}')
print(f'Unique restaurants: {len(all_shops)}')
for cat, shops in data.items():
    print(f'  {cat}: {len(shops)}')
