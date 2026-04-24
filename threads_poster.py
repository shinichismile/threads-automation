"""
threads_poster.py
=================
Threads API に投稿するモジュール。
GitHub Actions から呼び出されます。

更新履歴：
  2026-04-24: 重複投稿防止機能を追加
"""

import requests
import os
import time


THREADS_USER_ID = os.environ.get("THREADS_USER_ID", "268181249578044164")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
API_BASE = "https://graph.threads.net/v1.0"


def get_recent_post_texts(limit: int = 5) -> list:
    """
    最近の投稿テキストを取得する（重複チェック用）
    """
    try:
        url = f"{API_BASE}/me/threads"
        params = {
            "fields": "text",
            "limit": limit,
            "access_token": THREADS_ACCESS_TOKEN,
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "data" in data:
            return [item.get("text", "") for item in data["data"]]
    except Exception as e:
        print(f"⚠️ 最近の投稿取得エラー（重複チェックをスキップ）: {e}")
    return []


def is_duplicate_post(text: str) -> bool:
    """
    生成したテキストが最近の投稿と重複していないかチェックする。
    完全一致または80%以上の類似度がある場合は重複とみなす。
    """
    recent_posts = get_recent_post_texts()
    if not recent_posts:
        return False

    text_clean = text.strip()
    for existing in recent_posts:
        existing_clean = existing.strip()
        # 完全一致チェック
        if existing_clean == text_clean:
            print(f"⚠️ 重複検出：直近の投稿と完全一致しています")
            return True
        # 高類似度チェック（文字ベース）
        if existing_clean and text_clean:
            min_len = min(len(existing_clean), len(text_clean))
            max_len = max(len(existing_clean), len(text_clean))
            if min_len > 20 and max_len > 0:
                match_chars = sum(
                    c1 == c2
                    for c1, c2 in zip(existing_clean[:min_len], text_clean[:min_len])
                )
                similarity = match_chars / max_len
                if similarity > 0.80:
                    print(f"⚠️ 重複検出：類似度 {similarity:.0%} の投稿が存在します")
                    return True
    return False


def create_container(text: str) -> str | None:
    """Step 1: テキストコンテナを作成する"""
    url = f"{API_BASE}/me/threads"
    params = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    response = requests.post(url, params=params)
    data = response.json()

    if "id" in data:
        print(f"✅ コンテナ作成成功 -> creation_id: {data['id']}")
        return data["id"]
    else:
        print(f"❌ コンテナ作成失敗: {data}")
        return None


def publish_container(creation_id: str) -> bool:
    """Step 2: コンテナを公開する"""
    url = f"{API_BASE}/me/threads_publish"
    params = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    response = requests.post(url, params=params)
    data = response.json()

    if "id" in data:
        print(f"🎉 投稿完了！ post_id: {data['id']}")
        return True
    else:
        print(f"❌ 投稿失敗: {data}")
        return False


def post_to_threads(text: str, skip_duplicate_check: bool = False) -> bool:
    """
    テキストをThreadsに投稿するメイン関数。
    重複チェックを行い、重複している場合は投稿をスキップする。
    """
    if not THREADS_ACCESS_TOKEN:
        print("❌ THREADS_ACCESS_TOKEN が設定されていません")
        return False

    print(f"📝 投稿開始: {text[:40]}...")

    # 重複チェック
    if not skip_duplicate_check:
        print("🔍 重複チェック中...")
        if is_duplicate_post(text):
            print("⏭️ 重複のため投稿をスキップします（再生成が必要）")
            return "DUPLICATE"  # 特殊な戻り値で重複を通知

    print("✅ 重複なし。投稿を実行します。")
    creation_id = create_container(text)
    if not creation_id:
        return False

    print("⏳ 30秒待機中（API推奨）...")
    time.sleep(30)

    return publish_container(creation_id)
