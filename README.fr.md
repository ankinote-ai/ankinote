# AnkiNote

<p align="center">
  <img src="src/ankinote/ui/static/ankinote-logo.svg" width="96" alt="AnkiNote logo">
</p>

<p align="center">
  <strong>Transformez n'importe quel mot, phrase ou problème STEM en une carte Anki prête à réviser en quelques secondes.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ignity21/ankinote-ai/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ignity21/ankinote-ai"><img src="https://img.shields.io/codecov/c/github/ignity21/ankinote-ai?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <strong>Français</strong>
</p>

---

<!-- MEDIA PLACEHOLDER #1: Hero Demo GIF / Video (recommended: docs/img/demo-hero.gif)
     Montrer : saisie d'un mot ou import d'une photo de problème STEM -> génération par l'IA ->
     aperçu Recto/Verso -> clic sur Enregistrer et synchronisation vers Anki. -->

Créer de bonnes cartes Anki ne devrait pas prendre plus de temps que de les réviser. **AnkiNote** est un studio de cartes Anki propulsé par l'IA qui transforme un mot, une expression, une phrase ou un problème STEM en une carte complète et soignée — avec définitions, exemples, moyens mnémotechniques, illustrations et audio naturel — puis la synchronise directement avec votre compte AnkiWeb.

Fini la mise en forme manuelle et les copier-coller entre ChatGPT et Anki. Utilisez votre propre clé API, hébergez-le où vous voulez et révisez sur téléphone, tablette ou ordinateur.

---

## ✨ Pourquoi AnkiNote ?

- **Anki intégré & synchronisation AnkiWeb** — Aucun besoin d'ouvrir Anki Desktop ni AnkiConnect. AnkiNote embarque le moteur Anki et se synchronise automatiquement avec AnkiWeb : les cartes créées depuis un navigateur ou un NAS apparaissent sur tous vos appareils. *(AnkiConnect reste pris en charge si vous utilisez déjà Anki Desktop.)*
- **Configuration en une seule clé** — Collez une clé Gemini AI Studio et l'assistant en 5 étapes configure automatiquement le texte, les images et la voix. Vous pouvez aussi combiner OpenAI, Claude, DeepSeek, fal.ai, Google Cloud TTS ou tout endpoint compatible OpenAI.
- **4 modes de cartes : Mot, Expression, Phrase et STEM**
  - **Apprentissage des langues** : Définitions, exemples authentiques, astuces mnémotechniques, illustrations générées par IA et audio TTS. Prend en charge **l'anglais, le français, l'espagnol, l'allemand, le japonais, le chinois (simplifié et traditionnel, avec annotations ruby/pinyin) et le coréen (bêta)**.
  - **STEM & résolution de problèmes** : Saisissez un énoncé ou **importez la photo d'un exercice** pour obtenir une carte structurée avec explication étape par étape, formules MathJax et schémas optionnels.
- **Aperçu en direct, édition directe & réécriture IA** — Retournez le recto/verso et basculez entre mode clair et sombre avant d'enregistrer. Modifiez n'importe quel champ directement, demandez à l'IA de réécrire une explication STEM ou réparez les formules LaTeX cassées en un clic (avec annulation).
- **Thèmes de cartes soignés** — Choisissez parmi **Rosé Pine**, **Kanagawa**, **Tokyo Night** et **Gruvbox** en modes clair et sombre, adaptés au bureau comme au mobile.
- **Application Web + CLI** — Un studio web moderne en Svelte (`ankinote-web`) pour l'usage quotidien, accompagné d'une CLI et TUI (`ankinote`) pour le traitement par lots.

---

## 📸 Aperçu des cartes et de l'interface

<!-- MEDIA PLACEHOLDER #2a: Language Card Showcase (recommended: docs/img/showcase-word.png)
     Montrer : carte de langue générée (illustration, phonétique/ruby, exemple, audio). -->

<!-- MEDIA PLACEHOLDER #2b: STEM Card Showcase (recommended: docs/img/showcase-stem.png)
     Montrer : carte STEM générée à partir d'un texte ou d'une photo (formules MathJax et explication). -->

<!-- MEDIA PLACEHOLDER #3: Card Themes Comparison (docs/img/themes-light.png + docs/img/themes-dark.png, swapped by GitHub's color scheme via <picture>)
     Montrer : les 4 thèmes (Rosé Pine, Kanagawa, Tokyo Night, Gruvbox) côte à côte. -->

---

## 🚀 Démarrage rapide (1 minute)

Le seul prérequis est [uv](https://docs.astral.sh/uv/getting-started/installation/) (il gère Python automatiquement) :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Lancez AnkiNote directement sans installation :

```bash
uvx --from ankinote-ai ankinote-web
```

Ouvrez **<http://127.0.0.1:8000>** dans votre navigateur. Au premier lancement, **l'assistant de configuration** vous guide :

1. **Fournisseur IA** — Collez une clé Gemini (texte, image et voix inclus) ou ouvrez **Avancé** pour OpenAI, Claude, DeepSeek, fal.ai ou des endpoints personnalisés.
2. **Connexion Anki** — Choisissez **Anki intégré** et connectez-vous à AnkiWeb *(ou choisissez **AnkiConnect** avec Anki Desktop)*.
3. **Langues** — Sélectionnez votre langue maternelle et la langue cible.
4. **Apparence** — Choisissez la palette de couleurs et le mode clair ou sombre ; vos cartes Anki adoptent la même palette.
5. **Première carte** — Générez et enregistrez votre première carte directement depuis l'assistant.

<!-- MEDIA PLACEHOLDER #4: Setup Wizard Screenshot (recommended: docs/img/wizard-setup.png)
     Montrer : l'assistant de configuration en 5 étapes dans l'interface web. -->

Pour l'installer globalement :

```bash
uv tool install ankinote-ai
ankinote-web
```

> **Note :** Sous Linux, `ankinote-ai` requiert `glibc >= 2.35` (Ubuntu 22.04+, Debian 12+ ou équivalent). Compatible également avec macOS 12+ et Windows.

---

## 🐳 Auto-hébergement avec Docker

Hébergez AnkiNote 24h/24 sur un serveur, VPS ou NAS pour créer des cartes depuis votre téléphone à tout moment. Images multi-arch (`amd64` + `arm64`) publiées sur `ghcr.io/ignity21/ankinote-ai` et `ignity21/ankinote-ai`.

```bash
# Mode autonome (recommandé : Anki intégré + synchro AnkiWeb)
cd deploy/headless
cp .env.example .env      # optionnel : ANKIWEB_USERNAME / ANKIWEB_PASSWORD, port, etc.
docker compose up -d      # ouvrez http://localhost:8080
```

Si vous utilisez déjà Anki Desktop avec AnkiConnect, utilisez `deploy/standard`. Consultez [`deploy/README.md`](deploy/README.md) pour tous les détails.

---

## ⌨️ CLI & traitement par lots

La CLI (`ankinote`) partage le même fichier `settings.json` (`~/.config/ankinote/settings.json`) que l'application Web :

```bash
ankinote                  # ouvre l'interface terminal interactive (TUI)
ankinote word ephemeral   # génère une carte de vocabulaire
ankinote stem "..."       # génère une carte STEM
ankinote profiles list    # affiche les profils configurés
```

Consultez le [Guide d'utilisation CLI](docs/cli-usage.md) pour les listes par lots et l'automatisation.

---

## 🤖 Fournisseurs pris en charge

| Capacité | Préréglages et compatibilité |
| --- | --- |
| **Génération de texte** | Gemini, OpenAI, Claude, DeepSeek ou tout endpoint compatible OpenAI (via `litellm`) |
| **Génération d'images** | Gemini, OpenAI (`gpt-image`), fal.ai |
| **Synthèse vocale (TTS)** | Gemini TTS, OpenAI TTS, Google Cloud TTS |

Toutes vos clés API et réglages sont stockés localement (`~/.config/ankinote/settings.json`) et peuvent être exportés/importés dans un fichier chiffré (`scrypt` + `AES-256-GCM`) depuis **Paramètres**.

---

## 🛠️ Développement

```bash
git clone https://github.com/ignity21/ankinote-ai.git
cd ankinote-ai

uv sync                   # installer les dépendances Python (Python 3.14+)
make web-dev              # serveur de dev Svelte + Vite
uv run ankinote-web       # serveur backend FastAPI

make test                 # lancer les tests pytest
make format               # formater avec ruff
make check                # lint et vérification des types (ruff + ty)
```

---

## 📚 Documentation

- [Guide d'utilisation CLI](docs/cli-usage.md)
- [Guide de déploiement Docker](deploy/README.md)
- [Référence des types de notes](docs/NoteType.org)
- [Agent Skill](.agents/skills/ankinote-cli/SKILL.md) — pour utiliser AnkiNote avec des assistants de code IA

## 📄 Licence

Licence MIT — voir [LICENSE](LICENSE) pour plus de détails.
