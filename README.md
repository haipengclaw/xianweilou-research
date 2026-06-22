# 🐟 仙味楼 · 新菜研发 AI 助手

> **Hudadao R&D Assistant** — 海鲜小馆与宁波台州菜创新 · 高质平价
>
> 帮助你持续采集创新灵感，驱动菜品研发

一套基于 Node.js + Playwright + MiniMax-M3 多模态 AI 的菜品研发灵感工具。

## 核心理念

做餐饮研发创新，**最有价值的灵感来源**：

| 来源 | 找什么 | 为什么 |
|------|--------|-------|
| 📕 **小红书** | 创意做法、摆盘灵感、平价高级感 | 民间智慧 + 真实分享，比餐厅菜单更有创新启发 |
| 🍽️ **大众点评** | 热门推荐菜（不限门店） | 看什么菜被推荐最多，发现趋势 |

**不看门店、不看竞品，只看菜品本身和用户创意。**

---

## 快速开始

```bash
cd hudadao-r-and-d-assistant
npm install
npx playwright install chromium
```

编辑 `config.json`，确保 API 密钥已配置：

```json
{
  "llm": {
    "api_base_url": "https://api.minimax.chat/v1",
    "api_key": "你的MiniMax密钥",
    "model": "MiniMax-M3",
    "vision_model": "MiniMax-M3"
  }
}
```

---

## 一键运行

```bash
npm run research
```

全流程：
1. 📡 采集大众点评热门推荐菜 + 小红书创意笔记
2. 🧠 MiniMax-M3 多模态 AI 分析（摆盘、食材创新、爆品逻辑）
3. 🎨 生成 HTML 可视化研发报告

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `npm run research` | 全流程：采集 → 分析 → 报告 |
| `npm run scrape` | 仅采集数据 |
| `npm run analyze` | 仅 AI 分析 |
| `npm run render` | 仅生成 HTML 报告 |

---

## 小红书关键词策略

`config.json` 中的 `xiaohongshu.search_keywords` 分为几类：

**创意做法类：**
- 「海鲜 神仙吃法」「海鲜 创意做法 家常」
- 「台州菜 创新做法」「宁波 传统菜 新做」

**平价高级感类：**
- 「平价 高级感 美食DIY」「30元 做出餐厅感 摆盘」

**跨界借鉴类：**
- 「海鲜 融合菜 创新」「海鲜 西餐做法 在家」
- 「日料 海鲜 做法 在家复刻」「粤菜 海鲜 家常版」

**趋势类：**
- 「餐厅 爆款 菜品 2025」「摆盘 技巧 高级感」

> 你可以随时修改这些关键词，针对不同研发阶段调整搜索方向。

---

## 项目结构

```
├── config.json                # 配置（API密钥 + 搜索关键词）
├── src/
│   ├── index.js               # 一键入口
│   ├── image_scraper.js       # 大众点评 + 小红书采集
│   ├── visual_analyzer.js     # MiniMax 多模态分析
│   └── renderer.js            # HTML 报告渲染
├── data/                      # 采集数据（gitignore）
└── reports/                   # 分析报告（gitignore）
```

---

## 注意事项

1. **首次运行**：小红书需要扫码登录一次，Cookie 自动保存后续复用
2. **API 费用**：每条数据调用一次 MiniMax API，通过 `notes_to_scrape` 控制量
3. **反爬**：所有操作内置随机延迟 + 真人轨迹模拟
4. **图片防盗链**：部分图片在本地 HTML 可能无法显示，可右键新标签打开

---

## 自定义分析维度

编辑 `visual_analyzer.js` 中的 `SYSTEM_PROMPT` 可调整 AI 分析侧重点。当前分析三个维度：
- 🎨 视觉与呈现分析（摆盘、色彩、器皿）
- 🔬 研发创新点（食材搭配、烹饪技法）
- 💰 商业逻辑（为什么能成为爆款）

---

<div align="center">
  <sub>Made with ❤️ for 仙味楼 · 海鲜小馆与宁波台州菜创新</sub>
</div>
