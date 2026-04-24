"""
main.py
=======
GitHub Actions から呼び出されるエントリーポイント。

使い方:
  python main.py post      # 現在時刻に合った投稿を生成して投稿
  python main.py post 8    # 8時の投稿を生成して投稿（テスト用）

更新履歴：
  2026-04-24: 重複検出時の再生成ロジックを追加
"""

import sys
from datetime import datetime, timezone, timedelta
from content_generator import generate_post
from threads_poster import post_to_threads

JST = timezone(timedelta(hours=9))
MAX_RETRY = 3  # 重複時の最大再試行回数


def main():
    now = datetime.now(JST)
    hour = now.hour

    # コマンドライン引数で時間を上書き可能（テスト用）
    if len(sys.argv) >= 3 and sys.argv[1] == "post":
        try:
            hour = int(sys.argv[2])
            print(f"テストモード: {hour}時の投稿を生成します")
        except ValueError:
            pass
    elif len(sys.argv) >= 2 and sys.argv[1] == "post":
        print(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M JST')}")
    else:
        print("使い方: python main.py post [hour]")
        sys.exit(1)

    # 投稿文を生成・投稿（重複時は別トピックで再試行）
    for attempt in range(MAX_RETRY):
        topic_offset = attempt  # 試行ごとにトピックをずらす
        if attempt > 0:
            print(f"\n🔄 再試行 {attempt}/{MAX_RETRY - 1}（別トピックで生成）")

        print(f"\n=== {hour}時の投稿生成開始 ===")
        post_text = generate_post(hour, topic_offset=topic_offset)

        print(f"\n【生成された投稿文】")
        print("-" * 40)
        print(post_text)
        print("-" * 40)
        print(f"文字数: {len(post_text)}")

        print(f"\n=== Threadsに投稿 ===")
        result = post_to_threads(post_text)

        if result == "DUPLICATE":
            print(f"⚠️ 重複のため再生成します...")
            continue
        elif result:
            print("\n✅ 投稿完了！")
            sys.exit(0)
        else:
            print("\n❌ 投稿失敗")
            sys.exit(1)

    # 最大試行回数に達した場合
    print(f"\n❌ {MAX_RETRY}回試行しましたが、全て重複または失敗でした。")
    print("投稿をスキップします。（重複投稿を防ぐための正常な動作です）")
    sys.exit(0)  # 重複スキップは正常終了とする


if __name__ == "__main__":
    main()
