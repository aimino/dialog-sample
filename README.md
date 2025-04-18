# 対話型AIシステム プロトタイプ

このプロジェクトは、ユーザーの曖昧な質問に対して追加の質問を行い、具体的な回答ができるようになるまで対話を続ける対話型AIシステムのプロトタイプです。

## 機能

- ユーザーとの対話インターフェース（Webアプリケーション）
- 曖昧な質問の検出
- 文脈に応じたフォローアップ質問の生成
- 会話履歴の管理
- Claude APIとの統合（開発用ダミーレスポンス機能付き）

## システム構成

プロトタイプは以下のコンポーネントで構成されています：

1. **Claude API統合モジュール** (`claude_api.py`)
   - Claude APIとの通信
   - APIキーがない場合のダミーレスポンス生成
   - 曖昧さに基づく応答の調整

2. **会話管理システム** (`conversation.py`)
   - 会話履歴の追跡
   - メタデータと文脈情報の管理
   - 会話の保存と読み込み

3. **曖昧さ検出モジュール** (`ambiguity.py`)
   - パターンマッチングによる曖昧さの検出
   - 文脈に基づく曖昧さの評価
   - 曖昧さスコアの計算

4. **フォローアップ質問生成モジュール** (`follow_up.py`)
   - 曖昧さのタイプに基づく質問テンプレート
   - 文脈を考慮した質問生成
   - 特定の曖昧さに対応する質問の生成

5. **Webインターフェース** (`app.py`, `templates/`, `static/`)
   - Flaskベースのバックエンド
   - レスポンシブなフロントエンドデザイン
   - リアルタイムの対話機能

## 技術スタック

- **バックエンド**: Python, Flask
- **フロントエンド**: HTML, CSS, JavaScript
- **AI**: Claude API (Anthropic)
- **データ保存**: ファイルベース (JSON)

## インストール方法

### 前提条件

- Python 3.6以上
- pip (Pythonパッケージマネージャー)

### セットアップ

1. リポジトリをクローンまたはダウンロードします

2. 必要なパッケージをインストールします
   ```bash
   pip install flask anthropic
   ```

3. （オプション）Claude APIキーを設定します
   - 実際のAPIキーを使用する場合は、`app.py`の以下の行を変更します
   ```python
   claude_api = ClaudeAPI(api_key="YOUR_API_KEY_HERE")
   ```
   - APIキーがない場合は、デフォルトの「dummy」モードで動作します

## 使用方法

1. アプリケーションを起動します
   ```bash
   cd interactive_ai_prototype
   python -m flask run --host=0.0.0.0
   ```

2. ウェブブラウザで以下のURLにアクセスします
   ```
   http://localhost:5000
   ```

3. チャットインターフェースでAIと対話を開始します
   - 曖昧な質問をすると、AIは追加の質問を行います
   - 具体的な質問をすると、AIは直接回答します

## 開発ガイド

### 新機能の追加

1. **新しい曖昧さパターンの追加**
   - `ambiguity.py`の`AmbiguityDetector`クラスの`ambiguity_patterns`リストに新しいパターンを追加します

2. **新しいフォローアップ質問テンプレートの追加**
   - `follow_up.py`の`FollowUpQuestionGenerator`クラスの`question_templates`辞書に新しいテンプレートを追加します

3. **システムプロンプトのカスタマイズ**
   - `app.py`の`SYSTEM_PROMPT`変数を編集して、AIの応答スタイルを調整します

### デバッグ

- 曖昧さ検出のデバッグ:
  ```python
  detector = AmbiguityDetector()
  details = detector.get_ambiguity_details("あなたの質問")
  print(details)
  ```

- フォローアップ質問生成のデバッグ:
  ```python
  generator = FollowUpQuestionGenerator()
  question = generator.generate_follow_up_question("あなたの質問", ambiguity_details)
  print(question)
  ```

## プロジェクト構造

```
interactive_ai_prototype/
├── app.py                  # Flaskアプリケーションのメインファイル
├── claude_api.py           # Claude API統合モジュール
├── conversation.py         # 会話管理システム
├── ambiguity.py            # 曖昧さ検出モジュール
├── follow_up.py            # フォローアップ質問生成モジュール
├── templates/
│   └── index.html          # メインHTMLテンプレート
├── static/
│   ├── css/
│   │   └── style.css       # スタイルシート
│   └── js/
│       └── script.js       # フロントエンドJavaScript
└── conversations/          # 会話履歴の保存ディレクトリ
```

## 将来の拡張可能性

1. **本番環境用のデータベース統合**
   - 会話履歴をJSONファイルからデータベースに移行

2. **ユーザー認証システム**
   - 複数ユーザーのサポートとパーソナライズされた体験

3. **高度な自然言語処理**
   - より洗練された曖昧さ検出アルゴリズム
   - トピックモデリングによる文脈理解の向上

4. **マルチモーダル対応**
   - 画像や音声入力のサポート

5. **APIエンドポイント**
   - 他のアプリケーションとの統合のためのRESTful API

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 謝辞

このプロジェクトはAnthropicのClaude APIを使用しています。
