/**
 * index.js — 胡叨叨新菜研发AI助手 一键入口
 *
 * 流程：抓取灵感数据 → AI 多模态分析 → 生成 HTML 报告
 *
 * 运行：
 *   npm run research （全流程）
 *   npm run scrape   （仅采集）
 *   npm run analyze  （仅分析）
 *   npm run render   （仅报告）
 */

const fs = require('fs-extra');
const path = require('path');

const CONFIG_PATH = path.resolve(__dirname, '..', 'config.json');

function checkConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error('❌ 未找到 config.json');
    process.exit(1);
  }
  const config = fs.readJsonSync(CONFIG_PATH);
  if (!config.llm?.api_key || config.llm.api_key.length < 10) {
    console.error('❌ 请在 config.json 中配置有效的 llm.api_key');
    process.exit(1);
  }
  if (!config.llm?.api_base_url || config.llm.api_base_url.length < 10) {
    console.error('❌ 请在 config.json 中配置 llm.api_base_url');
    process.exit(1);
  }
  return config;
}

async function main() {
  console.log('');
  console.log('╔═══════════════════════════════════════════════╗');
  console.log('║                                               ║');
  console.log('║   🐟 胡叨叨 · 新菜研发 AI 助手              ║');
  console.log('║   Hudadao R&D Assistant                      ║');
  console.log('║                                               ║');
  console.log('║   灵感采集 → AI 分析 → 研发报告             ║');
  console.log('║                                               ║');
  console.log('╚═══════════════════════════════════════════════╝');
  console.log('');

  checkConfig();
  const args = process.argv.slice(2);
  const runAll = args.includes('--all') || args.length === 0;
  const scrapeOnly = args.includes('--scrape-only');
  const analyzeOnly = args.includes('--analyze-only');
  const renderOnly = args.includes('--render-only');

  try {
    if (runAll || scrapeOnly) {
      console.log('📡 [1/3] 采集研发灵感数据...\n');
      const scraper = require('./image_scraper');
      await scraper.main();
      console.log('');
    }

    if (runAll || analyzeOnly) {
      if (scrapeOnly) { console.log('⏭️  跳过分析'); }
      else {
        console.log('🧠 [2/3] MiniMax 多模态分析...\n');
        const analyzer = require('./visual_analyzer');
        await analyzer.main();
        console.log('');
      }
    }

    if (runAll || renderOnly) {
      if (scrapeOnly || analyzeOnly) { console.log('⏭️  跳过报告'); }
      else {
        console.log('🎨 [3/3] 生成 HTML 报告...\n');
        const renderer = require('./renderer');
        const htmlPath = await renderer.main();
        console.log(`   🌐 ${htmlPath}\n`);
      }
    }

    console.log('✨ 完成！');
    console.log('');
  } catch (err) {
    console.error('\n❌ 错误:', err);
    process.exit(1);
  }
}

main();
