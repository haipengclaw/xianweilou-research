#!/bin/bash
# Helper script to save shop page text to a named file
# Usage: collect_data.sh <shop_name>
# Run after navigating to a Dianping shop page

B="/Users/macclaw/.claude/skills/gstack/browse/dist/browse"
DATA_DIR="/Users/macclaw/hudadao-r-and-d-assistant/data/shops"

mkdir -p "$DATA_DIR"

name="$1"
if [ -z "$name" ]; then
    echo "Usage: collect_data.sh <shop_name>"
    exit 1
fi

# Save text
safe_name=$(echo "$name" | tr '/' '_')
$B text > "$DATA_DIR/${safe_name}.txt" 2>/dev/null
echo "Text saved to: $DATA_DIR/${safe_name}.txt"

# Save dish images JSON
$B js "JSON.stringify(Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 100).map(i => i.currentSrc||i.src).filter(s => s.includes('qcloud.dpfile.com') || s.includes('meituan.net')))" 2>/dev/null > "$DATA_DIR/${safe_name}_images.json"
img_count=$(cat "$DATA_DIR/${safe_name}_images.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "0")
echo "Images saved: $img_count images"
