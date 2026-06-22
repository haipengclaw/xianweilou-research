#!/usr/bin/env python3
"""
Extract lazyload images paired with dish names from Dianping pages.
Run this on each shop page via the browse tool JS.
"""
import json, sys

# JS to run on each shop page
JS_CODE = '''
// Scroll to trigger lazy loading
const sc = document.querySelector('.scrolldishPics-pc');
if (sc) { sc.scrollLeft = 500; }

// Wait for lazy images to load, then extract
setTimeout(() => {
  const container = document.querySelector('.scrolldishPics-pc') || document.querySelector('.dishPics');
  if (!container) { console.log(JSON.stringify({error: "no container found"})); return; }

  // Extract lazyload images (these are the correct dish thumbnails)
  const lazyImgs = container.querySelectorAll('.lazyload-image');
  const images = [];
  lazyImgs.forEach(el => {
    const bg = el.style.backgroundImage;
    if (bg && bg !== 'none') {
      const url = bg.replace(/^url\\(["']?|["']?\\)$/g, '').split('?')[0];
      images.push(url);
    }
  });

  // Extract dish names from the name container
  const nameContainer = container.querySelector('.dishNameContainer');
  const names = [];
  if (nameContainer) {
    nameContainer.querySelectorAll('.dishName, [class*=dishName]').forEach(el => {
      const t = (el.textContent || '').trim();
      if (t && t.length >= 2) names.push(t);
    });
  }

  // Extract recommend counts
  const allText = document.body.innerText;
  const counts = [];
  // Find the section with "网友推荐(NNN)"
  const recMatch = allText.match(/网友推荐\\(\\d+\\).*?(?:去大众点评App查看全部|\\n)/);
  if (recMatch) {
    const section = recMatch[0];
    const countMatches = section.matchAll(/(\\d+)人推荐/g);
    for (const m of countMatches) {
      counts.push(parseInt(m[1]));
    }
  }

  console.log(JSON.stringify({
    shopId: window.location.href.match(/shop\\/([^\\/?#]+)/)?.[1] || '',
    images: images.slice(0, 15),
    names: names.slice(0, 15),
    counts: counts.slice(0, 15)
  }));
}, 600);
'''

def generate_extraction_js():
    """Generate the JS code to run on each shop page."""
    return JS_CODE

if __name__ == '__main__':
    print(JS_CODE)
