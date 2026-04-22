"""
content_generator.py
====================
Claude AI を使ってThreads投稿文を自動生成するモジュール。

macchi_macchi のアカウントに合わせた投稿を生成します。
※嘘や本人が経験していないことは絶対に書かない。
※事実ベースのAI情報・フリーランス情報・副業情報のみ。
"""

import anthropic
import os
import random
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

PERSONA = """あなたはThreads運用のプロフェッショナルです。

今回は「macchi_macchi」のアカウントで投稿を書きます。

【アカウント情報】
- 静岡市在住40代、フリーランス歴5年
- 得意分野：AIを使ったライティング、事業サポート、事業伴走、LINE構築
- セミナー登壇・各種SNS運用中
- 生成AIパスポート保持者
- コンセプト：「AIで出来ないことを出来るに変換」
- ターゲット：20〜40代の副業志望者・起業家・AIを学びたいビジネスパーソン

【絶対ルール】
- 嘘を書かない。個人的な体験談は書かない
- 失敗談・収入・単価の話は書かない
- 事実ベースのAI情報・フリーランス一般論・副業事例のみ

【禁止表現】
- 「〜することが重要です」「〜と言えるでしょう」「〜ではないでしょうか」
- ハッシュタグ（絶対に使わない）
- マークダウン記法（**太字**、##見出し など）

【投稿の鉄則】
- 1行目で読者を引き付けるフックを入れる
- 改行を多めに。読みやすくする
- 具体的な数字・ツール名・事例を入れる
- 300文字以内、ですます調"""

POST_TYPES = {
    "freelance_howto": {
        "description": "8時 — 社会人×フリーランス両立術",
        "instruction": "会社員しながらフリーランスを目指す人への具体的なアドバイス。今日からできる一歩を提案する。",
        "topics": [
            "会社員しながらフリーランスを始める最初の一歩",
            "副業で最初の1件を取る現実的な方法",
            "本業を辞めないまま副収入を作る3つの方法",
            "フリーランスに必要なスキルの選び方",
            "副業解禁の今、何から始めるべきか",
            "スキルゼロからフリーランスになる学習順序",
        ],
    },
    "freelance_ai": {
        "description": "12時 — フリーランス×AI活用術",
        "instruction": "フリーランスがAIを使って業務効率を上げる具体的な方法。ツール名と手順を含める。",
        "topics": [
            "フリーランスがAIで仕事を3倍速にする方法",
            "クライアントへの提案書をAIで10分で作る手順",
            "フリーランスが絶対使うべきAIツール5選",
            "AIで営業メールの返信率を上げる方法",
            "フリーランスのポートフォリオをAIで作る方法",
        ],
    },
    "job_type_idea": {
        "description": "16時 — 職種別副業・起業提案",
        "instruction": "特定の職種の人が今の経験を活かせる副業・起業アイデアを提案。毎回違う職種で書く。AIとの組み合わせも提示。",
        "topics": [
            "看護師が副業で活かせる意外なスキル",
            "営業職がフリーランスになる最短ルート",
            "教師・塾講師がオンライン教育で起業する方法",
            "美容師がSNSとAIを使って集客する具体策",
            "エンジニアが副業で月10万稼ぐ方法",
            "介護士が経験を活かしてサービスを作る方法",
            "経理・会計の人がAI時代に生き残る副業",
        ],
    },
    "ai_beginner": {
        "description": "18時 — 初心者向けAI使い方・プロンプト例",
        "instruction": "AIを使ったことがない人でも今日から使える方法。コピペして使えるプロンプト例を必ず含める。",
        "topics": [
            "ChatGPTで回答の質が劇的に変わる一言",
            "Claudeで議事録を3分で作るプロンプト公開",
            "AIに文章を書かせるときの黄金パターン",
            "Perplexityで調査時間を半分にする使い方",
            "Geminiで英語メールを瞬時に翻訳する手順",
        ],
    },
    "ai_case_study": {
        "description": "20時 — AI活用事例（日本・海外）",
        "instruction": "日本・海外の具体的なAI活用成功事例を紹介。数字・金額・時間削減などの具体的な成果を含める。不確かな情報は「〜と報告されています」と表現。",
        "topics": [
            "海外フリーランサーがAIで収入を倍にした実例",
            "日本の中小企業がAIで業務時間を40%削減した事例",
            "個人事業主がAIで問い合わせ対応を自動化した話",
            "地方の飲食店がAIで客単価を上げた事例",
            "フリーランスのライターがAIで案件数を2倍にした実例",
        ],
    },
    "business_strategy": {
        "description": "22時 — 個人事業主の集客・事業戦略",
        "instruction": "個人事業主が今すぐ使える集客・マーケティング戦略。お金をかけずにできる方法を優先。明日から試せるレベルの具体性。",
        "topics": [
            "AIでチラシを作って半径3キロにポスティングする集客術",
            "Googleマイビジネスで地域No.1になる方法",
            "SNSと実店舗を連動させた集客の手順",
            "フリーランスがリピート客を増やす仕組みの作り方",
            "0円でできる個人事業主の最強集客3選",
            "LINE公式アカウントで顧客管理を自動化する手順",
        ],
    },
}


def get_post_type(hour: int) -> str:
    if hour <= 9:
        return "freelance_howto"
    elif 10 <= hour <= 13:
        return "freelance_ai"
    elif 14 <= hour <= 17:
        return "job_type_idea"
    elif hour == 18:
        return "ai_beginner"
    elif hour == 20:
        return "ai_case_study"
    else:
        return "business_strategy"


def generate_post_with_claude(hour: int) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    post_type = get_post_type(hour)
    post_info = POST_TYPES[post_type]
    topic = random.choice(post_info["topics"])
    today = datetime.now(JST).strftime("%Y年%m月%d日(%a)")

    prompt = f"""{PERSONA}

今日は{today}です。

テーマ：{topic}
時間帯：{post_info["description"]}
{post_info["instruction"]}

【投稿ルール】
- 300文字以内、ですます調
- ハッシュタグは使わない
- AIっぽい表現は使わない
- マークダウン記法は使わない
- 最後は読者への問いかけか行動を促す一文

投稿本文のみを出力してください。"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def proofread_with_claude(text: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""以下のThreads投稿文を校閲してください。

【チェック・修正項目】
1. AIっぽい表現を自然な日本語に書き換える（「重要です」「言えるでしょう」など）
2. 同じ文末が3回続いていたら変える
3. ハッシュタグがあれば削除
4. マークダウン記法があれば削除
5. 300文字を超えていたら自然に削る

【投稿文】
{text}

修正後の投稿文のみを出力してください。"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_post_fallback(hour: int) -> str:
    post_type = get_post_type(hour)
    fallbacks = {
        "freelance_howto": "フリーランスで最初につまずくのは「最初の1件」です。\n\nでも最初のクライアントは遠くにいません。\n\n今の職場の同僚、地域のお店、昔の友人。\nあなたのスキルを必要としている人は、意外と身近にいます。\n\nまず1件。それだけ意識してみてください。",
        "freelance_ai": "AIを使うと提案書が10分で作れます。\n\nポイントは「クライアントの課題を箇条書きにしてClaudeに渡す」こと。\n\n構成を考える時間が大幅に減って、クオリティに集中できます。\n\n試してみましたか？",
        "job_type_idea": "今の仕事のスキル、副業に使えていますか？\n\n「自分には特別なスキルがない」と思っている人ほど、実は宝の山を持っています。\n\n毎日やっていることが、誰かにとっての価値になります。",
        "ai_beginner": "AIに指示するとき「〇〇して」より「〇〇の専門家として〇〇して」と伝えると、回答の質が全然変わります。\n\n今日から試せる一番シンプルなテクニックです。",
        "ai_case_study": "海外では個人事業主がAIチャットボットを導入して、問い合わせ対応を完全自動化したという事例が増えています。\n\n1人でも大企業並みの対応ができる時代になりました。",
        "business_strategy": "個人事業主の集客で見落としがちなのが「半径3キロ」です。\n\nAIでチラシを作って近隣にポスティングするだけで、ネット集客とは違う層に届きます。\n\nデジタルとアナログの組み合わせ、試してみる価値ありますよ。",
    }
    return fallbacks.get(post_type, fallbacks["freelance_howto"])


def generate_post(hour: int) -> str:
    try:
        print(f"Claude AIで{hour}時の投稿を生成中...")
        text = generate_post_with_claude(hour)
        print(f"生成成功！{len(text)}文字")
        print("校閲中（見崎 精一）...")
        text = proofread_with_claude(text)
        print(f"校閲完了！{len(text)}文字")
        return text
    except Exception as e:
        print(f"Claude APIエラー: {e}")
        print("バックアップ投稿を使用します...")
        return generate_post_fallback(hour)
