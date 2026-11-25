# AnkiNote

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/brand/mark-dark.svg">
    <img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/brand/mark-light.svg" width="96" alt="AnkiNote logo">
  </picture>
</p>

<p align="center">
  <strong>Turn any word, sentence, or STEM problem into a ready-to-review Anki card in seconds.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ankinote-ai/ankinote/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ankinote-ai/ankinote"><img src="https://img.shields.io/codecov/c/github/ankinote-ai/ankinote?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <strong>English</strong> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.zh-Hant.md">繁體中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a>
</p>

---

<p align="center">
  <img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/demo-hero.gif" width="860" alt="AnkiNote demo: type a word, generate the card, flip to the back">
</p>

Making great Anki cards shouldn't take longer than reviewing them. **AnkiNote** is an AI-powered Anki card studio that turns a single word, phrase, sentence, or STEM problem into a complete, styled flashcard — with explanations, examples, memory hooks, custom illustrations, and native-sounding audio — and saves it straight into your Anki.

No manual formatting. No copy-pasting between ChatGPT and Anki. Bring your own API key, run it anywhere, and review on your phone, tablet, or desktop.

---

## ✨ Why AnkiNote?

- **Works with the Anki You Already Have** — On the computer you study on, cards go straight into Anki Desktop through the AnkiConnect add-on: no second collection, nothing to download first, and Anki syncs them as usual. On an always-on home server or NAS, AnkiNote can run its own built-in Anki and sync with AnkiWeb instead, so you can add cards from your phone's browser while your computer is off.
- **One-Key Setup Wizard** — Paste a single Gemini AI Studio key and the 5-step onboarding wizard configures text, image, and speech routes for you. Or mix and match OpenAI, Claude, DeepSeek, fal.ai, Google Cloud TTS, and any OpenAI-compatible endpoint.
- **4 Card Modes: Word, Phrase, Sentence & STEM**
  - **Language Learning**: Definitions, natural examples, memory hooks/mnemonics, AI-generated illustrations, and TTS audio. Supports **English, French, Spanish, German, Japanese, Chinese (Simplified & Traditional, with ruby/pinyin), and Korean (beta)** — learn any of them, explained in any other.
  - **STEM & Problem Solving**: Type a question or **upload a photo of a problem** to generate a structured, step-by-step explanation card with MathJax formulas and optional diagrams.
- **Live Preview, Inline Editing & AI Rewrite** — Flip front/back and toggle Light/Dark mode before saving. Tweak any field directly, ask AI to rewrite a STEM explanation, or fix broken LaTeX with one click (with undo).
- **Curated Card Themes** — Choose from **Rosé Pine**, **Kanagawa**, **Tokyo Night**, and **Gruvbox** in both Light and Dark modes, with responsive layouts for desktop and mobile Anki.
- **Works with your AI agent** — The `ankinote` CLI lets Claude Code, Codex, or any agent that can run commands turn what you're reading into cards.

---

## 📸 Card & UI Showcase

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/showcase-word.png" alt="Language card: definition, illustration, examples"><br><sub>Language card: definition, illustration, examples</sub></td>
    <td width="50%" valign="top" align="center"><img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/showcase-stem.png" alt="STEM card: formulas and a step-by-step solution"><br><sub>STEM card: formulas and a step-by-step solution</sub></td>
  </tr>
</table>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/themes-dark.png">
    <img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/themes-light.png" width="860" alt="Four card palettes: Kanagawa, Tokyo Night, Gruvbox and Rosé Pine, in light and dark">
  </picture>
</p>

---

## 🚀 Quick Start (1 Minute)

The only prerequisite is [uv](https://docs.astral.sh/uv/getting-started/installation/) (it manages Python for you):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run AnkiNote directly without installing:

```bash
uvx --from ankinote-ai ankinote-web
```

Then open **<http://127.0.0.1:8000>** in your browser. On first launch, the **Setup Wizard** walks you through:

1. **AI Provider** — Paste a Gemini API key (covers text, image, and speech) or expand **Advanced** for OpenAI, Claude, DeepSeek, fal.ai, or custom endpoints.
2. **Anki Connection** — Open Anki Desktop with the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed; the wizard finds it and sets up the note types. *(On a server without Anki Desktop, choose **Built-in Anki** and sign in to AnkiWeb.)*
3. **Languages** — Pick your native and target languages.
4. **Appearance** — Choose a color palette and light or dark mode; your Anki cards get the same palette.
5. **First Card** — Generate and save your first card right inside the wizard.

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/wizard-api.png" alt="Setup wizard, step 1: connect an AI model"><br><sub>Setup wizard, step 1: connect an AI model</sub></td>
    <td width="50%" valign="top" align="center"><img src="https://raw.githubusercontent.com/ankinote-ai/ankinote/main/docs/img/wizard-anki-account.png" alt="Setup wizard, step 2: connect Anki"><br><sub>Setup wizard, step 2: connect Anki</sub></td>
  </tr>
</table>

To install globally as a command:

```bash
uv tool install ankinote-ai
ankinote-web
```

> **Note:** On Linux, `ankinote-ai` requires `glibc >= 2.35` (Ubuntu 22.04+, Debian 12+, or similar). macOS 12+ and Windows are also supported.

---

## 🐳 Self-Hosting with Docker

Run AnkiNote 24/7 on a home server or NAS so you can create cards from your phone's browser anytime, even with your computer off. On the computer where you use Anki you don't need Docker: the Quick Start above is all it takes. Multi-arch images (`amd64` + `arm64`) are published to `ghcr.io/ankinote-ai/ankinote` and `ignity21/ankinote-ai`.

```bash
# Built-in Anki + AnkiWeb sync, no desktop app needed
cd deploy/headless
cp .env.example .env      # optional: set ANKIWEB_USERNAME / ANKIWEB_PASSWORD, port, etc.
docker compose up -d      # open http://localhost:8080
```

To have the container use an Anki Desktop with AnkiConnect instead, use `deploy/standard`. See [`deploy/README.md`](deploy/README.md) for full deployment options, reverse-proxy tips, and migration guides.

AnkiNote has no login, so keep it on your home network or a private network such as Tailscale; don't expose it to the internet except behind a reverse proxy that asks for a login. It answers only to `localhost` and IP addresses. To open it by a host name (a reverse proxy, a Tailscale name), list that name in `ANKINOTE_ALLOWED_HOSTS`, comma-separated. This also applies when a proxy forwards to an IP address: without the name, saving, syncing and model lists fail with 403.

---

## ⌨️ From the Terminal or an AI Agent

The `ankinote` command makes cards without opening a browser, using the same settings as the web app. That makes it a tool any AI agent that can run commands (Claude Code, Codex, …) can use for you.

**From a photo of what you're reading.** Photograph a page where you underlined new words and tell your agent: *"Make Anki cards for the underlined words."* It reads the picture, picks out the words, and runs:

```bash
ankinote word batch serendipity ephemeral eloquent
```

**From a list you already have.** One word per line:

```bash
ankinote word batch --file words.txt --rpm 30
```

Cards from the CLI go straight to Anki without a preview. To check each card before it's saved, paste the same list into the web app's Generate page instead.

Run `ankinote` on its own for a menu in the terminal. The [CLI Usage Guide](docs/cli-usage.md) covers phrases, sentences, STEM, and every option. To teach your agent these commands, run `ankinote skill install` once (again after upgrading).

---

## 🤖 Supported Providers

| Capability | Built-in Presets & Compatibility |
| --- | --- |
| **Text Generation** | Gemini, OpenAI, Claude, DeepSeek, or any OpenAI-compatible endpoint (via `litellm`) |
| **Image Generation** | Gemini, OpenAI (`gpt-image`), fal.ai |
| **Text-to-Speech** | Gemini TTS, OpenAI TTS, Google Cloud TTS |

Google Cloud TTS takes its own Google Cloud key, restricted to the Cloud Text-to-Speech API, and needs billing turned on for its project even within the free monthly allowance; an AI Studio key is limited to the Gemini API and won't work. The wizard lists the steps under *Set up each kind of content separately*.

All API keys and settings stay on your machine, in `~/.config/ankinote/settings.json`.

---

## 🛠️ Development

```bash
git clone https://github.com/ankinote-ai/ankinote.git
cd ankinote-ai

uv sync                   # install Python dependencies (Python 3.14+)
make web-dev              # run Svelte + Vite frontend dev server
uv run ankinote-web       # run FastAPI backend
                          # (ANKINOTE_API_DOCS=1 serves API docs at /api/docs)

make test                 # run pytest suite
make format               # format with ruff
make check                # lint & type-check (ruff + ty)
```

---

## 📚 Documentation

- [CLI Usage Guide](docs/cli-usage.md)
- [Docker Deployment Guide](deploy/README.md)
- [Note Types Reference](docs/NoteType.org)
- [Agent Skill](src/ankinote/skills/ankinote-cli/SKILL.md) — for using AnkiNote with AI coding assistants

## 🌐 Community

- [LINUX DO](https://linux.do/)

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
