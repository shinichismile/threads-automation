"""
main.py
=======
GitHub Actions から呼び出されるエントリーポイント。

使い方:
  python main.py post      # 現在時刻に合った投稿を生成して投稿
  python main.py post 8    # 8時の投稿を生成して投稿（テスト用）
"""

import sys
from datetime import datetime, timezone, timedelta
from content_generator import generate_post
from threads_poster import post_to_threads

JST = timezone(timedelta(hours=9))


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

    # 投稿文を生成（リサーチ→執筆→校閲）
    print(f"\n=== {hour}時の投稿生成開始 ===")
    post_text = generate_post(hour)

    print(f"\n【生成された投稿文】")
    print("-" * 40)
    print(post_text)
    print("-" * 40)
    print(f"文字数: {len(post_text)}")

    # Threadsに投稿
    print(f"\n=== Threadsに投稿 ===")
    success = post_to_threads(post_text)

    if success:
        print("\n✅ 投稿完了！")
        sys.exit(0)
    else:
        print("\n❌ 投稿失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
