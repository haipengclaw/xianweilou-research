"""Update generate_full_report.py to include header images in banners."""
import json, os

script_path = '/Users/macclaw/hudadao-r-and-d-assistant/scripts/generate_full_report.py'

with open(script_path, 'r') as f:
    content = f.read()

# Add header image loading code after "paired_data = load_paired_data()"
old_header_load = "# Load header image\n    header_key = image_files.get(name, '')"
if old_header_load in content:
    print("Header loading already exists")
else:
    # Insert header image loading before "paired_dishes = paired_data.get(name, [])"
    insert_point = content.find("paired_dishes = paired_data.get(name, [])")
    if insert_point > 0:
        header_code = '''
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

'''
        content = content[:insert_point] + header_code + content[insert_point:]
        print("Header loading code inserted")

# Replace the banner HTML template
# Find: <div class="shop-card" id="s{idx}">\n<div class="shop-banner">\n<h2>{idx+1}. {name}</h2>
old_banner = '''\t<div class="shop-banner">
\t<h2>{idx+1}. {name}</h2>
\t<div class="meta">
\t<span class="stars">{stars}</span>
\t<span class="{sc(rating)}" style="font-weight:700;font-size:16px">{rating}</span>
\t<span>|</span><span class="price-tag">{info.get(\'price\',\'\')}</span>
\t<span>|</span><span>{info.get(\'category\',\'\')}</span>
\t{f\'<span>|\U0001f4cd {info.get("location","")}</span>\' if info.get(\'location\') else \'\'}
\t{f\'<span class="award-badge">\U0001f3c5 {info.get("award","")}</span>\' if info.get(\'award\') else \'\'}
\t</div>
\t</div>'''

new_banner = '''\theader_img_div = \'\'
\tif header_img:
\t    header_img_div = f\'<div style="flex-shrink:0;width:60px;height:60px;border-radius:10px;overflow:hidden;background:#f0f0f0;box-shadow:0 2px 6px rgba(0,0,0,.08)"><img src="{header_img}" style="width:100%;height:100%;object-fit:cover" loading="lazy" onerror="this.parentElement.style.display=\\\\\\"none\\\\\\""></div>\'

\thtml_parts.append(f\'''
<div class="shop-card" id="s{idx}">
<div class="shop-banner" style="display:flex;align-items:center;gap:14px">
{header_img_div}
<div style="flex:1;min-width:0">
<h2 style="font-size:17px;margin-bottom:2px">{idx+1}. {name}</h2>
<div class="meta" style="margin-top:2px">
<span class="stars">{stars}</span>
<span class="{sc(rating)}" style="font-weight:700;font-size:16px">{rating}</span>
<span>|</span><span class="price-tag">{info.get(\'price\',\'\')}</span>
<span>|</span><span>{info.get(\'category\',\'\')}</span>
{f\'<span>|\U0001f4cd {info.get("location","")}</span>\' if info.get(\'location\') else \'\'}
{f\'<span class="award-badge">\U0001f3c5 {info.get("award","")}</span>\' if info.get(\'award\') else \'\'}
</div>
</div>
</div>\')'''

if old_banner in content:
    content = content.replace(old_banner, new_banner)
    print("Banner template replaced")
else:
    # Try to find the exact pattern
    idx = content.find('<div class="shop-banner">')
    if idx > 0:
        print(f"Found 'shop-banner' at position {idx}")
        print("Context:", content[idx:idx+300])
    else:
        print("Could not find shop-banner in file")

with open(script_path, 'w') as f:
    f.write(content)

print("Done")
