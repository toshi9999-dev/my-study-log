# 🗣️ AI English Conversation App

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.29+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg" alt="OpenAI">
</p>

<p align="center">
  <strong>🎯 AIを活用した次世代英会話練習アプリ</strong><br>
  音声認識・生成AI・リアルタイム評価で、あなたの英語力を飛躍的に向上させます
</p>

## ✨ 特徴

### 🎙️ **3つの学習モード**
- **日常英会話**: AIとの自然な会話で実践的なスピーキング力を向上
- **シャドーイング**: ネイティブレベルの発音とリズムを身につける
- **ディクテーション**: 正確な聞き取り能力を鍛える

### 🤖 **AI駆動の高度な機能**
- **リアルタイム音声認識**: 高精度な音声→テキスト変換
- **インテリジェント評価**: 発音・語彙・文法・流暢性を多角的に分析
- **適応的学習**: ユーザーのレベルに応じた問題生成
- **自然な音声合成**: 高品質なAI音声での問題読み上げ

### 🎯 **詳細な学習フィードバック**
- 4つの評価軸（発音・語彙・文法・流暢性）で40点満点評価
- 具体的な改善ポイントと練習方法の提案
- モチベーション維持のための励ましメッセージ

## 🚀 クイックスタート

### 前提条件
- Python 3.11以上
- OpenAI APIキー
- マイク・スピーカー付きデバイス

### インストール

1. **リポジトリのクローン**
```bash
git clone https://github.com/toshi9999-dev/my-study-log.git
cd my-study-log
```

2. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

3. **OpenAI APIキーの設定**
```bash
# .envファイルを作成
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```
OpenAI APIキーは [OpenAI Platform](https://platform.openai.com/api-keys) で取得してください。`.env` はGit管理対象外です。公開環境にデプロイする場合は、利用するサービスのシークレット設定に `OPENAI_API_KEY` を登録してください。

4. **アプリの起動**
```bash
streamlit run main.py
```

## 📱 使い方

### 基本操作
1. **モード選択**: 日常英会話・シャドーイング・ディクテーションから選択
2. **レベル設定**: 初級者・中級者・上級者から自分のレベルを選択
3. **再生速度調整**: 0.6x〜2.0xで音声速度を調整
4. **学習開始**: 「開始」ボタンで学習スタート

### 各モードの詳細

#### 🗨️ 日常英会話モード
- マイクボタンを押して話しかける
- AIが自然に応答し、文法ミスをさりげなく修正
- 実践的な会話スキルを向上

#### 🎯 シャドーイングモード
- AI生成の英文問題を聞く
- 同じように発話して発音練習
- 詳細な発音評価とフィードバック

#### ✏️ ディクテーションモード
- AI音声を聞いてテキスト入力
- 正確な聞き取り能力を養成
- 語彙力と文法理解を同時に向上

## 🛠️ 技術スタック

### フロントエンド
- **Streamlit**: 直感的なWebアプリインターフェース
- **streamlit-webrtc**: リアルタイム音声処理

### AI・機械学習
- **OpenAI GPT-4o-mini**: 自然言語理解・生成
- **Whisper API**: 高精度音声認識
- **TTS-1 Model**: 自然な音声合成

### 音声処理
- **FFmpeg**: 音声ファイル変換・処理
- **PyAudio**: リアルタイム音声入出力
- **noise reduction**: 高品質な音声前処理

### データ管理
- **LangChain**: 会話履歴管理・プロンプト最適化
- **Session State**: ユーザーセッション管理

## 📊 評価システム

### 多次元評価アルゴリズム
```
📈 総合スコア = 発音 + 語彙 + 文法 + 流暢性（40点満点）

🎯 各評価項目:
├── 発音・音韻 (10点) - 音素・ストレス・イントネーション
├── 語彙・単語 (10点) - 正確性・適切性・語彙レベル
├── 文法構造 (10点) - 構文・語順・時制・冠詞
└── 流暢性 (10点) - 自然さ・リズム・聞き取りやすさ
```

## 🎨 プロジェクト構造

```
my-study-log/
├── main.py              # メインアプリケーション
├── functions.py         # 音声処理・AI機能
├── constants.py         # 設定・プロンプトテンプレート
├── requirements.txt     # 依存パッケージ
├── .env                # 環境変数（要作成）
├── audio/              # 音声ファイル保存
│   ├── input/         # 録音音声
│   └── output/        # 生成音声
└── images/            # UIアイコン
    ├── ai_icon.jpg
    └── user_icon.jpg
```

## 🌟 今後の機能拡張予定

- [ ] 📈 学習進捗の可視化・分析
- [ ] 👥 マルチユーザー対応
- [ ] 🎮 ゲーミフィケーション要素
- [ ] 📚 カスタム学習コンテンツ作成
- [ ] 🌐 多言語対応（中国語・韓国語等）
- [ ] 📱 モバイルアプリ版開発

## 🤝 コントリビューション

プルリクエストやIssueを歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このリポジトリにはライセンスファイルが含まれていません。利用・再配布にあたっては、権利者に確認してください。

## 🙏 謝辞

- [OpenAI](https://openai.com/) - GPT-4とWhisper APIの提供
- [Streamlit](https://streamlit.io/) - 素晴らしいWebアプリフレームワーク
- [LangChain](https://langchain.com/) - AI開発効率化ツール

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/TONOTE1988">TONOTE1988</a>
</p>

<p align="center">
  ⭐ このプロジェクトが気に入ったらスターをお願いします！
</p>
