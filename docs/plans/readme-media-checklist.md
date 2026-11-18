# README 推广素材清单（v1.0.6）

多语言 README（`README.md`、`README.zh-CN.md`、`README.ja.md`、`README.es.md`、`README.fr.md`）中已预留 4 处媒体占位符（搜索 `MEDIA PLACEHOLDER` 即可定位）。

## 待准备素材

- [ ] **#1 主演示动画（必做，最高优先级）**
  - **占位标记**：`<!-- MEDIA PLACEHOLDER #1: ... -->`
  - **位置**：顶部语言切换栏下方（Hero 区）
  - **建议路径**：`docs/img/demo-hero.gif`（或 GitHub 托管 `.mp4`）
  - **内容**：输入单词或上传一道 STEM 题目截图 → AI 生成卡片 → 点击翻转正反面预览 → 点击保存同步到 Anki。
  - **录制建议**：
    - 时长控制在 **10–15 秒**，AI 生成等待过程剪掉或 4x–8x 加速。
    - 浏览器窗口约 `1280×800`，页面缩放 `110%–125%`，保证移动端缩略图清晰。
    - 导出为 `< 5 MB` 的 GIF 放入 `docs/img/`，或上传 `.mp4` 至 GitHub 生成嵌入式视频链接。

- [ ] **#2a 语言卡片展示图（建议做）**
  - **占位标记**：`<!-- MEDIA PLACEHOLDER #2a: ... -->`
  - **位置**：`Card & UI Showcase` 区块
  - **建议路径**：`docs/img/showcase-word.png`
  - **内容**：一张高质量单词/句子卡片效果（带 AI 配图、音标/注音、例句、音频按钮）。

- [ ] **#2b STEM 卡片展示图（建议做）**
  - **占位标记**：`<!-- MEDIA PLACEHOLDER #2b: ... -->`
  - **位置**：`Card & UI Showcase` 区块
  - **建议路径**：`docs/img/showcase-stem.png`
  - **内容**：一道数学/物理/编程题（最好带题目截图或 MathJax 公式 + 分步解析）的卡片效果。

- [ ] **#3 卡片主题对比图（可选）**
  - **占位标记**：`<!-- MEDIA PLACEHOLDER #3: ... -->`
  - **位置**：`Card & UI Showcase` 区块
  - **路径**：`docs/img/themes-light.png` + `docs/img/themes-dark.png`（两张）
  - **内容**：**Rosé Pine**、**Kanagawa**、**Tokyo Night**、**Gruvbox** 四套主题并排（1×4 或 2×2）。两张图用同一张卡、同样的排版，一张全部浅色模式，一张全部深色模式。
  - **嵌入方式**：用 `<picture>` 让 GitHub 根据访客的浅色/深色模式自动显示对应那张：

    ```html
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="docs/img/themes-dark.png">
      <img src="docs/img/themes-light.png" alt="Rosé Pine, Kanagawa, Tokyo Night and Gruvbox card themes">
    </picture>
    ```

- [ ] **#4 首次配置向导截图（可选）**
  - **占位标记**：`<!-- MEDIA PLACEHOLDER #4: ... -->`
  - **位置**：`Quick Start` 步骤下方
  - **建议路径**：`docs/img/wizard-setup.png`
  - **内容**：5 步 Setup Wizard 界面（如粘贴 Gemini Key 一步）。

## 替换说明

素材准备好放入 `docs/img/` 后，在以下 5 个文件中将对应的 `<!-- MEDIA PLACEHOLDER ... -->` 替换为图片/视频标签即可（#2a 与 #2b 可并排展示）：

- `README.md`
- `README.zh-CN.md`
- `README.ja.md`
- `README.es.md`
- `README.fr.md`
