# AnkiNote

<p align="center">
  <img src="src/ankinote/ui/static/ankinote-logo.svg" width="96" alt="AnkiNote logo">
</p>

<p align="center">
  <strong>输入一个单词、句子或 STEM 题目，几秒钟生成可直接复习的精美观 Anki 卡片。</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ignity21/ankinote-ai/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ignity21/ankinote-ai"><img src="https://img.shields.io/codecov/c/github/ignity21/ankinote-ai?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a>
</p>

---

<!-- MEDIA PLACEHOLDER #1: Hero Demo GIF / Video (recommended: docs/img/demo-hero.gif)
     展示：输入单词或上传 STEM 题目图片 -> AI 生成卡片 -> 正反面预览切换 -> 点击保存直接同步到 Anki。 -->

制卡不该比背卡还累。**AnkiNote** 是一款由 AI 驱动的 Anki 制卡工作台，只需输入一个单词、短语、句子或理工科（STEM）题目，即可自动生成包含释义、例句、助记、AI 配图与自然语音的精美卡片，并直接同步到你的 AnkiWeb 账号。

告别手动排版，告别在 ChatGPT 和 Anki 之间反复复制粘贴。自带 API Key 即可随时随地运行，在手机、平板和电脑上无缝复习。

---

## ✨ 核心亮点

- **内置 Anki 引擎与 AnkiWeb 自动同步** — 无需安装桌面端 Anki，也无需配置 AnkiConnect。AnkiNote 内置 Anki 核心库并自动与 AnkiWeb 同步，在浏览器或 NAS 上添加的卡片会自动出现在你的所有设备上。*（如果你习惯使用桌面端，同样支持 AnkiConnect。）*
- **一个 Key 搞定全部配置** — 首次启动提供 5 步引导向导：只需粘贴一个 Gemini AI Studio Key，即可同时驱动文本、配图和语音合成；也支持自由混搭 OpenAI、Claude、DeepSeek、fal.ai、Google Cloud TTS 及任意 OpenAI 兼容接口。
- **四种制卡模式：单词、短语、句子与 STEM**
  - **语言学习**：自动生成精准释义、地道例句、记忆技巧、AI 场景配图与真人感发音。支持 **英语、法语、西班牙语、德语、日语、中文（简/繁体，带注音/拼音）与韩语（Beta）** 任意互译学习。
  - **STEM 理科解题**：输入题目或**直接上传题目截图/照片**，生成结构化的分步解析卡片，原生支持 MathJax 公式渲染与辅助示意图。
- **实时预览、行内编辑与 AI 改写** — 保存前可随时翻转正反面、切换深色/浅色主题。支持直接修改任意字段，也可让 AI 按指令重写 STEM 解析或一键修复损坏的 LaTeX 公式（支持撤销）。
- **精选卡片配色主题** — 内置 **Rosé Pine**、**Kanagawa**、**Tokyo Night**、**Gruvbox** 四套护眼配色（均含浅色与深色模式），桌面端与移动端 Anki 均自适应。
- **Web 工作台 + CLI 命令行** — 日常制卡使用现代化的 Svelte Web 应用（`ankinote-web`），批量处理与自动化脚本可使用 CLI 与终端交互界面（`ankinote`）。

---

## 📸 卡片与界面展示

<!-- MEDIA PLACEHOLDER #2a: Language Card Showcase (recommended: docs/img/showcase-word.png)
     展示：单词/句子卡片效果（含配图、音标/注音、例句、音频）。 -->

<!-- MEDIA PLACEHOLDER #2b: STEM Card Showcase (recommended: docs/img/showcase-stem.png)
     展示：通过题目文本或拍照生成的 STEM 卡片效果（含 MathJax 公式与分步解析）。 -->

<!-- MEDIA PLACEHOLDER #3: Card Themes Comparison (docs/img/themes-light.png + docs/img/themes-dark.png, swapped by GitHub's color scheme via <picture>)
     展示：Rosé Pine、Kanagawa、Tokyo Night、Gruvbox 四套卡片主题并排对比。 -->

---

## 🚀 1 分钟快速上手

唯一的前置依赖是 [uv](https://docs.astral.sh/uv/getting-started/installation/)（它会自动帮你管理 Python 环境）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

无需安装，直接运行：

```bash
uvx --from ankinote-ai ankinote-web
```

在浏览器打开 **<http://127.0.0.1:8000>**。首次启动时，**配置向导**会带你完成：

1. **AI 服务** — 粘贴 Gemini API Key（一站式覆盖文本、配图、语音），或展开**高级选项**配置 OpenAI、Claude、DeepSeek、fal.ai 等。
2. **Anki 连接** — 选择**内置 Anki** 并登录 AnkiWeb*（若桌面端常驻运行，也可选择 **AnkiConnect**）*。
3. **语言** — 选择母语与目标语言。
4. **外观** — 选择配色方案与浅色/深色模式，Anki 卡片也会使用同一套配色。
5. **首张卡片** — 在向导中直接生成并保存你的第一张卡片。

<!-- MEDIA PLACEHOLDER #4: Setup Wizard Screenshot (recommended: docs/img/wizard-setup.png)
     展示：Web 端 5 步首次配置向导界面。 -->

如果想全局安装以便随时启动：

```bash
uv tool install ankinote-ai
ankinote-web
```

> **系统要求**：Linux 需 `glibc >= 2.35`（Ubuntu 22.04+、Debian 12+ 等）；同时支持 macOS 12+ 与 Windows。

---

## 🐳 Docker 自部署（NAS / 服务器）

将 AnkiNote 部署在服务器、VPS 或 NAS 上，随时用手机浏览器打开就能制卡。Docker Hub 与 GHCR 均已提供多架构镜像（`amd64` + `arm64`）：`ghcr.io/ignity21/ankinote-ai` 与 `ignity21/ankinote-ai`。

```bash
# 独立运行模式（推荐：内置 Anki + AnkiWeb 同步，无需桌面端）
cd deploy/headless
cp .env.example .env      # 可选：配置 ANKIWEB_USERNAME / ANKIWEB_PASSWORD、端口等
docker compose up -d      # 访问 http://localhost:8080
```

如果你已经在宿主机运行了带 AnkiConnect 的 Anki 桌面端，可使用 `deploy/standard`。完整部署说明与迁移指南请见 [`deploy/README.md`](deploy/README.md)。

---

## ⌨️ CLI 与批量制卡

AnkiNote 提供命令行工具 `ankinote`，与 Web 端共用同一份配置（`~/.config/ankinote/settings.json`）：

```bash
ankinote                  # 打开交互式终端菜单（TUI）
ankinote word ephemeral   # 生成单词卡片
ankinote stem "..."       # 生成 STEM 题目卡片
ankinote profiles list    # 查看已配置的模型方案
```

更多批量制卡与脚本自动化用法，请参考 [CLI 使用指南](docs/cli-usage.md)。

---

## 🤖 支持的模型服务

| 能力 | 内置预设与兼容范围 |
| --- | --- |
| **文本生成** | Gemini、OpenAI、Claude、DeepSeek，或任意 OpenAI 兼容接口（基于 `litellm`） |
| **图像生成** | Gemini、OpenAI（`gpt-image`）、fal.ai |
| **语音合成（TTS）** | Gemini TTS、OpenAI TTS、Google Cloud TTS |

所有 API Key 与配置均保存在本地（`~/.config/ankinote/settings.json`），并可在**设置**页面导出为加密备份文件（`scrypt` + `AES-256-GCM`），方便跨设备迁移。

---

## 🛠️ 本地开发

```bash
git clone https://github.com/ignity21/ankinote-ai.git
cd ankinote-ai

uv sync                   # 安装 Python 依赖（需 Python 3.14+）
make web-dev              # 启动 Svelte + Vite 前端开发服务器
uv run ankinote-web       # 启动 FastAPI 后端服务

make test                 # 运行 pytest 测试
make format               # 使用 ruff 格式化代码
make check                # 代码检查与类型检查（ruff + ty）
```

---

## 📚 相关文档

- [CLI 使用指南](docs/cli-usage.md)
- [Docker 部署指南](deploy/README.md)
- [笔记模板说明](docs/NoteType.org)
- [Agent Skill](.agents/skills/ankinote-cli/SKILL.md) — 配合 AI 编程助手使用 AnkiNote

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE)。
