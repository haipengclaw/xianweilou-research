#!/usr/bin/env python3
"""
Parse Dianping shop detail page text and extract structured data.
"""
import re, json, sys

def parse_shop_text(text):
    data = {}

    # Clean text
    text = re.sub(r'--- BEGIN.*?CONTENT \(source:.*?\) ---\n?', '', text)
    text = re.sub(r'--- END.*?CONTENT ---', '', text)
    text = re.sub(r'^打开App\s*', '', text)
    text = text.strip()

    # --- BASIC INFO from first chunk ---
    # Extract from the dense first line
    # Format: NAME★★★★★RATINGREVIEW_COUNT条¥PRICE/人LOCATIONCATEGORY口味:X环境:X服务:X

    # Rating: find the first float after ★★★★★ (or ★★ etc)
    rating_match = re.search(r'★+\s*([\d.]+)\s*(\d+)\s*条', text)
    if rating_match:
        data['rating'] = float(rating_match.group(1))

    # Review count
    review_match = re.search(r'(\d+)\s*条评价', text)
    if review_match:
        data['reviewCount'] = int(review_match.group(1))

    # Price
    price_match = re.search(r'¥(\d+)', text)
    if price_match:
        data['price'] = '¥' + price_match.group(1)

    # Category
    cat_match = re.search(r'(?:¥\d+/\w+)\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if not cat_match:
        cat_match = re.search(r'/(?:人)?\s*(本帮菜|苏浙菜|浙菜|淮扬菜|特色菜|面馆|粤菜|江浙菜)', text)
    if cat_match:
        data['category'] = cat_match.group(1)

    # Scores
    score_match = re.search(r'口味:\s*([\d.]+)\s+环境:\s*([\d.]+)\s+服务:\s*([\d.]+)', text)
    if score_match:
        data['tasteScore'] = float(score_match.group(1))
        data['envScore'] = float(score_match.group(2))
        data['serviceScore'] = float(score_match.group(3))

    # Award
    award_match = re.search(r'(\d{4}上榜[^ ]+)', text)
    if award_match:
        data['award'] = award_match.group(1)

    # Address - look for pattern "路XX号XX商场X楼" or similar
    addr_match = re.search(r'([一-鿿]+路[一-鿿0-9]+号[一-鿿0-9]*(?:商场|广场|大厦|中心|楼|馆|店)?)', text)
    if addr_match:
        data['address'] = addr_match.group(1)

    # Business hours
    hours_match = re.search(r'(\d+:\d+开始营业)', text)
    if hours_match:
        data['hours'] = hours_match.group(1)

    # Metro
    metro_match = re.search(r'距地铁(\d+号线[一-鿿]+地铁站[一-鿿0-9]+口\d+m)', text)
    if metro_match:
        data['metro'] = metro_match.group(1)

    # Location area
    for area in ['淮海路', '南京西路商圈', '南京东路商圈', '陆家嘴商圈', '静安寺商圈',
                 '徐家汇商圈', '新天地/马当路', '虹桥枢纽', '八佰伴', '外滩商圈',
                 '北新泾/淞虹路', '张江商圈', '曲阳地区', '复兴西路/丁香花园',
                 '苏河湾', '松江大学城', '前滩', '桃浦商圈', '金山区',
                 '长寿路商圈', '中山公园', '西藏北路', '打浦桥', '老西门',
                 '虹口足球场', '人民广场', '世纪大道', '天山', '万体馆',
                 '肇嘉浜路', '城隍庙', '洋泾', '御桥', '江桥', '七宝商圈',
                 '北蔡商圈', '国家会展中心', '中山中路', '衡山路', '静安寺']:
        if area in text:
            data['location'] = area
            break

    # --- RECOMMENDED DISHES ---
    # Find the line containing "推荐菜" and extract dish counts + names
    dishes_section = re.search(r'推荐菜.*?去大众点评App查看全部', text, re.DOTALL)
    if dishes_section:
        section = dishes_section.group(0)

        # Find all counts: "533人推荐" etc
        counts = [int(m) for m in re.findall(r'(\d+)人推荐', section)]

        # Find dish names - they appear after the last count
        last_count_end = 0
        for m in re.finditer(r'\d+人推荐', section):
            last_count_end = m.end()

        dish_text = section[last_count_end:]
        # Remove trailing text
        dish_text = re.sub(r'去大众点评App查看全部.*', '', dish_text)
        dish_text = dish_text.strip()

        # Split concatenated Chinese dish names
        # Try to split by matching individual dish name patterns
        # Common dish patterns: 2-12 Chinese chars, can include · and brackets
        # Approach: match progressively shorter sequences
        dish_text_clean = dish_text.strip()

        # First try: find dish names by looking for patterns with known suffixes
        # Common dish suffixes/patterns in Chinese cuisine
        dish_suffixes = ['背', '鲳', '卷', '福', '鸡', '鱼', '酱', '巴', '仁', '骨',
                        '饭', '鳝', '子', '肉', '煲', '汤', '锦', '肝', '蟹', '虾',
                        '鸭', '参', '蹄', '翅', '肚', '菇', '笋', '豆', '羹', '丝',
                        '片', '块', '条', '段', '丁']
        dish_prefixes = ['白烧', '秘制', '现包', '浦东', '咸菜', '带骨', '初一',
                        '清炒', '糖醋', '本帮', '龙皇', '酒酿', '老底子', '老上海',
                        '茄汁', '乳香', '海皇', '兴鲜']

        # Try to find individual dish names by matching known patterns
        # Each dish typically: prefix? + chars + suffix
        # Simple split by finding boundaries where a new dish starts
        # A new dish often starts with a known prefix or a verb/ingredient

        # Alternative: just match all Chinese char sequences and split intelligently
        # by looking for common dish-starting characters
        dish_starts = ['白', '秘', '现', '老', '浦', '咸', '带', '初', '清', '糖',
                      '本', '龙', '酒', '茄', '乳', '海', '兴', '冰', '芝', '奶',
                      '招', '特', '招', '极', '顶', '风', '经', '传', '古', '新',
                      '鲜', '原', '金', '银', '玉', '宝', '珍', '翠', '红', '绿']

        # Simple approach: extract all consecutive Chinese char sequences
        # Then try to split longer ones at dish-starting characters
        raw_names = re.findall(r'[一-鿿·()（）]{2,}', dish_text_clean)

        expanded = []
        for name in raw_names:
            if len(name) <= 12:
                expanded.append(name)
            else:
                # Try to split at dish-starting characters
                current = ''
                for ch in name:
                    current += ch
                    if ch in dish_suffixes and len(current) >= 2:
                        if len(current) <= 12:
                            expanded.append(current)
                            current = ''
                        else:
                            # Force split
                            expanded.append(current)
                            current = ''
                if current:
                    expanded.append(current)

        # Filter and remove duplicates
        seen = set()
        dishes = []
        skip_words = ['代金券', '团购套餐', '午市双人', '推荐菜', '查看更多',
                     '网友推荐', '菜单', '评价', '查看全部', '优惠', '抢购',
                     '折', '随时退', '过期自动退', '仅限大堂', '周一至周日',
                     '用户头像', '默认图', '广告', '小伙伴']

        for name in expanded:
            name = name.strip()
            if not name or len(name) < 2:
                continue
            if any(skip in name for skip in skip_words):
                continue
            if name in seen:
                continue
            # Skip numeric-heavy names
            if sum(1 for c in name if c.isdigit()) > len(name) * 0.3:
                continue
            seen.add(name)
            dishes.append(name)

        data['dishes'] = []
        for i, name in enumerate(dishes):
            count = counts[i] if i < len(counts) else 0
            data['dishes'].append({'name': name, 'recommendCount': count})

    # --- REVIEW KEYWORDS ---
    keywords = []
    # Match patterns like "白烧鳝背招牌菜 2609"
    kw_matches = re.findall(r'([一-鿿]{2,20}(?:招牌菜|搭配菜|消费|菜馆|推荐|新鲜|果盘|环境|排队|停车|服务|包厢|菜品|味道|价格|分量|位置|装修|卫生|交通|性价比|体验|口感|食材|卖相|人气|特色|优惠|最低|建议|整洁|海鲜|招牌))\s+(\d{2,5})', text)
    for kw in kw_matches:
        keywords.append({'keyword': kw[0], 'count': int(kw[1])})
    if keywords:
        data['reviewKeywords'] = keywords

    # --- USER REVIEWS ---
    reviews = []
    # Pattern: username on one line, "N天前" on next, optional "超预期" + optional price, then review text
    # Find all review blocks
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Check if this line looks like a username
        user_match = re.match(r'^([a-zA-Z0-9_一-鿿]{2,20})$', line)
        if user_match:
            user = user_match.group(1)
            # Check next line for time
            if i + 1 < len(lines):
                time_match = re.match(r'^(\d+[天时]前)$', lines[i+1].strip())
                if time_match:
                    date = time_match.group(1)
                    sentiment = ''
                    price = 0
                    review_text = ''

                    # Check line after for sentiment + price
                    if i + 2 < len(lines):
                        third_line = lines[i+2].strip()
                        sent_match = re.match(r'(超预期|好评|不错|推荐|满意)?\s*(?:¥(\d+))?', third_line)
                        if sent_match:
                            sentiment = sent_match.group(1) or ''
                            price = int(sent_match.group(2)) if sent_match.group(2) else 0
                            # Review text starts from line i+3
                            if i + 3 < len(lines):
                                review_text = lines[i+3].strip()[:300]
                        else:
                            # Third line might be review text directly
                            review_text = third_line[:300]

                    # Get review text if we haven't already
                    if not review_text and i + 2 < len(lines):
                        review_text = lines[i+2].strip()[:300]

                    if len(review_text) > 10:
                        reviews.append({
                            'user': user,
                            'date': date,
                            'sentiment': sentiment,
                            'price': price,
                            'text': review_text[:300]
                        })
                    i += 3
                    continue
        i += 1

    data['reviews'] = reviews[:3]

    return data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 extract_shop_data.py <text_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        text = f.read()

    data = parse_shop_text(text)
    print(json.dumps(data, ensure_ascii=False, indent=2))
