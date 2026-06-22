/**
 * visual_analyzer.js — AI 多模态视觉研发分析模块（MiniMax-M3）
 *
 * 职责：
 *   1. 读取 raw_research_data.json（含竞品门店、菜品、小红书笔记）
 *   2. 下载图片 → base64 → 调用 MiniMax-M3 多模态 API
 *   3. 产出结构化的 Markdown 研发报告
 *
 * MiniMax-M3 使用 OpenAI 兼容接口（api.minimax.chat/v1），
 * 文本与多模态共用一个模型。图片通过 base64 data URI 传入。
 *
 * 运行方式：npm run analyze  或  node src/visual_analyzer.js
 */

const fs = require('fs-extra');
const path = require('path');
const axios = require('axios');
const OpenAI = require('openai');

const CONFIG_PATH = path.resolve(__dirname, '..', 'config.json');
const config = fs.readJsonSync(CONFIG_PATH);

/* ===================================================================
 * 工具函数
 * =================================================================== */

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

/** 下载图片为 base64 */
async function downloadImageAsBase64(url) {
  if (!url || url.length < 10) return null;
  const cleanUrl = url.replace(/_\d+x\d+(\.\w+)$/, '$1');

  try {
    const resp = await axios.get(cleanUrl, {
      responseType: 'arraybuffer',
      timeout: 15000,
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' +
          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        Referer: 'https://www.dianping.com/',
      },
    });

    const contentType = resp.headers['content-type'] || 'image/jpeg';
    const base64 = Buffer.from(resp.data).toString('base64');
    return { contentType, base64 };
  } catch (err) {
    console.warn(`  ⚠️  图片下载失败: ${err.message.slice(0, 60)}`);
    return null;
  }
}

/* ===================================================================
 * LLM 客户端初始化（OpenAI 兼容接口）
 * =================================================================== */

function createLLMClient() {
  const llmCfg = config.llm;
  return new OpenAI({
    apiKey: llmCfg.api_key,
    baseURL: llmCfg.api_base_url,
    dangerouslyAllowBrowser: false,
  });
}

/* ===================================================================
 * 系统提示词
 * =================================================================== */

const SYSTEM_PROMPT = `你是一位拥有20年精致粤菜/台州菜研发经验的总厨，兼餐饮品牌视觉总监。
请根据传入的菜品/笔记图片以及相关文本，为"胡叨叨（海鲜小馆与宁波台州菜创新，定位高质平价）"分析以下内容：

## 1. 视觉与呈现分析
分析该菜品的摆盘技巧、色彩搭配、器皿选择以及它是如何营造"高级感/品质感"的。

## 2. 研发创新点提炼
这道菜在食材搭配、烹饪技法（如煎、蒸、焖、烤的创新应用）上有什么值得借鉴的地方？

## 3. 为什么推荐（核心商业逻辑）
从消费者心理学和"高质平价"角度，分析这道菜为什么能成为爆款（例如：高价值感食材的低成本替代、极强的视觉传播力等）。

请以 JSON 格式回复，严格遵循以下结构，不要加 markdown 代码块标记：
{
  "visual_analysis": "详细的视觉与呈现分析（300-500字）",
  "innovation_points": "详细的研发创新点（200-400字）",
  "commercial_logic": "详细的商业逻辑分析（200-400字）",
  "tags": ["相关标签1", "相关标签2", "相关标签3"],
  "inspiration_score": 1-10
}`;

/* ===================================================================
 * 调用 MiniMax 分析单个条目
 * =================================================================== */

async function analyzeItem(item, index, total) {
  const label = item.name || item.title || item.itemLabel || '未知条目';
  console.log(`\n  🔬 [${index + 1}/${total}] 分析: ${label.slice(0, 40)}`);

  // ---- 1. 准备图片（如有） ----
  const imageUrl = item.imageUrl || item.coverUrl;
  let downloadedImage = null;

  if (imageUrl) {
    console.log(`    📥 下载图片...`);
    downloadedImage = await downloadImageAsBase64(imageUrl);
    if (downloadedImage) {
      console.log('    ✅ 图片下载成功');
    } else {
      console.log('    ℹ️  图片下载失败，仅分析文本');
    }
  }

  // ---- 2. 构建文本上下文 ----
  const textParts = [];
  if (item.shopName) textParts.push(`门店: ${item.shopName}（${item.shopCity || ''}）`);
  if (item.name) textParts.push(`菜品: ${item.name}`);
  if (item.price) textParts.push(`价格: ${item.price}`);
  if (item.recommendCount) textParts.push(`推荐频次: ${item.recommendCount}`);
  if (item.reviewText) textParts.push(`用户评价: ${item.reviewText}`);
  if (item.shopRating) textParts.push(`门店评分: ${item.shopRating}`);
  if (item.shopAvgPrice) textParts.push(`门店人均: ¥${item.shopAvgPrice}`);
  if (item.shopAwards) textParts.push(`荣誉: ${item.shopAwards}`);
  if (item.title) textParts.push(`笔记标题: ${item.title}`);
  if (item.bodyText) textParts.push(`笔记正文: ${item.bodyText.slice(0, 1000)}`);
  if (item.likeCount) textParts.push(`点赞数: ${item.likeCount}`);
  textParts.push(`来源: ${item.source || '未知'}`);

  const summary = textParts.join('\n');

  // ---- 3. 调用 MiniMax API ----
  const client = createLLMClient();
  const llmCfg = config.llm;

  let analysisResult = null;

  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      // 构建消息
      const messages = [{ role: 'system', content: SYSTEM_PROMPT }];
      const userContent = [];

      // 如果有图片，以 base64 data URI 形式传入（MiniMax 不支持 URL fetch 故用 base64）
      if (downloadedImage) {
        const dataUri = `data:${downloadedImage.contentType};base64,${downloadedImage.base64}`;
        userContent.push({
          type: 'image_url',
          image_url: { url: dataUri },
        });
      }

      userContent.push({
        type: 'text',
        text: `请基于以下信息进行分析：\n\n${summary}`,
      });

      messages.push({ role: 'user', content: userContent });

      const model = downloadedImage ? llmCfg.vision_model : llmCfg.model;

      const response = await client.chat.completions.create({
        model: model,
        max_tokens: llmCfg.max_tokens || 2000,
        temperature: llmCfg.temperature || 0.7,
        messages,
      });

      let responseText = response.choices?.[0]?.message?.content || '';

      // MiniMax-M3 有时会在响应前加 <think>...</think> 推理过程，需要剥离
      responseText = responseText.replace(/<think>[\s\S]*?<\/think>\s*/g, '').trim();

      // 解析 JSON
      let jsonStr = responseText;
      // 去掉可能的 markdown 代码块
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) jsonStr = jsonMatch[0];

      analysisResult = JSON.parse(jsonStr);
      console.log(
        `    ✅ 分析完成 | 灵感评分: ${analysisResult.inspiration_score ?? '?'}/10`,
      );
      break;
    } catch (err) {
      console.warn(`    ⚠️  API 调用失败 (第${attempt + 1}次): ${err.message.slice(0, 100)}`);
      if (attempt < 2) {
        await sleep(3000);
      }
    }
  }

  if (!analysisResult) {
    console.error(`    ❌ 分析彻底失败，使用备选结构`);
    analysisResult = {
      visual_analysis: 'API 分析失败，本次无法获取视觉分析。',
      innovation_points: 'API 分析失败。',
      commercial_logic: 'API 分析失败。',
      tags: ['error'],
      inspiration_score: 0,
    };
  }

  // ---- 4. 组装结果 ----
  return {
    itemLabel: label,
    itemType: item.name ? '菜品' : item.title ? '笔记' : '其他',
    source: item.source || '未知',
    shopName: item.shopName || null,
    shopCity: item.shopCity || null,
    shopRating: item.shopRating || null,
    shopAvgPrice: item.shopAvgPrice || null,
    shopAwards: item.shopAwards || null,
    imageUrl: imageUrl || null,
    sourceUrl: item.sourceUrl || item.noteUrl || '',
    originalText: summary,
    analysis: analysisResult,
  };
}

/* ===================================================================
 * 按门店分组统计数据（Dashboard 用）
 * =================================================================== */

function buildShopDashboard(analysisResults) {
  const shopMap = {};
  for (const r of analysisResults) {
    if (!r.shopName) continue;
    if (!shopMap[r.shopName]) {
      shopMap[r.shopName] = {
        shopName: r.shopName,
        city: r.shopCity,
        rating: r.shopRating,
        avgPrice: r.shopAvgPrice,
        awards: r.shopAwards,
        dishes: [],
        totalScore: 0,
        count: 0,
      };
    }
    shopMap[r.shopName].dishes.push(r);
    shopMap[r.shopName].totalScore += r.analysis?.inspiration_score || 0;
    shopMap[r.shopName].count += 1;
  }

  return Object.values(shopMap)
    .map((s) => ({
      ...s,
      avgInspirationScore: s.count > 0 ? (s.totalScore / s.count).toFixed(1) : 0,
    }))
    .sort((a, b) => b.avgInspirationScore - a.avgInspirationScore);
}

/* ===================================================================
 * 生成 Markdown 研发报告
 * =================================================================== */

async function generateReport(analysisResults) {
  console.log('\n  📝 生成 Markdown 研发报告...');

  const dishes = analysisResults.filter((r) => r.itemType === '菜品');
  const notes = analysisResults.filter((r) => r.itemType === '笔记');

  // 按灵感评分排序
  const sortedAll = [...analysisResults].sort(
    (a, b) => (b.analysis?.inspiration_score ?? 0) - (a.analysis?.inspiration_score ?? 0),
  );

  const avgScore =
    analysisResults.length > 0
      ? (
          analysisResults.reduce((s, r) => s + (r.analysis?.inspiration_score ?? 0), 0) /
          analysisResults.length
        ).toFixed(1)
      : '0.0';

  // 标签云
  const tagCloud = {};
  analysisResults.forEach((r) => {
    (r.analysis?.tags || []).forEach((t) => {
      tagCloud[t] = (tagCloud[t] || 0) + 1;
    });
  });
  const topTags = Object.entries(tagCloud).sort((a, b) => b[1] - a[1]).slice(0, 20);

  // 高评分 >=7
  const highScoreItems = sortedAll.filter((r) => (r.analysis?.inspiration_score ?? 0) >= 7);

  // 门店排行
  const shopDashboard = buildShopDashboard(analysisResults);

  let md = '';

  md += `# 🐟 胡叨叨 · 新菜研发创新报告\n\n`;
  md += `> **品牌定位**：海鲜小馆与宁波台州菜创新 · 高质平价\n`;
  md += `> **生成时间**：${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}\n`;
  md += `> **分析引擎**：MiniMax ${config.llm.model}\n`;
  md += `> **分析条目**：${analysisResults.length} 条（菜品 ${dishes.length} 道 · 笔记 ${notes.length} 篇）\n`;
  md += `> **平均灵感评分**：${avgScore} / 10\n\n`;

  md += `---\n\n`;

  // ---- 目录 ----
  md += `## 📑 目录\n\n`;
  md += `1. [竞品门店概览](#竞品门店概览)\n`;
  md += `2. [数据概览 & 趋势标签](#数据概览--趋势标签)\n`;
  md += `3. [高价值参考（灵感评分 ≥7）](#高价值参考灵感评分-7)\n`;
  md += `4. [全部菜品分析](#全部菜品分析)\n`;
  md += `5. [全部小红书笔记分析](#全部小红书笔记分析)\n`;
  md += `6. [研发建议摘要](#研发建议摘要)\n\n`;

  md += `---\n\n`;

  // ---- 竞品门店概览 ----
  md += `## 🏪 竞品门店概览\n\n`;
  md += `基于大众点评搜索发现的宁波菜/台州菜热门门店，按菜品平均灵感评分排序：\n\n`;
  md += `| # | 门店 | 城市 | 评分 | 人均 | 荣誉 | 分析菜品数 | 平均灵感分 |\n`;
  md += `|---|------|------|------|------|------|-----------|----------|\n`;
  if (shopDashboard.length === 0) {
    md += '| — | 暂无门店数据 | — | — | — | — | — | — |\n';
  } else {
    shopDashboard.forEach((s, i) => {
      const awardsIcon = [];
      if (s.awards?.includes('必吃')) awardsIcon.push('🏆');
      if (s.awards?.includes('黑珍珠')) awardsIcon.push('💎');
      md += `| ${i + 1} | ${s.shopName} | ${s.city || '-'} | ${s.rating || '-'} | ¥${s.avgPrice || '-'} | ${awardsIcon.join(' ') || '-'} | ${s.count} | ${s.avgInspirationScore}/10 |\n`;
    });
  }
  md += '\n';

  // 客单价分布说明
  const pricedShops = shopDashboard.filter((s) => s.avgPrice > 0);
  if (pricedShops.length > 0) {
    const avgShopPrice = Math.round(
      pricedShops.reduce((sum, s) => sum + parseInt(s.avgPrice), 0) / pricedShops.length,
    );
    md += `> 💡 竞品平均客单价约 **¥${avgShopPrice}**，胡叨叨定位 ¥100 左右，在市场中存在明显的价格优势空间。\n\n`;
  }
  md += `---\n\n`;

  // ---- 数据概览 ----
  md += `## 📊 数据概览 & 趋势标签\n\n`;
  md += `| 指标 | 数值 |\n`;
  md += `| --- | --- |\n`;
  md += `| 竞品门店数 | ${shopDashboard.length} 家 |\n`;
  md += `| 大众点评菜品数 | ${dishes.length} 道 |\n`;
  md += `| 小红书笔记数 | ${notes.length} 篇 |\n`;
  md += `| 高价值参考(≥7分) | ${highScoreItems.length} 条 |\n`;
  md += `| 平均灵感评分 | ${avgScore}/10 |\n`;
  md += `| 聚类标签数 | ${topTags.length} 个 |\n\n`;

  md += `### 🏷️ 趋势标签云\n\n`;
  topTags.forEach(([tag, count]) => {
    const bar = '█'.repeat(Math.min(count * 3, 30));
    md += `- **${tag}** ${bar} (${count})\n`;
  });
  md += '\n---\n\n';

  // ---- 高价值参考 ----
  md += `## ⭐ 高价值参考（灵感评分 ≥7）\n\n`;
  if (highScoreItems.length === 0) {
    md += '*暂无灵感评分≥7的条目*\n\n';
  } else {
    for (const item of highScoreItems) {
      md += `### ${item.itemLabel}\n\n`;
      if (item.shopName) {
        md += `**${item.shopName}** ${item.shopCity ? `· ${item.shopCity}` : ''} ${item.shopRating ? `· 评分 ${item.shopRating}` : ''} ${item.shopAvgPrice ? `· 人均 ¥${item.shopAvgPrice}` : ''}\n\n`;
      }
      if (item.imageUrl) {
        md += `<div align="center">\n  <img src="${item.imageUrl}" alt="${item.itemLabel}" width="400" />\n</div>\n\n`;
      }
      md += `**来源**：${item.source}  \n`;
      md += `**灵感评分**：**${item.analysis.inspiration_score}/10**  \n`;
      md += `**标签**：${(item.analysis.tags || []).map((t) => `\`${t}\``).join(' ')}\n\n`;
      md += `#### 🎨 视觉与呈现分析\n${item.analysis.visual_analysis}\n\n`;
      md += `#### 🔬 研发创新点\n${item.analysis.innovation_points}\n\n`;
      md += `#### 💰 为什么推荐（商业逻辑）\n${item.analysis.commercial_logic}\n\n`;
      md += `---\n\n`;
    }
  }

  // ---- 全部菜品 ----
  md += `## 🍜 全部菜品分析\n\n`;
  for (const item of dishes) {
    md += `### 🥘 ${item.itemLabel}\n\n`;
    if (item.shopName) {
      md += `**${item.shopName}** · ${item.shopCity || '-'} · 评分 ${item.shopRating || '-'} · 人均 ¥${item.shopAvgPrice || '-'}\n\n`;
    }
    md += `**灵感评分**：${item.analysis.inspiration_score ?? 'N/A'}/10  \n`;
    md += `**标签**：${(item.analysis.tags || []).map((t) => `\`${t}\``).join(' ')}\n\n`;
    md += `#### 🎨 视觉与呈现\n${item.analysis.visual_analysis}\n\n`;
    md += `#### 🔬 创新点\n${item.analysis.innovation_points}\n\n`;
    md += `#### 💰 商业逻辑\n${item.analysis.commercial_logic}\n\n`;
    if (item.sourceUrl) md += `> 来源：${item.sourceUrl}\n\n`;
    md += `---\n\n`;
  }

  // ---- 全部小红书笔记 ----
  md += `## 📕 全部小红书笔记分析\n\n`;
  for (const item of notes) {
    md += `### 📝 ${item.itemLabel}\n\n`;
    if (item.imageUrl) {
      md += `<div align="center">\n  <img src="${item.imageUrl}" alt="${item.itemLabel}" width="400" />\n</div>\n\n`;
    }
    md += `**灵感评分**：${item.analysis.inspiration_score ?? 'N/A'}/10  \n`;
    md += `**标签**：${(item.analysis.tags || []).map((t) => `\`${t}\``).join(' ')}\n\n`;
    md += `#### 🎨 视觉与呈现\n${item.analysis.visual_analysis}\n\n`;
    md += `#### 🔬 创新点\n${item.analysis.innovation_points}\n\n`;
    md += `#### 💰 商业逻辑\n${item.analysis.commercial_logic}\n\n`;
    if (item.sourceUrl) md += `> 来源：${item.sourceUrl}\n\n`;
    md += `---\n\n`;
  }

  // ---- 研发建议摘要 ----
  md += `## 💡 研发建议摘要\n\n`;
  md += `基于以上 ${analysisResults.length} 条数据的 AI 多模态分析，以下是针对"胡叨叨"品牌的研发建议：\n\n`;

  // 竞品定位分析
  md += `### 竞品定位分析\n\n`;
  if (shopDashboard.length > 0) {
    const avgShopPrice = pricedShops.length > 0
      ? Math.round(pricedShops.reduce((sum, s) => sum + parseInt(s.avgPrice), 0) / pricedShops.length)
      : 'N/A';
    md += `- 本次共分析 **${shopDashboard.length} 家** 宁波菜/台州菜竞品门店\n`;
    md += `- 竞品平均客单价约 **¥${avgShopPrice}**，胡叨叨定位 ¥100 左右存在空间\n`;
    const topShops = shopDashboard.filter((s) => s.rating >= 4.5);
    if (topShops.length > 0) {
      md += `- 高评分门店(≥4.5)：**${topShops.map((s) => s.shopName).join('、')}**\n`;
    }
    md += '\n';
  }

  md += `### 视觉呈现方向\n\n`;
  md += `- **器皿选择**：注重简约而有质感的器皿，白色/哑光陶瓷器皿最能凸显海鲜食材的本色\n`;
  md += `- **色彩搭配**：利用海鲜自带的橙红（虾蟹）、翠绿（葱蒜）、金黄（炸物）形成强烈视觉对比\n`;
  md += `- **摆盘技巧**：去繁就简，减少堆砌，强调食材的"主角地位"\n\n`;

  md += `### 食材创新方向\n\n`;
  md += `- **宁波台州特色**：深度挖掘带鱼、黄鱼、梭子蟹、蛏子等本地海鲜的多元做法\n`;
  md += `- **高质平价策略**：通过精准的食材部位选择（如鱼腩而非整鱼）降低客单价，同时保持品质感\n`;
  md += `- **海鲜+X**：海鲜与传统宁波/台州家常食材（年糕、霉干菜、雪菜）的创新搭配\n\n`;

  md += `### 爆品打造策略\n\n`;
  md += `- **视觉传播力**：每道菜都必须在 3 秒内产生"值得拍照"的冲动\n`;
  md += `- **记忆点打造**：每道菜至少有一个"哇"点（火焰上桌、石锅滋滋声、现场浇汁等）\n`;
  md += `- **价格锚定**：设置 1-2 道"引流爆品"（低价高质），带动整体客单价\n\n`;

  // 重点参考
  if (highScoreItems.length > 0) {
    md += `### 重点参考菜品\n\n`;
    md += `以下为本次分析中灵感评分最高的条目，建议优先纳入研发试菜清单：\n\n`;
    highScoreItems.slice(0, 5).forEach((item, i) => {
      const shopTag = item.shopName ? `（${item.shopName}）` : '';
      md += `${i + 1}. **${item.itemLabel}** ${shopTag}— ${item.analysis.inspiration_score}/10 · ${(item.analysis.tags || []).slice(0, 3).join('、')}\n`;
    });
    md += '\n';
  }

  md += `---\n\n`;
  md += `*本报告由胡叨叨新菜研发AI助手自动生成 | ${new Date().toLocaleDateString('zh-CN')}*\n`;

  return md;
}

/* ===================================================================
 * 主入口
 * =================================================================== */

async function main() {
  console.log('');
  console.log('╔═══════════════════════════════════════════╗');
  console.log('║   🤖 胡叨叨 · AI 研发分析引擎            ║');
  console.log(`║   模型: MiniMax ${config.llm.model}                 ║`);
  console.log('╚═══════════════════════════════════════════╝');
  console.log('');

  const rawPath = path.resolve(__dirname, '..', config.output.raw_data_path);
  if (!(await fs.pathExists(rawPath))) {
    console.error(`❌ 未找到原始数据: ${rawPath}`);
    console.error('   请先运行 npm run discover 和 npm run scrape');
    process.exit(1);
  }

  const rawData = await fs.readJson(rawPath);
  const sources = [];

  // 竞品门店菜品
  if (rawData.dianping?.length) {
    sources.push(...rawData.dianping);
    console.log(`📦 大众点评菜品: ${rawData.dianping.length} 道`);
  }
  // 小红书笔记
  if (rawData.xiaohongshu?.length) {
    sources.push(...rawData.xiaohongshu);
    console.log(`📦 小红书笔记: ${rawData.xiaohongshu.length} 篇`);
  }
  // 门店概况
  if (rawData.shops?.length) {
    console.log(`📦 竞品门店: ${rawData.shops.length} 家`);
  }

  if (sources.length === 0) {
    console.error('❌ 无数据可分析');
    process.exit(1);
  }

  console.log(`\n🧠 开始分析 ${sources.length} 条条目...\n`);

  const results = [];
  for (let i = 0; i < sources.length; i++) {
    const r = await analyzeItem(sources[i], i, sources.length);
    results.push(r);
    if (i < sources.length - 1) await sleep(1200);
  }

  const md = await generateReport(results);

  await fs.ensureDir(path.resolve(__dirname, '..', 'reports'));
  const mdPath = path.resolve(__dirname, '..', config.output.report_markdown_path);
  await fs.writeFile(mdPath, md, 'utf-8');

  const totalScore = results.reduce((s, r) => s + (r.analysis?.inspiration_score ?? 0), 0);
  console.log(`\n✅ 研发报告已生成: ${mdPath}`);
  console.log(`   📊 总计分析 ${results.length} 条`);
  console.log(`   ⭐ 平均灵感评分: ${results.length > 0 ? (totalScore / results.length).toFixed(1) : 'N/A'}/10`);
  console.log('');

  return { results, md };
}

// 独立运行
if (require.main === module) {
  main().catch((err) => {
    console.error('\n❌ 严重错误:', err);
    process.exit(1);
  });
}

module.exports = { analyzeItem, generateReport, main };
