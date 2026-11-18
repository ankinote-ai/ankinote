# AnkiNote

<p align="center">
  <img src="src/ankinote/ui/static/ankinote-logo.svg" width="96" alt="AnkiNote logo">
</p>

<p align="center">
  <strong>Turn any word, sentence, or STEM problem into a ready-to-review Anki card in seconds.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ignity21/ankinote-ai/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ignity21/ankinote-ai"><img src="https://img.shields.io/codecov/c/github/ignity21/ankinote-ai?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <strong>English</strong> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a>
</p>

---

<!-- MEDIA PLACEHOLDER #1: Hero Demo GIF / Video (recommended: docs/img/demo-hero.gif)
     Show: Typing a word or uploading a STEM problem -> AI generates the card ->
     flipping Front/Back preview -> clicking Save to sync straight to Anki. -->

Making great Anki cards shouldn't take longer than reviewing them. **AnkiNote** is an AI-powered Anki card studio that turns a single word, phrase, sentence, or STEM problem into a complete, styled flashcard — with explanations, examples, memory hooks, custom illustrations, and native-sounding audio — and syncs it straight to your AnkiWeb account.

No manual formatting. No copy-pasting between ChatGPT and Anki. Bring your own API key, run it anywhere, and review on your phone, tablet, or desktop.

---

## ✨ Why AnkiNote?

- **Built-in Anki & AnkiWeb Sync** — No Anki Desktop or AnkiConnect required. AnkiNote embeds the Anki engine directly and syncs with AnkiWeb automatically, so cards added from a browser or NAS appear on every device. *(Already use Anki Desktop? AnkiConnect is supported too.)*
- **One-Key Setup Wizard** — Paste a single Gemini AI Studio key and the 5-step onboarding wizard configures text, image, and speech routes for you. Or mix and match OpenAI, Claude, DeepSeek, fal.ai, Google Cloud TTS, and any OpenAI-compatible endpoint.
- **4 Card Modes: Word, Phrase, Sentence & STEM**
  - **Language Learning**: Definitions, natural examples, memory hooks/mnemonics, AI-generated illustrations, and TTS audio. Supports **English, French, Spanish, German, Japanese, Chinese (Simplified & Traditional, with ruby/pinyin), and Korean (beta)** — learn any of them, explained in any other.
  - **STEM & Problem Solving**: Type a question or **upload a photo of a problem** to generate a structured, step-by-step explanation card with MathJax formulas and optional diagrams.
- **Live Preview, Inline Editing & AI Rewrite** — Flip front/back and toggle Light/Dark mode before saving. Tweak any field directly, ask AI to rewrite a STEM explanation, or fix broken LaTeX with one click (with undo).
- **Curated Card Themes** — Choose from **Rosé Pine**, **Kanagawa**, **Tokyo Night**, and **Gruvbox** in both Light and Dark modes, with responsive layouts for desktop and mobile Anki.
- **Web App + CLI** — A modern Svelte web studio (`ankinote-web`) for daily card creation, plus a scriptable CLI & TUI (`ankinote`) for batch workflows.

---

## 📸 Card & UI Showcase

<!-- MEDIA PLACEHOLDER #2a: Language Card Showcase (recommended: docs/img/showcase-word.png)
     Show: A generated Word/Sentence card in preview or Anki (front/back with image, ruby/phonetics, example, audio). -->

<!-- MEDIA PLACEHOLDER #2b: STEM Card Showcase (recommended: docs/img/showcase-stem.png)
     Show: A STEM card generated from a problem or photo, with MathJax formulas and step-by-step explanation. -->

<!-- MEDIA PLACEHOLDER #3: Card Themes Comparison (docs/img/themes-light.png + docs/img/themes-dark.png, swapped by GitHub's color scheme via <picture>)
     Show: Rosé Pine, Kanagawa, Tokyo Night, and Gruvbox palettes side by side. -->

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
2. **Anki Connection** — Choose **Built-in Anki** and sign in to AnkiWeb *(or choose **AnkiConnect** if you keep Anki Desktop open)*.
3. **Languages** — Pick your native and target languages.
4. **Appearance** — Choose a color palette and light or dark mode; your Anki cards get the same palette.
5. **First Card** — Generate and save your first card right inside the wizard.

<!-- MEDIA PLACEHOLDER #4: Setup Wizard Screenshot (recommended: docs/img/wizard-setup.png)
     Show: The 5-step onboarding wizard in the web UI. -->

To install globally as a command:

```bash
uv tool install ankinote-ai
ankinote-web
```

> **Note:** On Linux, `ankinote-ai` requires `glibc >= 2.35` (Ubuntu 22.04+, Debian 12+, or similar). macOS 12+ and Windows are also supported.

---

## 🐳 Self-Hosting with Docker

Run AnkiNote 24/7 on a server, VPS, or NAS so you can create cards from your phone's browser anytime. Multi-arch images (`amd64` + `arm64`) are published to `ghcr.io/ignity21/ankinote-ai` and `ignity21/ankinote-ai`.

```bash
# Standalone mode (recommended — built-in Anki + AnkiWeb sync, no desktop app needed)
cd deploy/headless
cp .env.example .env      # optional: set ANKIWEB_USERNAME / ANKIWEB_PASSWORD, port, etc.
docker compose up -d      # open http://localhost:8080
```

Already running Anki Desktop with AnkiConnect? Use `deploy/standard` instead. See [`deploy/README.md`](deploy/README.md) for full deployment options, reverse-proxy tips, and migration guides.

---

## ⌨️ CLI & Batch Mode

AnkiNote also ships a CLI (`ankinote`) that shares the same `settings.json` (`~/.config/ankinote/settings.json`) as the Web App:

```bash
ankinote                  # open the interactive terminal UI (TUI)
ankinote word ephemeral   # generate a vocabulary card
ankinote stem "..."       # generate a STEM card
ankinote profiles list    # inspect configured provider profiles
```

See the [CLI Usage Guide](docs/cli-usage.md) for batch lists, flags, and automation examples.

---

## 🤖 Supported Providers

| Capability | Built-in Presets & Compatibility |
| --- | --- |
| **Text Generation** | Gemini, OpenAI, Claude, DeepSeek, or any OpenAI-compatible endpoint (via `litellm`) |
| **Image Generation** | Gemini, OpenAI (`gpt-image`), fal.ai |
| **Text-to-Speech** | Gemini TTS, OpenAI TTS, Google Cloud TTS |

All API keys and settings are stored locally on your machine (`~/.config/ankinote/settings.json`) and can be exported/imported as an encrypted backup bundle (`scrypt` + `AES-256-GCM`) from **Settings**.

---

## 🛠️ Development

```bash
git clone https://github.com/ignity21/ankinote-ai.git
cd ankinote-ai

uv sync                   # install Python dependencies (Python 3.14+)
make web-dev              # run Svelte + Vite frontend dev server
uv run ankinote-web       # run FastAPI backend

make test                 # run pytest suite
make format               # format with ruff
make check                # lint & type-check (ruff + ty)
```

---

## 📚 Documentation

- [CLI Usage Guide](docs/cli-usage.md)
- [Docker Deployment Guide](deploy/README.md)
- [Note Types Reference](docs/NoteType.org)
- [Agent Skill](.agents/skills/ankinote-cli/SKILL.md) — for using AnkiNote with AI coding assistants

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
