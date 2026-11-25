# AnkiNote

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/brand/mark-dark.svg">
    <img src="docs/brand/mark-light.svg" width="96" alt="AnkiNote logo">
  </picture>
</p>

<p align="center">
  <strong>単語・フレーズ・例文・理系（STEM）問題を、数秒で完成度の高い Anki カードに。</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/v/ankinote-ai?color=blue&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ankinote-ai/"><img src="https://img.shields.io/pypi/pyversions/ankinote-ai?color=blue&logo=python&logoColor=white" alt="Python versions"></a>
  <a href="https://github.com/ankinote-ai/ankinote/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ankinote-ai?color=blue" alt="License"></a>
  <a href="https://codecov.io/gh/ankinote-ai/ankinote"><img src="https://img.shields.io/codecov/c/github/ankinote-ai/ankinote?logo=codecov&logoColor=white" alt="Codecov"></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a> | <a href="README.zh-Hant.md">繁體中文</a> | <strong>日本語</strong> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a>
</p>

---

<p align="center">
  <img src="docs/img/demo-hero.gif" width="860" alt="AnkiNote のデモ：単語を入力し、カードを生成して、裏面へ">
</p>

カード作りが、復習そのものより大変であってはいけません。**AnkiNote** は、単語・フレーズ・例文・STEM（数学・理科・プログラミング）問題を入力するだけで、解説・例文・語呂合わせ（記憶フック）・AI イラスト・自然な音声を備えた完成品カードを自動生成し、そのまま Anki に保存できる AI カードスタジオです。

手作業のレイアウト調整も、ChatGPT と Anki の間のコピペも不要。自分の API キーでどこでも動かせ、スマホ・タブレット・PC からすぐに復習できます。

---

## ✨ AnkiNote の特長

- **いつもの Anki とそのまま連携** — デスクトップでは AnkiConnect 経由でいつもの Anki に直接保存（二重コレクション不要）。自宅サーバーや NAS では内蔵 Anki で AnkiWeb と同期し、スマホからもカードを追加できます。
- **API キー 1 つで簡単セットアップ** — 5 ステップウィザードに Gemini API キーを貼るだけでテキスト・画像・音声を一括設定。好みのプロバイダーを組み合わせることもできます。
- **4 つのカードモード：単語・フレーズ・例文・STEM**
  - **語学学習**：意味・自然な例文・記憶のヒント・AI イラスト・TTS 音声を作成。**英語・フランス語・スペイン語・ドイツ語・日本語・中国語（簡体字／繁体字・ルビ／ピンイン対応）・韓国語（Beta）** をどの言語ペアでも学習可能。
  - **STEM 問題演習**：問題文の入力、または**問題の写真・スクショをドロップ**するだけで、MathJax 数式と図解付きのステップ解説カードを生成。
- **リアルタイムプレビュー・直接編集・AI リライト** — 保存前に表裏反転やライト／ダークを確認。各フィールドの直接編集、STEM 解説の AI リライト、壊れた LaTeX のワンクリック修復（元に戻す対応）が可能。
- **洗練されたカードテーマ** — **Rosé Pine**、**Kanagawa**、**Tokyo Night**、**Gruvbox** の 4 パレット（ライト／ダーク両対応）、デスクトップ・モバイル最適化済み。
- **CLI ＆ AI エージェント対応** — `ankinote` CLI でターミナルから直接カード作成。Claude Code や Codex などのエージェントにも任せられます。

---

## 📸 カード ＆ 画面イメージ

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="docs/img/showcase-word.png" alt="語学カード：定義・イラスト・例文"><br><sub>語学カード：定義・イラスト・例文</sub></td>
    <td width="50%" valign="top" align="center"><img src="docs/img/showcase-stem.png" alt="STEM カード：数式とステップごとの解説"><br><sub>STEM カード：数式とステップごとの解説</sub></td>
  </tr>
</table>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/img/themes-dark.png">
    <img src="docs/img/themes-light.png" width="860" alt="4 つのカード配色：Kanagawa、Tokyo Night、Gruvbox、Rosé Pine（ライト／ダーク）">
  </picture>
</p>

---

## 🚀 1 分でクイックスタート

必要なのは [uv](https://docs.astral.sh/uv/getting-started/installation/) だけです（Python 環境も自動で用意されます）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストールせずにそのまま起動（毎回最新版で起動します）：

```bash
uvx --from ankinote-ai@latest ankinote-web
```

ブラウザで **<http://127.0.0.1:8000>** を開くと、初回**セットアップウィザード**が案内してくれます：

1. **AI プロバイダー** — Gemini API キーを貼り付けるだけ（テキスト・画像・音声すべてに対応）。**詳細設定**を開けば OpenAI、Claude、DeepSeek、fal.ai なども選択できます。
2. **Anki 連携** — [AnkiConnect](https://ankiweb.net/shared/info/2055492159) アドオンを入れたデスクトップ版 Anki を開いておくと、ウィザードが自動で見つけてノートタイプを作成します。*（デスクトップ版のないサーバーでは **内蔵 Anki** を選んで AnkiWeb にログインします。）*
3. **言語** — 母語と学習言語を選択します。
4. **外観** — カラーパレットとライト／ダークモードを選択します。Anki のカードにも同じパレットが適用されます。
5. **最初のカード** — ウィザード内で最初のカードを生成して保存できます。

<table>
  <tr>
    <td width="50%" valign="top" align="center"><img src="docs/img/wizard-api.png" alt="セットアップウィザード 手順 1：AI モデルに接続"><br><sub>セットアップウィザード 手順 1：AI モデルに接続</sub></td>
    <td width="50%" valign="top" align="center"><img src="docs/img/wizard-anki-account.png" alt="セットアップウィザード 手順 2：Anki に接続"><br><sub>セットアップウィザード 手順 2：Anki に接続</sub></td>
  </tr>
</table>

コマンドとして恒久インストールする場合：

```bash
uv tool install ankinote-ai
ankinote-web
```

> [!NOTE]
> - **動作環境**：Linux では `glibc >= 2.35`（Ubuntu 22.04+、Debian 12+ 等）が必要です。macOS 12+ および Windows にも対応しています。
> - **アップデート確認**：どの方法でインストールしても、起動時と 1 日 1 回 PyPI で新バージョンを確認し、**設定 → このアプリについて** に更新コマンドを表示します。`ANKINOTE_UPDATE_CHECK=0` で無効化できます。

---

## 🐳 Docker でのセルフホスト

自宅サーバーや NAS に常駐させれば、パソコンを切っていてもスマホのブラウザでいつでもカードを追加できます。普段 Anki を使うパソコンでは Docker は不要で、上のクイックスタートだけで十分です。マルチアーキテクチャ（`amd64` + `arm64`）イメージを `ghcr.io/ankinote-ai/ankinote` と `ignity21/ankinote-ai` で公開しています。

```bash
# Anki 内蔵 ＋ AnkiWeb 同期（デスクトップ版不要）
cd deploy/headless
cp .env.example .env      # 任意：ANKIWEB_USERNAME / ANKIWEB_PASSWORD、ポート等を設定
docker compose up -d      # http://localhost:8080 にアクセス
```

コンテナから AnkiConnect 付きのデスクトップ版 Anki を使う場合は `deploy/standard` を利用してください。詳細なデプロイ手順・リバースプロキシ・移行ガイドは [`deploy/README.md`](deploy/README.md) をご覧ください。

> [!IMPORTANT]
> - **ログイン機能なし**：自宅ネットワークや Tailscale などのプライベートネットワーク内で使用してください。インターネットに公開する場合は、必ず認証付きのリバースプロキシを挟んでください。
> - **カスタムホスト名（`ANKINOTE_ALLOWED_HOSTS`）**：既定では `localhost` と IP アドレスのみ受け付けます。リバースプロキシや Tailscale のホスト名でアクセスする場合は、そのホスト名をカンマ区切りで `ANKINOTE_ALLOWED_HOSTS` に指定してください（プロキシが IP に転送する場合も必要です。未設定だと保存・同期・モデル一覧が `403` で失敗します）。

---

## ⌨️ ターミナルや AI エージェントから使う

`ankinote` コマンドはブラウザを開かずにカードを作れ、Web アプリと同じ設定を使います。コマンドを実行できる AI エージェント（Claude Code、Codex など）なら、あなたの代わりに使えます。

**読んでいるページの写真から。** 新しい単語に線を引いたページを撮って、エージェントに *「線を引いた単語を Anki カードにして」* と頼むだけ。画像を読み、単語を拾い、次を実行します：

```bash
ankinote word batch serendipity ephemeral eloquent
```

**手元の単語リストから。** 1 行に 1 語：

```bash
ankinote word batch --file words.txt --rpm 30
```

CLI で作ったカードはプレビューなしで Anki に入ります。保存前に 1 枚ずつ確認したいときは、同じリストを Web アプリの生成ページに貼り付けてください。

`ankinote` だけを実行するとターミナルにメニューが開きます。フレーズ・文・STEM と全オプションは [CLI 利用ガイド](docs/cli-usage.md) を参照してください。エージェントにこれらのコマンドを教えるには、`ankinote skill install` を一度実行します（更新後にもう一度）。

---

## 💡 実践ワークフロー

通常の単語登録に加えて、日々の学習で特に役立つ 2 つのワークフローです：

### 出会った文の中で単語を覚える

記事や小説の文を「生成」ページに貼り付け、覚えたい単語（フレーズなら各部分）を角かっこで囲みます。かっこのない行はそのまま単語扱いなので、同じバッチに混ぜられます：

```text
We sat on the [bank] of the river.
I'll [pick] you [up] at six.
```

- **その意味だけ、すっきり整理** — 文中で使われている意味だけを解説（ここでの "bank" は「川岸」）。多義語や句動詞も散らかりません。
- **あなたの文が最初の例文に** — 読んだ文がそのままカードに残り、出会った文脈で復習できます。
- **活用形・言語を問わず対応** — 見たままの形（`ran`、`食べた`、ドイツ語 `Ich [rufe] dich [an]`）を囲めば辞書形に整えてくれます。

### 間違えた STEM 問題をカードにする

宿題や過去問で間違えた問題を撮り、「生成」ページを **STEM** にして画像を貼り付け／ドロップします（カード種類は **問題** または **自動**）：

- **画像なしで読める問題カードに** — 表面は画像なしでも完結する問題文に書き起こし、裏面に最終解答と段階的な解説を配置。
- **解法に気づくヒント付き** — 計算手順だけでなく、問題文のどの手がかりから解法を導けるかも示します。
- **保存前に数式をチェック** — プレビューで MathJax を確認し、**フィールドを編集** や **AI で修正** で整えてから保存できます。*（画像入力対応のメインモデルが必要。推奨の Gemini モデルは対応済みです。）*

---

## 🤖 対応プロバイダー

| 機能 | プリセット ＆ 互換性 |
| --- | --- |
| **テキスト生成** | Gemini、OpenAI、Claude、DeepSeek、その他 OpenAI 互換エンドポイント（`litellm` 経由） |
| **画像生成** | Gemini、OpenAI（`gpt-image`）、fal.ai |
| **音声合成（TTS）** | Gemini TTS、OpenAI TTS、Google Cloud TTS |

API キーと設定はすべて手元のマシン（`~/.config/ankinote/settings.json`）にだけ保存されます。

> [!NOTE]
> Google Cloud TTS には、Cloud Text-to-Speech API のみを許可した専用の Google Cloud キーと、無料枠内であってもプロジェクトの課金有効化が必要です。AI Studio のキーは Gemini API 専用のため使えません。手順はウィザードの「内容ごとに個別に設定」に表示されます。

---

## 🛠️ 開発

```bash
git clone https://github.com/ankinote-ai/ankinote.git
cd ankinote

uv sync                   # Python 依存関係のインストール（Python 3.14+）
make web-dev              # Svelte + Vite フロントエンド開発サーバー起動
uv run ankinote-web       # FastAPI バックエンド起動

make test                 # pytest 実行
make format               # ruff でフォーマット
make check                # リント ＆ 型チェック（ruff + ty）
```

---

## 📚 ドキュメント

- [CLI 利用ガイド](docs/cli-usage.md)
- [Docker デプロイガイド](deploy/README.md)
- [ノートタイプリファレンス](docs/NoteType.org)
- [Agent Skill](src/ankinote/skills/ankinote-cli/SKILL.md) — AI コーディングアシスタントとの連携用

## 🌐 コミュニティ

- [GitHub Discussions](https://github.com/ankinote-ai/ankinote/discussions) — 質問、アイデア、作ったカードの共有

## 📄 ライセンス

MIT License — 詳細は [LICENSE](LICENSE) をご覧ください。
