# AnkiNote

<p align="center">
  <img src="src/ankinote/ui/static/ankinote-logo.svg" width="96" alt="AnkiNote logo">
</p>

<p align="center">
  <strong>Convierte cualquier palabra, frase o problema STEM en una tarjeta Anki lista para repasar en segundos.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ignity21/ankinote-ai/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ignity21/ankinote-ai"><img src="https://img.shields.io/codecov/c/github/ignity21/ankinote-ai?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <strong>Español</strong> | <a href="README.fr.md">Français</a>
</p>

---

<!-- MEDIA PLACEHOLDER #1: Hero Demo GIF / Video (recommended: docs/img/demo-hero.gif)
     Mostrar: Escribir una palabra o subir la foto de un problema STEM -> generación con IA ->
     voltear vista previa Anverso/Reverso -> guardar y sincronizar con Anki. -->

Crear buenas tarjetas de Anki no debería llevar más tiempo que repasarlas. **AnkiNote** es un estudio de tarjetas Anki impulsado por IA que transforma una palabra, expresión, oración o problema STEM en una tarjeta completa y estilizada — con definiciones, ejemplos, reglas mnemotécnicas, ilustraciones y audio natural — y la sincroniza directamente con tu cuenta de AnkiWeb.

Sin formato manual. Sin copiar y pegar entre ChatGPT y Anki. Usa tu propia clave API, ejecútalo donde quieras y repasa desde tu móvil, tablet u ordenador.

---

## ✨ ¿Por qué AnkiNote?

- **Anki integrado y sincronización con AnkiWeb** — No necesitas tener Anki Desktop ni AnkiConnect abiertos. AnkiNote incorpora el motor de Anki y sincroniza automáticamente con AnkiWeb, para que cualquier tarjeta creada desde el navegador o un NAS aparezca en todos tus dispositivos. *(Si ya usas Anki Desktop, AnkiConnect también es compatible.)*
- **Configuración con una sola clave** — Pega una clave de Gemini AI Studio y el asistente inicial de 5 pasos configurará texto, imágenes y voz automáticamente. También puedes combinar OpenAI, Claude, DeepSeek, fal.ai, Google Cloud TTS o cualquier endpoint compatible con OpenAI.
- **4 modos de tarjeta: Palabra, Frase, Oración y STEM**
  - **Aprendizaje de idiomas**: Definiciones, ejemplos reales, trucos de memoria, ilustraciones generadas por IA y audio TTS. Compatible con **inglés, francés, español, alemán, japonés, chino (simplificado y tradicional, con anotaciones ruby/pinyin) y coreano (beta)**.
  - **STEM y resolución de problemas**: Escribe un enunciado o **sube una foto del problema** para generar una tarjeta con explicación paso a paso, fórmulas MathJax y diagramas opcionales.
- **Vista previa en vivo, edición directa y reescritura con IA** — Voltea anverso/reverso y alterna entre modo claro/oscuro antes de guardar. Edita cualquier campo directamente, pide a la IA que reescriba una explicación STEM o corrige fórmulas LaTeX rotas en un clic (con deshacer).
- **Temas visuales cuidados** — Elige entre **Rosé Pine**, **Kanagawa**, **Tokyo Night** y **Gruvbox** (modos claro y oscuro), adaptados a escritorio y móvil.
- **App Web + CLI** — Una moderna interfaz web en Svelte (`ankinote-web`) para el día a día, más una CLI y TUI (`ankinote`) para lotes y scripts.

---

## 📸 Galería de tarjetas e interfaz

<!-- MEDIA PLACEHOLDER #2a: Language Card Showcase (recommended: docs/img/showcase-word.png)
     Mostrar: Tarjeta de idioma generada (imagen, pronunciación/ruby, ejemplo, audio). -->

<!-- MEDIA PLACEHOLDER #2b: STEM Card Showcase (recommended: docs/img/showcase-stem.png)
     Mostrar: Tarjeta STEM generada desde texto o foto (fórmulas MathJax y explicación paso a paso). -->

<!-- MEDIA PLACEHOLDER #3: Card Themes Comparison (docs/img/themes-light.png + docs/img/themes-dark.png, swapped by GitHub's color scheme via <picture>)
     Mostrar: los 4 temas (Rosé Pine, Kanagawa, Tokyo Night, Gruvbox) lado a lado. -->

---

## 🚀 Inicio rápido (1 minuto)

El único requisito es [uv](https://docs.astral.sh/uv/getting-started/installation/) (gestiona Python automáticamente):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Ejecuta AnkiNote directamente sin instalarlo:

```bash
uvx --from ankinote-ai ankinote-web
```

Abre **<http://127.0.0.1:8000>** en tu navegador. En el primer arranque, el **asistente de configuración** te guiará paso a paso:

1. **Proveedor de IA** — Pega tu clave de Gemini (cubre texto, imagen y voz) o abre **Avanzado** para OpenAI, Claude, DeepSeek, fal.ai o endpoints personalizados.
2. **Conexión con Anki** — Elige **Anki integrado** e inicia sesión en AnkiWeb *(o elige **AnkiConnect** si usas Anki Desktop)*.
3. **Idiomas** — Selecciona tu idioma nativo y el idioma objetivo.
4. **Apariencia** — Elige la paleta de colores y el modo claro u oscuro; tus tarjetas de Anki usan la misma paleta.
5. **Primera tarjeta** — Genera y guarda tu primera tarjeta sin salir del asistente.

<!-- MEDIA PLACEHOLDER #4: Setup Wizard Screenshot (recommended: docs/img/wizard-setup.png)
     Mostrar: El asistente inicial de 5 pasos en la interfaz web. -->

Para instalarlo de forma permanente:

```bash
uv tool install ankinote-ai
ankinote-web
```

> **Nota:** En Linux, `ankinote-ai` requiere `glibc >= 2.35` (Ubuntu 22.04+, Debian 12+ o similar). También compatible con macOS 12+ y Windows.

---

## 🐳 Autoalojamiento con Docker

Ejecuta AnkiNote 24/7 en un servidor, VPS o NAS para crear tarjetas desde el móvil en cualquier momento. Imágenes multi-arquitectura (`amd64` + `arm64`) disponibles en `ghcr.io/ignity21/ankinote-ai` e `ignity21/ankinote-ai`.

```bash
# Modo autónomo (recomendado: Anki integrado + sincronización AnkiWeb)
cd deploy/headless
cp .env.example .env      # opcional: ANKIWEB_USERNAME / ANKIWEB_PASSWORD, puerto, etc.
docker compose up -d      # abre http://localhost:8080
```

Si ya ejecutas Anki Desktop con AnkiConnect, usa `deploy/standard`. Consulta [`deploy/README.md`](deploy/README.md) para ver todas las opciones.

---

## ⌨️ CLI y modo por lotes

La CLI (`ankinote`) comparte el mismo archivo `settings.json` (`~/.config/ankinote/settings.json`) que la aplicación web:

```bash
ankinote                  # abre el menú interactivo en terminal (TUI)
ankinote word ephemeral   # genera una tarjeta de vocabulario
ankinote stem "..."       # genera una tarjeta STEM
ankinote profiles list    # consulta los perfiles configurados
```

Consulta la [Guía de uso de la CLI](docs/cli-usage.md) para listas por lotes y automatización.

---

## 🤖 Proveedores compatibles

| Capacidad | Preajustes y compatibilidad |
| --- | --- |
| **Generación de texto** | Gemini, OpenAI, Claude, DeepSeek o cualquier endpoint compatible con OpenAI (vía `litellm`) |
| **Generación de imágenes** | Gemini, OpenAI (`gpt-image`), fal.ai |
| **Texto a voz (TTS)** | Gemini TTS, OpenAI TTS, Google Cloud TTS |

Todas las claves y ajustes se guardan localmente (`~/.config/ankinote/settings.json`) y pueden exportarse/importarse en un archivo cifrado (`scrypt` + `AES-256-GCM`) desde **Ajustes**.

---

## 🛠️ Desarrollo

```bash
git clone https://github.com/ignity21/ankinote-ai.git
cd ankinote-ai

uv sync                   # instalar dependencias Python (Python 3.14+)
make web-dev              # servidor de desarrollo Svelte + Vite
uv run ankinote-web       # servidor backend FastAPI

make test                 # ejecutar tests con pytest
make format               # formatear con ruff
make check                # lint y comprobación de tipos (ruff + ty)
```

---

## 📚 Documentación

- [Guía de uso de la CLI](docs/cli-usage.md)
- [Guía de despliegue con Docker](deploy/README.md)
- [Referencia de tipos de nota](docs/NoteType.org)
- [Agent Skill](.agents/skills/ankinote-cli/SKILL.md) — para usar AnkiNote con asistentes de programación IA

## 📄 Licencia

Licencia MIT — consulta el archivo [LICENSE](LICENSE) para más detalles.
