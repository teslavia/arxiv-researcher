# arXiv Researcher

> **論文をコード資産に変える** — Claude Code ネイティブの研究アシスタント。発見から実装、そして貢献まで、完全なループを構築します。

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

## 🚀 課題と解決策

エンジニアや研究者として、こんな経験はありませんか？
- 📄 **積読（ツンドク）**: PDFを100本保存しても、実際に読むのは10本以下。
- 🔧 **再現の地獄**: 環境構築ができない、コードが動かない、依存関係が解決しない。
- 🚫 **実用化の壁**: 学術的なコードは、そのままではプロダクション環境で使えない。
- 🗂️ **知識の断片化**: ノートやコードが散在し、後から振り返れない。

**arXiv Researcher** は、標準化された **SOP (標準作業手順)** でこれを解決します：

```mermaid
graph LR
    A[🔍 発見] --> B[📖 精読]
    B --> C[🔬 再現]
    C --> D[🛠️ エンジニアリング]
    D --> E[🌟 貢献]
```

## ⚡️ 30秒でクイックスタート

### 1. インストール

```bash
git clone https://github.com/teslavia/arxiv-researcher.git
cd arxiv-researcher
./install.sh
```

### 2. 使い方

Claude Code を再起動後、すぐに使用可能です：

```bash
# 1. 論文検索 (GitHub Stars ⭐ を自動表示)
/arxiv-search "speculative decoding"

# 2. プロジェクト初期化 (PDFダウンロード、ディレクトリ作成)
/arxiv-init 2401.12345

# 3. 深度リーディング (構造化されたノートを生成)
/arxiv-read

# 4. コード再現 (Clone、依存関係分析、環境構築)
/arxiv-repro

# 5. エンジニアリング・ラボ (API/ONNX/学習ループのスカフォールド生成)
/arxiv-lab api

# 6. オープンソース貢献 (Issue/PR/技術ブログの生成)
/arxiv-contrib blog
```

## 🌟 コア機能

### 🔍 インテリジェント検索 (`/arxiv-search`)
単なる検索ではなく、**フィルタリング**です。
- GitHub Stars を自動取得し、影響力を即座に判断。
- コード実装がある論文を優先的に表示。
- 無関係な結果を除外し、核心に到達します。

### 📁 標準化されたプロジェクト空間 (`/arxiv-init`)
すべての論文を独立した**エンジニアリング・プロジェクト**として扱います。
- `paper.pdf`: 論文の原本。
- `src/`: 公式の実装コード (gitignored)。
- `playground/`: 実験や魔改造用のコード。
- `SUMMARY.md`: 構造化されたナレッジベース。

### 📚 蓄積型ナレッジベース (Knowledge Base)
**「ブックマークの墓場」を拒絶し、あなたの「第二の脳」を構築します。**

- **カスタムストレージ**: インストール時に保存パスを選択可能（デフォルト: `~/knowledge/arxiv`）。データは完全にあなたのものです。
- **ローカルファースト**: すべてのPDF、コード、ノートはローカルに保存され、オフラインでもアクセス可能。
- **AI Ready**: 構造化されたノートは RAG (検索拡張生成) のコーパスとして最適化されています。
- **コンテキストの永続化**: `/arxiv-context` で、瞬時に「研究の現場」を復元します。

#### 🗃️ ディレクトリ構造

```text
~/knowledge/arxiv/             # ルートディレクトリ (設定可能)
├── README.md                  # グローバルダッシュボード
├── .context                   # 状態ファイル
├── cs.CL/                     # arXiv カテゴリ
│   └── 2401.12345_title/      # 論文プロジェクト
│       ├── info.yaml          # メタデータ
│       ├── paper.pdf          # 論文原本
│       ├── SUMMARY.md         # 詳細ノート
│       ├── REPRODUCTION.md    # 再現ログ
│       ├── src/               # 公式ソースコード
│       └── playground/        # 実験コード
└── ...
```

### 📖 深度リーディング (`/arxiv-read`)
AI が読書をアシストし、重要な情報を抽出します：
- **Context**: どのような核心的問題を解決するのか？
- **Method**: アーキテクチャと革新点。
- **Results**: 主要な指標の比較。
- **Open Questions**: 潜在的な改善の方向性。

### 🛠️ エンジニアリング・ラボ (`/arxiv-lab`)
**学術コードと本番環境の「ラストワンマイル」を埋めます。**
汎用的なディープラーニングのスカフォールド（足場）を生成し、Claude が論文の文脈に合わせてロジックを自動入力します。

| タイプ | 説明 | 適用シーン |
|------|------|----------|
| `demo` | 汎用推論スカフォールド | モデル効果の迅速な検証 |
| `api` | FastAPI マイクロサービス | 本番環境へのデプロイ |
| `train`| PyTorch 学習ループ | 学習プロセスの再現 |
| `onnx` | ONNX エクスポート | モデルの量子化と高速化 |
| `viz` | 可視化 Hook | Attention/Feature Map の解析 |

### 🌟 オープンソース貢献ジェネレーター (`/arxiv-contrib`)
あなたの再現経験をコミュニティへの貢献に変えます。
- **Issue**: 環境情報を含む再現失敗レポートを自動生成。
- **PR**: バグ修正や新機能の提案。
- **Blog**: 技術ブログを一発生成し、知見をシェア。

## 🧩 拡張システム

自然言語であなた専用のワークフローを定義できます：

```bash
# ポッドキャスト台本ジェネレーターを作成
/arxiv-extend create podcast -i "論文の長所と短所を議論する5分間のポッドキャスト台本を生成"

# Notion インポート用フォーマット
/arxiv-extend create notion -i "Notion データベースのインポート形式に整形"
```

## 🤝 貢献

PRの送信は大歓迎です！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## 📄 ライセンス

MIT License
