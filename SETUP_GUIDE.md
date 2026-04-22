# threads-automation セットアップガイド

GitHub Actionsを使って、PCが起動していなくてもThreadsに自動投稿するシステムです。

---

## 📁 ファイル構成

```
threads-automation/
├── .github/
│   └── workflows/
│       └── threads_workflow.yml   ← GitHub Actionsの設定
├── main.py                        ← エントリーポイント
├── content_generator.py           ← 投稿文の生成（Claude AI使用）
├── threads_poster.py              ← Threads APIへの投稿
├── requirements.txt               ← 必要なPythonパッケージ
├── .env.example                   ← 環境変数のサンプル
├── .gitignore                     ← GitHubにアップしないファイルの設定
└── SETUP_GUIDE.md                 ← このファイル
```

---

## ⏰ 投稿スケジュール

| 時間（JST） | テーマ |
|------------|--------|
| 8:00 | 社会人×フリーランス両立術 |
| 12:00 | フリーランス×AI活用術 |
| 16:00 | 職種別副業・起業提案 |
| 18:00 | 初心者向けAI使い方 |
| 20:00 | AI活用事例 |
| 22:00 | 個人事業主の集客・事業戦略 |

---

## 🚀 セットアップ手順

### Step 1: GitHubにリポジトリを作成

1. https://github.com を開く
2. 右上の「＋」→「New repository」
3. Repository name: `threads-automation`
4. Private（非公開）を選択
5. 「Create repository」をクリック

### Step 2: このフォルダをGitHubにアップロード

GitHubのページに表示される手順に従って実行（コマンドライン）：

```bash
cd threads-automation
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/threads-automation.git
git push -u origin main
```

### Step 3: GitHub Secretsを設定

GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」→「New repository secret」で以下を追加：

| Secret名 | 値 |
|----------|-----|
| `THREADS_ACCESS_TOKEN` | Threads APIの長期アクセストークン |
| `THREADS_USER_ID` | `268181249578044164` |
| `ANTHROPIC_API_KEY` | Anthropic APIキー（console.anthropic.com で取得） |

### Step 4: ANTHROPIC_API_KEYの取得

1. https://console.anthropic.com にアクセス
2. 「API Keys」→「Create Key」
3. キーをコピーしてGitHub Secretsに貼り付け

---

## ✅ 動作確認

GitHubリポジトリの「Actions」タブ→「Threads Auto Post」→「Run workflow」で手動実行できます。

`hour` に `8` や `12` などを入力すると、その時間帯の投稿を生成してテストできます。

---

## 🔑 アクセストークンの更新

Threadsのアクセストークンは60日で期限切れになります。
期限が近づいたら新しいトークンを取得して、GitHub Secretsの `THREADS_ACCESS_TOKEN` を更新してください。

（将来的には自動更新の仕組みも追加予定）
