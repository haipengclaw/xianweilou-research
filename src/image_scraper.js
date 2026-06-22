/**
 * image_scraper.js — 多渠道研发灵感采集引擎
 *
 * 设计理念：
 *   做餐饮研发创新，最有价值的灵感来自两个方向：
 *   1. 小红书：普通用户分享的创意做法、民间智慧、摆盘灵感
 *   2. 大众点评热门菜品：什么菜被推荐最多（不限门店）
 *
 * 运行：npm run scrape
 */

const { chromium } = require('playwright');
const fs = require('fs-extra');
const path = require('path');

const CONFIG_PATH = path.resolve(__dirname, '..', 'config.json');
const config = fs.readJsonSync(CONFIG_PATH);

/* ===================================================================
 * 工具函数
 * =================================================================== */

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function humanPause(page, min = 800, max = 2500) {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  await sleep(delay);
  await page.mouse.move(200 + Math.random() * 800, 200 + Math.random() * 500);
}

async function humanScroll(page, times = 4) {
  for (let i = 0; i < times; i++) {
    await page.evaluate(() => window.scrollBy(0, 600 + Math.random() * 400));
    await humanPause(page, 500, 1200);
  }
}

async function handleCaptcha(page, timeout = 30000) {
  try {
    const modalSelectors = [
      '.login-modal', '.popup-iframe', '.J-verify-popup',
      '[class*="verify"]', '[class*="captcha"]', '#captcha',
    ];
    for (const sel of modalSelectors) {
      const el = await page.$(sel);
      if (el && await el.isVisible()) {
        console.warn('  ⚠️  检测到验证弹窗，请在浏览器中手动完成...');
        await sleep(timeout);
        return true;
      }
    }
  } catch (e) { /* ignore */ }
  return false;
}

/* ===================================================================
 * 城市映射（大众点评）
 * =================================================================== */
const CITY_MAP = { '北京': 2, '上海': 1, '杭州': 3, '宁波': 7, '台州': 179, '苏州': 46, '南京': 45, '广州': 4 };

/* ===================================================================
 * 大众点评 — 热门菜品搜索
 *
 * 不为找门店，为找"什么菜被推荐最多"
 * 搜"宁波菜 推荐菜"、"台州菜 招牌菜"等，提取菜名、价格、图片
 * =================================================================== */

async function scrapeTrendingDishes(browser) {
  console.log('\n===============================================');
  console.log('  🍽️  大众点评 · 热门菜品采集');
  console.log('  目标：找出宁波菜/台州菜/海鲜中被推荐最多的菜');
  console.log('===============================================\n');

  const context = await browser.newContext({
    userAgent: config.browser.user_agent,
    viewport: { width: config.browser.viewport_width, height: config.browser.viewport_height },
  });
  const page = await context.newPage();
  const allDishes = [];
  const seenDishKeys = new Set();
  const cfg = config.dianping_dishes;

  // Cookie 持久化
  const cookiePath = path.resolve(__dirname, '..', 'data', 'dianping_cookies.json');
  if (await fs.pathExists(cookiePath)) {
    const cookies = await fs.readJson(cookiePath);
    await context.addCookies(cookies);
    console.log('  ✅ 已加载大众点评 Cookie');
  }

  // 建立会话
  console.log('  🌐 访问首页建立会话...');
  await page.goto('https://www.dianping.com', { waitUntil: 'networkidle', timeout: 60000 });
  await humanPause(page, 2000, 3000);
  await handleCaptcha(page);
  // 保存 Cookie
  const cookies = await context.cookies();
  await fs.writeJson(cookiePath, cookies, { spaces: 2 });

  for (const city of cfg.cities) {
    const cityId = CITY_MAP[city] || 1;
    let cityDishCount = 0;

    for (const kw of cfg.search_keywords) {
      if (cityDishCount >= cfg.max_dishes) break;
      console.log(`\n📌 [${city}] 搜推荐菜: "${kw}"`);

      try {
        // 先访问城市分类页，建立城市上下文
        if (cityId) {
          await page.goto(`https://www.dianping.com/search/category/${cityId}/10`, {
            waitUntil: 'networkidle', timeout: 30000,
          });
          await humanPause(page, 1000, 2000);
        }

        // 搜索框输入
        const searchInput = await page.$(
          '#search-input, input.search-input, input[class*="search"], ' +
          'input[name="searchWord"], input[placeholder*="搜索"], ' +
          '.search-bar input, form input[type="text"]'
        );

        if (searchInput) {
          await searchInput.click();
          await humanPause(page, 200, 400);
          await searchInput.fill('');
          for (const ch of kw) {
            await page.keyboard.type(ch, { delay: 50 + Math.random() * 80 });
          }
          await humanPause(page, 400, 800);
          await page.keyboard.press('Enter');
          console.log('    🔍 已搜索');
        } else {
          const encoded = encodeURIComponent(kw);
          await page.goto(`https://www.dianping.com/search/keyword/${cityId}/${encoded}`, {
            waitUntil: 'networkidle', timeout: 30000,
          });
        }

        await humanPause(page, 3000, 5000);
        await handleCaptcha(page);

        // 如果页面无结果，保存调试 HTML
        const bodyPreview = await page.evaluate(() => document.body.innerText.slice(0, 300));
        if (bodyPreview.includes('没有找到') || bodyPreview.includes('搜不到')) {
          console.log(`    ℹ️  无结果: "${bodyPreview.slice(0, 60)}..."`);
          continue;
        }

        await humanScroll(page, 5);

        // ---- 解析菜品（通用选择器） ----
        const dishes = await page.evaluate(({ maxItems, city, kw }) => {
          const results = [];

          // 找所有可能包含菜品信息的卡片
          const candidates = document.querySelectorAll(
            '.shop-list li, [class*="shop-item"], [class*="shop-card"], ' +
            '#shop-all-list li, .list-item, [data-shopid], ' +
            '[class*="result"] > div, [class*="item"]'
          );

          candidates.forEach((card) => {
            if (results.length >= maxItems) return;

            const name =
              card.querySelector('.shop-name, .tit, [class*="name"] a, h3 a, h4 a, ' +
                '[class*="shopname"] a, .shopname')
                ?.innerText?.trim() ||
              card.getAttribute('data-shopname') || '';
            if (!name || name.length < 2) return;

            const link = card.querySelector('a[href*="shop"]')?.getAttribute('href') ||
              card.querySelector('a')?.getAttribute('href') || '';
            const shopId = card.getAttribute('data-shopid') || link.match(/shop\/(\d+)/)?.[1] || '';
            if (!shopId) return;

            const rating =
              card.querySelector('.star, [class*="star"], .score')?.getAttribute('title') ||
              card.querySelector('.star, [class*="star"], .score')?.innerText?.trim() || '';

            const priceText = card.querySelector('.price, [class*="price"], .mean-price, .per-person')
              ?.innerText?.trim() || '';
            const priceMatch = priceText.match(/(\d+)/);
            const avgPrice = priceMatch ? parseInt(priceMatch[1]) : 0;

            const awards = [];
            card.querySelectorAll('.badge, .tag, [class*="badge"], [class*="mark"]').forEach(el => {
              const t = el.innerText.trim();
              if (t && t.length < 15) awards.push(t);
            });

            // 提取该店推荐菜（在卡片内找菜品名称）
            const dishNames = [];
            card.querySelectorAll('.recommend-dish, .dish-name, .food-name, [class*="dish"]').forEach(el => {
              const dn = el.innerText.trim();
              if (dn && dn.length < 30) dishNames.push(dn);
            });

            // 提取菜品图片
            const dishImg = card.querySelector('img[src*="img"], img[data-src*="img"]')
              ?.getAttribute('src') ||
              card.querySelector('img[src*="img"], img[data-src*="img"]')
                ?.getAttribute('data-src') || '';

            results.push({
              shopId, shopName: name,
              link: link.startsWith('http') ? link : `https://www.dianping.com${link}`,
              rating, avgPrice, awards,
              recommendedDishes: dishNames,
              dishImage: dishImg.startsWith('//') ? 'https:' + dishImg : dishImg,
              city, keyword: kw,
              source: '大众点评',
              scrapedAt: new Date().toISOString(),
            });
          });

            return results;
          }, { maxItems: cfg.max_dishes, city, kw });

        // 过滤已见
        const fresh = dishes.filter(d => {
          const k = `${d.shopId}:${d.shopName}`;
          if (seenDishKeys.has(k)) return false;
          seenDishKeys.add(k);
          return true;
        });

        cityDishCount += fresh.length;
        allDishes.push(...fresh);
        console.log(`    📊 采集到 ${fresh.length} 家门店（共 ${dishes.length} 结果）`);

        await sleep(cfg.sleep_between_requests_ms);
      } catch (err) {
        console.error(`    ❌ 出错: ${err.message}`);
      }
    }
  }

  await page.close();
  await context.close();

  allDishes.sort((a, b) => parseFloat(b.rating) || 0 - parseFloat(a.rating) || 0);
  allDishes.forEach(s => {
    s.isBichibang = s.awards?.some(a => a.includes('必吃'));
    s.isHeizhenzhu = s.awards?.some(a => a.includes('黑珍珠'));
  });

  console.log(`\n📊 大众点评共采集 ${allDishes.length} 条门店数据\n`);
  return allDishes;
}

/* ===================================================================
 * 小红书 — 研发灵感笔记采集
 * 搜索研发导向关键词：创意做法、摆盘灵感、平价高级感
 * =================================================================== */

async function scrapeXiaohongshu(browser) {
  console.log('\n===============================================');
  console.log('  📕 小红书 · 研发灵感笔记采集');
  console.log('  目标：创意做法、摆盘灵感、平价高级感');
  console.log('===============================================\n');

  const context = await browser.newContext({
    userAgent: config.browser.user_agent,
    viewport: { width: config.browser.viewport_width, height: config.browser.viewport_height },
  });
  const page = await context.newPage();
  const allNotes = [];
  const seenUrls = new Set();

  const cookiesPath = path.resolve(__dirname, '..', config.xiaohongshu.cookies_file);
  if (await fs.pathExists(cookiesPath)) {
    const cookies = await fs.readJson(cookiesPath);
    await context.addCookies(cookies);
    console.log('  ✅ 已加载小红书 Cookie');
  } else {
    console.warn('  ⚠️  未找到 Cookie，打开首页请手动登录...');
    await page.goto('https://www.xiaohongshu.com', { waitUntil: 'networkidle', timeout: 60000 });
    console.warn('  🔑 扫码登录（45秒）...');
    await sleep(45000);
    const cookies = await context.cookies();
    await fs.writeJson(cookiesPath, cookies, { spaces: 2 });
    console.log('  💾 已保存 Cookie');
  }

  for (const kw of config.xiaohongshu.search_keywords) {
    console.log(`\n🔍 搜索: "${kw}"`);
    try {
      await page.goto(
        `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(kw)}`,
        { waitUntil: 'networkidle', timeout: 60000 },
      );
      await humanPause(page, 2000, 4000);

      // 滚动加载
      for (let i = 0; i < 6; i++) {
        await page.evaluate(() => window.scrollBy(0, 1000));
        await humanPause(page, 800, 1500);
      }

      const notes = await page.evaluate((maxItems) => {
        const items = [];
        const cards = document.querySelectorAll(
          '.note-item, a.note-item, [class*="note"] a[href*="explore"], ' +
          'section.note, article[class*="note"]'
        );
        cards.forEach(c => {
          if (items.length >= maxItems) return;
          const title = c.querySelector('.title, .note-title, [class*="title"]')?.innerText?.trim() ||
            c.getAttribute('title') || '';
          const cover = c.querySelector('img')?.getAttribute('src') ||
            c.querySelector('img')?.getAttribute('data-src') || '';
          const likes = c.querySelector('.like-count, .count, [class*="like"]')?.innerText?.trim() || '';
          const author = c.querySelector('.author, .username, [class*="author"]')?.innerText?.trim() || '';
          const link = c.getAttribute('href') || c.querySelector('a')?.getAttribute('href') || '';
          if (title || cover) {
            items.push({
              title, coverUrl: cover.startsWith('//') ? 'https:' + cover : cover,
              likeCount: likes, author, keyword: kw,
              noteUrl: link.startsWith('http') ? link : `https://www.xiaohongshu.com${link}`,
              source: '小红书', scrapedAt: new Date().toISOString(),
            });
          }
        });
        return items;
      }, config.xiaohongshu.notes_to_scrape);

      console.log(`    ✅ ${notes.length} 条笔记`);

      // 正文提取（前 10 条）
      for (let i = 0; i < Math.min(notes.length, 10); i++) {
        const n = notes[i];
        if (n.noteUrl?.includes('explore')) {
          try {
            await page.goto(n.noteUrl, { waitUntil: 'networkidle', timeout: 20000 });
            await humanPause(page, 1000, 2000);
            n.bodyText = await page.evaluate(() => {
              const el = document.querySelector('.note-desc, .desc, [class*="desc"], ' +
                '.content, [class*="content"] span, #detail-desc');
              return el?.innerText?.trim() || '';
            });
          } catch (e) { n.bodyText = ''; }
        }
      }

      const fresh = notes.filter(n => {
        if (seenUrls.has(n.noteUrl)) return false;
        seenUrls.add(n.noteUrl);
        return true;
      });
      allNotes.push(...fresh);
    } catch (err) {
      console.error(`    ❌ 出错: ${err.message}`);
    }
  }

  await page.close();
  await context.close();
  console.log(`\n📊 小红书共 ${allNotes.length} 条不重复笔记\n`);
  return allNotes;
}

/* ===================================================================
 * 主入口
 * =================================================================== */

async function main() {
  console.log('');
  console.log('╔══════════════════════════════════════════════╗');
  console.log('║   🐟 胡叨叨 · 新菜研发灵感采集引擎         ║');
  console.log('╠══════════════════════════════════════════════╣');
  console.log('║   小红书 → 创意做法 · 摆盘 · 平价高级感   ║');
  console.log('║   大众点评 → 热门推荐菜 · 趋势分析         ║');
  console.log('╚══════════════════════════════════════════════╝');
  console.log('');

  const browser = await chromium.launch({
    headless: config.browser.headless,
    slowMo: config.browser.slow_mo,
  });

  const result = { dianping: [], xiaohongshu: [] };

  try {
    // ---- 大众点评热门菜品 ----
    console.log('🍽️  采集大众点评热门推荐菜...\n');
    result.dianping = await scrapeTrendingDishes(browser);

    // ---- 小红书研发灵感 ----
    console.log('\n📕 采集小红书研发灵感笔记...\n');
    result.xiaohongshu = await scrapeXiaohongshu(browser);

  } finally {
    await browser.close();
  }

  // 保存
  await fs.ensureDir(path.resolve(__dirname, '..', 'data'));
  await fs.writeJson(
    path.resolve(__dirname, '..', config.output.raw_data_path),
    result, { spaces: 2 },
  );

  console.log('\n╔══════════════════════════════════════════════╗');
  console.log('║   ✅ 采集完成！                             ║');
  console.log('╠══════════════════════════════════════════════╣');
  console.log(`║   大众点评菜品数据: ${result.dianping.length} 条`);
  console.log(`║   小红书灵感笔记:   ${result.xiaohongshu.length} 篇`);
  console.log('╚══════════════════════════════════════════════╝');
  console.log(`\n📦 ${config.output.raw_data_path}\n`);

  return result;
}

if (require.main === module) {
  main().catch(err => { console.error('\n❌ 错误:', err); process.exit(1); });
}

module.exports = { scrapeTrendingDishes, scrapeXiaohongshu, main };
