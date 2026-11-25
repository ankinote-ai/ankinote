# AnkiNote

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/brand/mark-dark.svg">
    <img src="docs/brand/mark-light.svg" width="96" alt="AnkiNote logo">
  </picture>
</p>

<p align="center">
  <strong>输入一个单词、句子或 STEM 题目，几秒钟生成可直接复习的精美 Anki 卡片。</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ankinote-ai/ankinote/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ankinote-ai/ankinote"><img src="https://img.shields.io/codecov/c/github/ankinote-ai/ankinote?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong> | <a href="README.zh-Hant.md">繁體中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a>
</p>

---

<p align="center">
  <img src="docs/img/demo-hero.gif" width="860" alt="AnkiNote 演示：输入单词、生成卡片、翻到背面">
</p>

制卡不该比背卡还累。**AnkiNote** 是一款由 AI 驱动的 Anki 制卡工作台，只需输入一个单词、短语、句子或理工科（STEM）题目，即可自动生成包含释义、例句、助记、AI 配图与自然语音的精美卡片，并直接存进你的 Anki。

告别手动排版，告别在 ChatGPT 和 Anki 之间反复复制粘贴。自带 API Key 即可随时随地运行，在手机、平板和电脑上无缝复习。

---

## ✨ 核心亮点

- **配合你已有的 Anki** — 在你平时学习的电脑上，卡片通过 AnkiConnect 插件直接存进 Anki 桌面版：不多一份资料库，不用先下载，Anki 照常同步。在常开的家用服务器或 NAS 上，AnkiNote 也可以用内置的 Anki 直接同步 AnkiWeb，电脑关着也能用手机浏览器加卡片。
- **一个 Key 搞定全部配置** — 首次启动提供 5 步引导向导：只需粘贴一个 Gemini AI Studio Key，即可同时驱动文本、配图和语音合成；也支持自由混搭 OpenAI、Claude、DeepSeek、fal.ai、Google Cloud TTS 及任意 OpenAI 兼容接口。
- **四种制卡模式：单词、短语、句子与 STEM**
  - **语言学习**：自动生成精准释义、地道例句、记忆技巧、AI 场景配图与真人感发音。支持 **英语、法语、西班牙语、德语、日语、中文（简/繁体，带注音/拼音）与韩语（Beta）** 任意互译学习。
  - **STEM 理科解题**：输入题目或**直接上传题目截图/照片**，生成结构化的分步解析卡片，原生支持 MathJax 公式渲染与辅助示意图。
- **实时预览、行内编辑与 AI 改写** — 保存前可随时翻转正反面、切换深色/浅色主题。支持直接修改任意字段，也可让 AI 按指令重写 STEM 解析或一键修复损坏的 LaTeX 公式（支持撤销）。
- **精选卡片配色主题** — 内置 **Rosé Pine**、**Kanagawa**、**Tokyo Night**、**Gruvbox** 四套护眼配色（均含浅色与深色模式），桌面端与移动端 Anki 均自适应。
- **可以交给 AI Agent** — 有了 `ankinote` 命令行，Claude Code、Codex 等能执行命令的 Agent 就能把你正在读的内容做成卡片。

---

## 📸 卡片与界面展示

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="docs/img/showcase-word.png" alt="语言卡片：释义、配图与例句"><br><sub>语言卡片：释义、配图与例句</sub></td>
    <td width="50%" valign="top" align="center"><img src="docs/img/showcase-stem.png" alt="STEM 卡片：公式与分步解析"><br><sub>STEM 卡片：公式与分步解析</sub></td>
  </tr>
</table>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/img/themes-dark.png">
    <img src="docs/img/themes-light.png" width="860" alt="四套卡片配色：Kanagawa、Tokyo Night、Gruvbox 与 Rosé Pine，含浅色与深色">
  </picture>
</p>

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
2. **Anki 连接** — 打开装好 [AnkiConnect](https://ankiweb.net/shared/info/2055492159) 插件的 Anki 桌面版，向导会自动找到它并建好笔记类型。*（服务器上没有 Anki 桌面版时，选择**内置 Anki** 并登录 AnkiWeb。）*
3. **语言** — 选择母语与目标语言。
4. **外观** — 选择配色方案与浅色/深色模式，Anki 卡片也会使用同一套配色。
5. **首张卡片** — 在向导中直接生成并保存你的第一张卡片。

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="docs/img/wizard-api.png" alt="设置向导第 1 步：连接 AI 模型"><br><sub>设置向导第 1 步：连接 AI 模型</sub></td>
    <td width="50%" valign="top" align="center"><img src="docs/img/wizard-anki-account.png" alt="设置向导第 2 步：连接 Anki"><br><sub>设置向导第 2 步：连接 Anki</sub></td>
  </tr>
</table>

如果想全局安装以便随时启动：

```bash
uv tool install ankinote-ai
ankinote-web
```

> **系统要求**：Linux 需 `glibc >= 2.35`（Ubuntu 22.04+、Debian 12+ 等）；同时支持 macOS 12+ 与 Windows。

---

## 🐳 Docker 自部署（NAS / 服务器）

将 AnkiNote 常驻在家用服务器或 NAS 上，电脑关着也能随时用手机浏览器制卡。在你平时用 Anki 的电脑上不需要 Docker，上面的快速上手就够了。Docker Hub 与 GHCR 均已提供多架构镜像（`amd64` + `arm64`）：`ghcr.io/ankinote-ai/ankinote` 与 `ignity21/ankinote-ai`。

```bash
# 内置 Anki + AnkiWeb 同步，无需桌面端
cd deploy/headless
cp .env.example .env      # 可选：配置 ANKIWEB_USERNAME / ANKIWEB_PASSWORD、端口等
docker compose up -d      # 访问 http://localhost:8080
```

如果想让容器改用带 AnkiConnect 的 Anki 桌面版，请使用 `deploy/standard`。AnkiNote 没有登录功能，请只在家庭内网或 Tailscale 这类私有网络里使用；要暴露到公网，必须放在要求登录的反向代理之后。完整部署说明与迁移指南请见 [`deploy/README.md`](deploy/README.md)。

---

## ⌨️ 在终端里用，或交给 AI Agent

`ankinote` 命令不用打开浏览器就能制卡，和 Web 应用共用同一份设置。所以任何能执行命令的 AI Agent（Claude Code、Codex 等）都可以替你调用它。

**从一张拍下来的书页开始。** 把划了生词的那一页拍下来，告诉 Agent：*“把划线的单词做成 Anki 卡片。”* 它会读图、挑出单词，然后执行：

```bash
ankinote word batch serendipity ephemeral eloquent
```

**从现成的单词表开始。** 一行一个词：

```bash
ankinote word batch --file words.txt --rpm 30
```

命令行做的卡不经预览，直接进 Anki。想先逐张检查再保存，就把同一份列表粘贴到 Web 应用的生成页面。

单独运行 `ankinote` 会在终端里打开菜单。短语、句子、STEM 卡片和全部选项见 [CLI 使用指南](docs/cli-usage.md)。

---

## 🤖 支持的模型服务

| 能力 | 内置预设与兼容范围 |
| --- | --- |
| **文本生成** | Gemini、OpenAI、Claude、DeepSeek，或任意 OpenAI 兼容接口（基于 `litellm`） |
| **图像生成** | Gemini、OpenAI（`gpt-image`）、fal.ai |
| **语音合成（TTS）** | Gemini TTS、OpenAI TTS、Google Cloud TTS |

Google Cloud TTS 需要单独的 Google Cloud 密钥（只允许 Cloud Text-to-Speech API），并且即使在每月免费额度内，所在项目也要开通结算；AI Studio 的密钥只能调用 Gemini API，在这里用不了。向导的「按内容分别设置」里列出了具体步骤。

所有 API Key 与设置都只保存在你自己的电脑上（`~/.config/ankinote/settings.json`）。

---

## 🛠️ 本地开发

```bash
git clone https://github.com/ankinote-ai/ankinote.git
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

## 🌐 社区

- [LINUX DO](https://linux.do/)

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE)。
