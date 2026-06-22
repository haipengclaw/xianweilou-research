#!/bin/bash
# Batch extract paired data for new restaurants
# Usage: pass shop IDs as arguments
B="/Users/macclaw/.claude/skills/gstack/browse/dist/browse"

for shop_id in "$@"; do
    echo "=== Processing $shop_id ==="
    $B goto "https://www.dianping.com/shop/$shop_id" 2>/dev/null
    sleep 3
    $B js "const sc=document.querySelector('.scrolldishPics-pc');if(sc)sc.scrollLeft=500;" 2>/dev/null
    sleep 2
    $B js "
const c=document.querySelector('.scrolldishPics-pc');
if(!c){JSON.stringify({error:'no container',id:'$shop_id'})}
else {
  const imgs=[];c.querySelectorAll('.lazyload-image').forEach(el=>{const bg=el.style.backgroundImage;if(bg&&bg!=='none')imgs.push(bg.replace(/^url\\([\"']?|[\"']?\\)$/g,'').split('?')[0]);});
  const nc=c.querySelector('.dishNameContainer');const names=[];if(nc){nc.querySelectorAll('.dishName,[class*=dishName]').forEach(el=>{const t=(el.textContent||'').trim();if(t&&t.length>=2)names.push(t);});}
  const paired=[];for(let i=0;i<Math.min(imgs.length,names.length);i++){paired.push({rank:i+1,name:names[i],img:imgs[i]});}
  JSON.stringify({id:'$shop_id',count:imgs.length,paired});
}
" 2>/dev/null | tee /tmp/shops/p_${shop_id}.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'  {d.get(\"id\",\"?\")}: {d.get(\"count\",0)} dishes')" 2>/dev/null
    echo "---"
done
