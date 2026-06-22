/**
 * renderer.js — 本地可视化预览模块
 *
 * 职责：
 *   1. 读取 reports/seasonal_innovation_report.md
 *   2. 将其转化为美观的 report.html 网页
 *   3. 布局：左图右文，方便快速浏览
 *
 * 运行方式：npm run render  或  node src/renderer.js
 */

const fs = require('fs-extra');
const path = require('path');
const { marked } = require('marked');

const CONFIG_PATH = path.resolve(__dirname, '..', 'config.json');
const config = fs.readJsonSync(CONFIG_PATH);

/* ===================================================================
 * HTML 模板
 * =================================================================== */

function buildHtml(markdownContent) {
  // 提取高价值参考条目中的图片信息用于左侧导航
  const imageLinks = [];
  const imgRegex = /<img src="([^"]+)" alt="([^"]*)"[^>]*\/>/g;
  let match;
  while ((match = imgRegex.exec(markdownContent)) !== null) {
    const alt = match[2] || '图片';
    if (alt !== '图片' && alt.length > 0 && alt.length < 50) {
      imageLinks.push({ src: match[1], alt });
    }
  }

  // 解析 Markdown 为 HTML
  const bodyHtml = marked.parse(markdownContent, { async: false });

  const imagesJson = JSON.stringify(imageLinks);

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>胡叨叨 · 新菜研发创新报告</title>
  <style>
    /* ===== 全局重置 & 字体 ===== */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
      background: #f8f6f2;
      color: #2c2c2c;
      line-height: 1.8;
      font-size: 15px;
    }

    /* ===== 顶部导航 ===== */
    .top-nav {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 52px;
      background: #1a1a1a;
      color: #f5f0e8;
      display: flex;
      align-items: center;
      padding: 0 24px;
      z-index: 1000;
      box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .top-nav .brand {
      font-size: 17px;
      font-weight: 600;
      letter-spacing: 1px;
    }
    .top-nav .brand small {
      font-weight: 400;
      font-size: 13px;
      opacity: 0.6;
      margin-left: 12px;
    }
    .top-nav .nav-links {
      margin-left: auto;
      display: flex;
      gap: 16px;
      font-size: 13px;
    }
    .top-nav .nav-links a {
      color: #b8a898;
      text-decoration: none;
      transition: color 0.2s;
    }
    .top-nav .nav-links a:hover { color: #f5f0e8; }

    /* ===== 布局容器 ===== */
    .app-container {
      display: flex;
      margin-top: 52px;
      min-height: calc(100vh - 52px);
    }

    /* ===== 左侧图片画廊 ===== */
    .side-gallery {
      width: 280px;
      min-width: 280px;
      background: #f0ece4;
      padding: 20px 16px;
      overflow-y: auto;
      max-height: calc(100vh - 52px);
      position: sticky;
      top: 52px;
    }
    .side-gallery h3 {
      font-size: 14px;
      color: #8a7a6a;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #ddd6cc;
      letter-spacing: 1px;
    }
    .side-gallery .gallery-item {
      margin-bottom: 16px;
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      border: 2px solid transparent;
    }
    .side-gallery .gallery-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    .side-gallery .gallery-item.active {
      border-color: #c0392b;
    }
    .side-gallery .gallery-item img {
      width: 100%;
      height: 120px;
      object-fit: cover;
      display: block;
    }
    .side-gallery .gallery-item .label {
      padding: 6px 8px;
      font-size: 12px;
      color: #555;
      background: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .side-gallery .empty-gallery {
      color: #999;
      font-size: 13px;
      text-align: center;
      padding: 40px 0;
    }

    /* ===== 主内容区 ===== */
    .main-content {
      flex: 1;
      padding: 40px 48px;
      max-width: 960px;
    }

    /* ===== Markdown 样式 ===== */
    .main-content h1 {
      font-size: 28px;
      color: #1a1a1a;
      margin: 32px 0 16px;
      padding-bottom: 12px;
      border-bottom: 2px solid #d4c8b8;
    }
    .main-content h1:first-of-type {
      margin-top: 0;
    }
    .main-content h2 {
      font-size: 22px;
      color: #2c2c2c;
      margin: 28px 0 14px;
      padding-left: 12px;
      border-left: 4px solid #c0392b;
    }
    .main-content h3 {
      font-size: 18px;
      color: #3a3a3a;
      margin: 20px 0 10px;
    }
    .main-content h4 {
      font-size: 16px;
      color: #555;
      margin: 16px 0 8px;
    }
    .main-content p {
      margin: 8px 0 12px;
      text-align: justify;
    }
    .main-content blockquote {
      margin: 12px 0;
      padding: 10px 20px;
      background: #f5f0e8;
      border-left: 4px solid #c0392b;
      color: #666;
      font-style: italic;
    }
    .main-content code {
      background: #eee9e0;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 13px;
    }
    .main-content table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
    }
    .main-content th, .main-content td {
      border: 1px solid #ddd6cc;
      padding: 8px 14px;
      text-align: left;
    }
    .main-content th {
      background: #e8e0d4;
      font-weight: 600;
    }
    .main-content tr:nth-child(even) td {
      background: #faf6f0;
    }
    .main-content ul, .main-content ol {
      margin: 8px 0 12px 24px;
    }
    .main-content li {
      margin: 4px 0;
    }
    .main-content hr {
      border: none;
      border-top: 1px solid #ddd6cc;
      margin: 32px 0;
    }
    .main-content div[align="center"] {
      margin: 16px 0;
    }
    .main-content img {
      max-width: 100%;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .main-content img[width="400"] {
      max-width: 400px;
    }
    .main-content .tag {
      display: inline-block;
      background: #f0e8dc;
      color: #8a6a4a;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 12px;
      margin: 2px 4px;
    }
    .main-content strong {
      color: #1a1a1a;
    }

    /* ===== 分数徽章 ===== */
    .score-badge {
      display: inline-block;
      background: #c0392b;
      color: #fff;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 13px;
      font-weight: 600;
    }

    /* ===== 响应式 ===== */
    @media (max-width: 900px) {
      .app-container {
        flex-direction: column;
      }
      .side-gallery {
        width: 100%;
        min-width: 100%;
        max-height: none;
        position: static;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 12px;
      }
      .side-gallery h3 {
        width: 100%;
        margin-bottom: 8px;
      }
      .side-gallery .gallery-item {
        width: calc(33% - 8px);
        margin-bottom: 0;
      }
      .side-gallery .gallery-item img {
        height: 80px;
      }
      .main-content {
        padding: 24px 20px;
      }
    }
    @media (max-width: 600px) {
      .side-gallery .gallery-item {
        width: calc(50% - 8px);
      }
      .main-content img[width="400"] {
        max-width: 100%;
      }
    }

    /* ===== 打印优化 ===== */
    @media print {
      .top-nav, .side-gallery { display: none; }
      .app-container { margin-top: 0; }
      .main-content { max-width: 100%; padding: 32px; }
    }
  </style>
</head>
<body>

  <!-- 顶部导航 -->
  <nav class="top-nav">
    <div class="brand">
      🐟 胡叨叨
      <small>新菜研发 AI 助手 · 高质平价海鲜小馆</small>
    </div>
    <div class="nav-links">
      <a href="#" onclick="window.print()">🖨️ 打印/PDF</a>
      <a href="#" onclick="document.querySelector('.side-gallery').classList.toggle('collapsed')">📷 图库</a>
    </div>
  </nav>

  <div class="app-container">
    <!-- 左侧图片画廊 -->
    <aside class="side-gallery" id="gallery">
      <h3>📷 参考图片</h3>
      <div id="galleryItems">
        <!-- 由 JS 动态渲染 -->
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="main-content">
      ${bodyHtml}
    </main>
  </div>

  <script>
    (function() {
      const images = ${imagesJson};

      const galleryEl = document.getElementById('galleryItems');
      if (images.length === 0) {
        galleryEl.innerHTML = '<div class="empty-gallery">暂无参考图片</div>';
      } else {
        galleryEl.innerHTML = images.map((img, i) =>
          '<div class="gallery-item" onclick="scrollToDish(' + i + ')" title="' + escapeHtml(img.alt) + '">' +
            '<img src="' + escapeHtml(img.src) + '" alt="' + escapeHtml(img.alt) + '" loading="lazy" />' +
            '<div class="label">' + escapeHtml(img.alt.slice(0, 30)) + '</div>' +
          '</div>'
        ).join('');
      }

      function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;')
          .replace(/</g, '&lt;').replace(/>/g, '&gt;');
      }

      window.scrollToDish = function(index) {
        const img = images[index];
        if (!img) return;

        // 尝试滚动到对应位置
        const altText = img.alt;
        // 查找包含该 alt 文本的 h3 或 img 附近
        const allImgs = document.querySelectorAll('.main-content img');
        for (let i = 0; i < allImgs.length; i++) {
          if (allImgs[i].alt === altText || allImgs[i].alt.includes(altText)) {
            allImgs[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
            // 高亮闪烁
            allImgs[i].style.transition = 'box-shadow 0.5s';
            allImgs[i].style.boxShadow = '0 0 0 4px #c0392b';
            setTimeout(() => { allImgs[i].style.boxShadow = ''; }, 1500);
            break;
          }
        }

        // 更新激活状态
        document.querySelectorAll('.gallery-item').forEach(el => el.classList.remove('active'));
        const items = document.querySelectorAll('.gallery-item');
        if (items[index]) items[index].classList.add('active');
      };
    })();
  </script>
</body>
</html>`;
}

/* ===================================================================
 * 主入口
 * =================================================================== */

async function main() {
  console.log('');
  console.log('╔══════════════════════════════════════════╗');
  console.log('║   🎨 胡叨叨 · 研发报告可视化渲染器     ║');
  console.log('╚══════════════════════════════════════════╝');
  console.log('');

  const mdPath = path.resolve(__dirname, '..', config.output.report_markdown_path);
  if (!(await fs.pathExists(mdPath))) {
    console.error(`❌ 未找到 Markdown 报告: ${mdPath}`);
    console.error('   请先运行 npm run analyze');
    process.exit(1);
  }

  const mdContent = await fs.readFile(mdPath, 'utf-8');
  console.log(`📖 读取报告: ${mdPath}`);

  const html = buildHtml(mdContent);

  const htmlPath = path.resolve(__dirname, '..', config.output.report_html_path);
  await fs.ensureDir(path.dirname(htmlPath));
  await fs.writeFile(htmlPath, html, 'utf-8');

  console.log(`✅ HTML 报告已生成: ${htmlPath}`);
  console.log(`   🌐 可直接在浏览器中打开该文件查看\n`);

  return htmlPath;
}

if (require.main === module) {
  main().catch(err => {
    console.error('\n❌ 严重错误:', err);
    process.exit(1);
  });
}

module.exports = { buildHtml, main };
