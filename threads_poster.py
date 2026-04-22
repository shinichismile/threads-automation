"""
threads_poster.py
=================
Threads API に投稿するモジュール。
GitHub Actions から呼び出されます。
"""

import requests
import os
import time


THREADS_USER_ID = os.environ.get("THREADS_USER_ID", "268181249578044164")
THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
API_BASE = "https://graph.threads.net/v1.0"


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
        print(f"✅ コンテナ作成成功 → creation_id: {data['id']}")
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


def post_to_threads(text: str) -> bool:
    """テキストをThreadsに投稿するメイン関数"""
    if not THREADS_ACCESS_TOKEN:
        print("❌ THREADS_ACCESS_TOKEN が設定されていません")
        return False

    print(f"📝 投稿開始: {text[:30]}...")

    creation_id = create_container(text)
    if not creation_id:
        return False

    print("⏳ 30秒待機中（API推奨）...")
    time.sleep(30)

    return publish_container(creation_id)
