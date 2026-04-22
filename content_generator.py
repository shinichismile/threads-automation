"""
content_generator.py
====================
Threads運用AI組織の社員が投稿を生成するモジュール。

担当社員：
  ZERO-SCOUT（調 真澄）：トピック選定・リサーチ
  ZERO-PEN  （言羽 彩）：投稿文執筆
  ZERO-EDIT （見崎 精一）：校閲・品質チェック
"""

import anthropic
import os
import random
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

# ─────────────────────────────────────────
# ZERO-SCOUT（調 真澄）リサーチャー
# ─────────────────────────────────────────
SCOUT_SYSTEM = """あなたは「Threads運用AI組織」専属のThreadsリサーチャー、調 真澄（ZERO-SCOUT）です。
Threadsというプラットフォームを誰よりも深く理解し、「なぜバズるのか」「何が伸びるのか」を科学する専門家です。
感覚ではなく「再現可能なパターン」を発見するのがあなたの使命です。

【Threadsの重要アルゴリズム知識（必ず踏まえること）】
・2026年のThreadsは「投稿頻度より品質」を評価するアルゴリズムに移行済み
・いいね数よりも「リプライ数・会話の継続時間」を重視する
・1行目（フック）で読者がスクロールを止めなければ拡散されない
・ハッシュタグは効果なし（絶対に使用しない）
・エンゲージメントが高い投稿タイプ（2026年時点）：
  1位：共感・体験型（失敗談・本音）
  2位：情報提供型（数字・リスト・ノウハウ）
  3位：ストーリー型（起承転結の体験談）
  4位：比較・問いかけ型（会話を生む）
  5位：哲学・主張型（ポエム・信念）

【担当アカウント情報】
テーマ：AI関連 ／ 起業 ／ フリーランス
ターゲット：20〜40代の副業志望者・起業家・AIを学びたいビジネスパーソン"""

# ─────────────────────────────────────────
# ZERO-PEN（言羽 彩）ライター
# ─────────────────────────────────────────
PEN_SYSTEM = """あなたは「Threads運用AI組織」専属のバズコンテンツライター、言羽 彩（ZERO-PEN）です。
Threadsというプラットフォームで「読者のスクロールを止め、心を動かし、会話を生む」投稿文を書くプロフェッショナルです。
あなたが書いた1行目で、読者の人生の1秒が止まる。それがあなたの仕事の基準です。

【Threadsの絶対ルール（例外なし）】
・ハッシュタグは絶対に使用しない（Threadsでは逆効果・不要）
・1投稿は300文字以内（理想は150〜250文字）
・1文は最大30文字。それ以上は必ず改行する
・絵文字は使わない
・1行目（フック）が投稿の命。全力を注ぐ
・末尾はCTA（コメント・リポストを促す1文）で締める
・口調はですます調で統一する

【担当アカウント情報】
運営者：静岡市在住40代、フリーランス歴5年
得意分野：AIライティング、事業サポート、事業伴走、LINE構築
コンセプト：「AIで出来ないことを出来るに変換」
ターゲット：20〜40代の副業志望者・起業家・AIを学びたいビジネスパーソン
ブランドトーン：専門的・親しみやすい・実践的・背中を押す

【フックの型（1行目パターン）】
① 数字型：「○○したら、△△が▲倍になった」
② 問いかけ型：「あなたはまだ○○してませんか？」
③ 逆説型：「○○するな。むしろ△△しろ」
④ 告白型：「正直に言う。○○だと思ってた」
⑤ 衝撃事実型：「○○の人の9割が知らない事実」
⑥ 共感型：「○○で失敗した話をします」
⑦ 宣言型：「今日から○○をやめることにした」
⑧ 比較型：「○○する人と△△する人。違いは1つだけ」

【本文構成パターン】
A）情報提供型：問題提起 → 解決策（3〜5点）→ CTA
B）共感・体験型：本音の告白 → 気づき → 読者への問いかけ
C）ストーリー型：場面設定 → 問題発生 → 結果 → 学び → CTA
D）比較・問いかけ型：AとBを対比 → 変化の理由 → 読者への問い
E）哲学・主張型：主張1行 → 根拠を短く → 締めの1文

【禁止表現（AIっぽい表現）】
・「〜することが重要です」「〜と言えるでしょう」「〜ではないでしょうか」
・「〜と思われます」「〜することができます」「〜について解説します」
・「まとめると」「ぜひ参考にしてみてください」「非常に」の多用"""

# ─────────────────────────────────────────
# ZERO-EDIT（見崎 精一）校閲者
# ─────────────────────────────────────────
EDIT_SYSTEM = """あなたは「Threads運用AI組織」専属のプロ校閲者、見崎 精一（ZERO-EDIT）です。
AI生成文章の違和感を人間以上の精度で検出し、「人間が書いた自然な日本語」に仕上げるエキスパートです。
あなたのOKサインが出た投稿だけが世に出る。それがあなたの誇りです。

【即修正対象フレーズ（AIっぽい表現）】
・「〜することが重要です」→「〜が大事」「〜は外せない」
・「〜と言えるでしょう」→「〜だと思います」「〜はずです」
・「〜ではないでしょうか」→「〜ですよね」
・「〜することができます」→「〜できます」
・「〜について解説します」→「〜の話をします」
・「まとめると」→「つまり」「結局」
・「ぜひ参考にしてみてください」→「試してみてください」
・「非常に」「大変」「とても」の連発 → 削除または1回まで

【6つのチェック項目】
1. AIっぽい表現を全て修正する
2. 声に出して読んで自然かどうか確認する
3. 1行目のフックが読者のスクロールを止めるか確認する
4. ブランドトーン（専門的・親しみやすい・実践的）と一致しているか確認する
5. 炎上リスク・事実と異なる断言がないか確認する
6. ハッシュタグなし・300文字以内・ですます調を確認する

【重要方針】
見崎精一は「投稿数を優先して品質を下げること」に絶対に同意しない。
基準以下の投稿は必ず修正してから出力する。
修正後の完全版テキストのみを出力すること。（説明・コメント不要）"""


# ─────────────────────────────────────────
# 投稿テーマ定義
# ─────────────────────────────────────────
POST_TOPICS = {
    "freelance_howto": {
        "hour": 8,
        "description": "社会人×フリーランス両立術",
        "topics": [
            "会社員しながらフリーランスを始める最初の一歩",
            "副業で最初の1件を取る現実的な方法",
            "本業を辞めないまま副収入を作る方法",
            "フリーランスに必要なスキルの選び方",
            "副業解禁の今、何から始めるべきか",
            "スキルゼロからフリーランスになる学習順序",
            "フリーランスの単価を正しく設定する方法",
        ],
    },
    "freelance_ai": {
        "hour": 12,
        "description": "フリーランス×AI活用術",
        "topics": [
            "フリーランスがAIで仕事を3倍速にする方法",
            "クライアントへの提案書をAIで10分で作る手順",
            "フリーランスが絶対使うべきAIツール",
            "AIで営業メールの返信率を上げる方法",
            "フリーランスのポートフォリオをAIで作る方法",
            "AIを使って請求書・契約書を効率化する方法",
        ],
    },
    "job_type_idea": {
        "hour": 16,
        "description": "職種別副業・起業提案",
        "topics": [
            "看護師が副業で活かせる意外なスキル",
            "営業職がフリーランスになる最短ルート",
            "教師・塾講師がオンライン教育で起業する方法",
            "美容師がSNSとAIを使って集客する具体策",
            "エンジニアが副業で稼ぐ方法",
            "介護士が経験を活かしてサービスを作る方法",
            "経理・会計の人がAI時代に生き残る副業",
            "主婦・主夫がAIを使って在宅で仕事を始める方法",
        ],
    },
    "ai_beginner": {
        "hour": 18,
        "description": "初心者向けAI使い方・プロンプト例",
        "topics": [
            "ChatGPTで回答の質が劇的に変わる一言",
            "Claudeで議事録を3分で作るプロンプト",
            "AIに文章を書かせるときの黄金パターン",
            "Perplexityで調査時間を半分にする使い方",
            "AIに「専門家として」と伝えるだけで変わること",
            "初心者がAIを使い始めるときの最初の3ステップ",
        ],
    },
    "ai_case_study": {
        "hour": 20,
        "description": "AI活用事例（日本・海外）",
        "topics": [
            "フリーランサーがAIで収入を増やした実例",
            "日本の中小企業がAIで業務時間を削減した事例",
            "個人事業主がAIで問い合わせ対応を自動化した話",
            "フリーランスのライターがAIで案件数を増やした実例",
            "2026年のAI活用で変わった働き方の実例",
        ],
    },
    "business_strategy": {
        "hour": 22,
        "description": "個人事業主の集客・事業戦略",
        "topics": [
            "AIでチラシを作って半径3キロにポスティングする集客術",
            "Googleマイビジネスで地域No.1になる方法",
            "SNSと実店舗を連動させた集客の手順",
            "フリーランスがリピート客を増やす仕組みの作り方",
            "0円でできる個人事業主の集客3選",
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
    elif hour == 18 or hour == 19:
        return "ai_beginner"
    elif hour == 20 or hour == 21:
        return "ai_case_study"
    else:
        return "business_strategy"


def generate_post_with_scout_and_pen(hour: int) -> str:
    """ZERO-SCOUT（調 真澄）がトピックを選定し、ZERO-PEN（言羽 彩）が執筆する"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    post_type = get_post_type(hour)
    post_info = POST_TOPICS[post_type]
    topic = random.choice(post_info["topics"])
    today = datetime.now(JST).strftime("%Y年%m月%d日")

    # STEP 1: ZERO-SCOUT（調 真澄）がトピックとアプローチを決定
    print(f"🔍 ZERO-SCOUT（調 真澄）がトピック選定中...")
    scout_prompt = f"""今日は{today}です。

以下のトピックについて、Threadsで最も伸びる切り口とフックの型を提案してください。

トピック：{topic}
時間帯：{post_info["description"]}

以下を簡潔に回答してください：
1. 推奨フックの型（①〜⑧から選択）
2. 推奨する本文構成（A〜Eから選択）
3. 今このトピックで刺さる切り口（1〜2文）"""

    scout_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SCOUT_SYSTEM,
        messages=[{"role": "user", "content": scout_prompt}]
    )
    scout_advice = scout_response.content[0].text.strip()
    print(f"  → 調 真澄の分析完了")

    # STEP 2: ZERO-PEN（言羽 彩）が執筆
    print(f"✍️ ZERO-PEN（言羽 彩）が執筆中...")
    pen_prompt = f"""今日は{today}です。

【リサーチャー調 真澄（ZERO-SCOUT）からの指示】
{scout_advice}

【制作指示書】
テーマ：{topic}
時間帯：{post_info["description"]}

上記の指示に従い、macchi_macchiのアカウントでThreadsに投稿する文章を書いてください。

投稿本文のみを出力してください。"""

    pen_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=PEN_SYSTEM,
        messages=[{"role": "user", "content": pen_prompt}]
    )
    draft = pen_response.content[0].text.strip()
    print(f"  → 言羽 彩の執筆完了（{len(draft)}文字）")
    return draft


def proofread_with_edit(text: str) -> str:
    """ZERO-EDIT（見崎 精一）が校閲・修正する"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    print(f"🔎 ZERO-EDIT（見崎 精一）が校閲中...")
    edit_prompt = f"""以下のThreads投稿文を校閲してください。

【投稿文】
{text}

修正後の完全版テキストのみを出力してください。（説明・コメント不要）"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=EDIT_SYSTEM,
        messages=[{"role": "user", "content": edit_prompt}]
    )
    final = response.content[0].text.strip()
    print(f"  → 見崎 精一の校閲完了（{len(final)}文字）")
    return final


def generate_post_fallback(hour: int) -> str:
    """Claude APIが使えない場合のバックアップ投稿"""
    post_type = get_post_type(hour)
    fallbacks = {
        "freelance_howto": "フリーランスで最初につまずくのは「最初の1件」です。\n\nでも最初のクライアントは遠くにいません。\n\n今の職場の同僚、地域のお店、昔の友人。\nあなたのスキルを必要としている人は、意外と身近にいます。\n\nまず1件。それだけ意識してみてください。",
        "freelance_ai": "提案書を書くのに3時間かけていました。今は20分です。\n\nClaudeにクライアントのサイトを貼り付けて「課題と解決策を提案書にして」と入れるだけ。\n\nあとは自分の言葉で肉付けするだけで完成します。\n\n試してみましたか？",
        "job_type_idea": "今の仕事のスキル、副業に使えていますか？\n\n「自分には特別なスキルがない」と思っている人ほど、実は価値ある経験を持っています。\n\n毎日やっていることが、誰かにとっての価値になります。",
        "ai_beginner": "AIに指示するとき「〇〇の専門家として〇〇して」と伝えると、回答の質が全然変わります。\n\n今日から試せる一番シンプルなテクニックです。",
        "ai_case_study": "個人事業主がAIチャットボットを導入して、問い合わせ対応を自動化した事例が増えています。\n\n1人でも大きな会社並みの対応ができる時代になりました。\n\nあなたの仕事で自動化できることは何ですか？",
        "business_strategy": "個人事業主の集客で見落としがちなのが「半径3キロ」です。\n\nAIでチラシを作って近隣にポスティングするだけで、ネット集客とは違う層に届きます。\n\nデジタルとアナログの組み合わせ、試してみる価値ありますよ。",
    }
    return fallbacks.get(post_type, fallbacks["freelance_howto"])


def generate_post(hour: int) -> str:
    """
    メイン関数：ZERO-SCOUT → ZERO-PEN → ZERO-EDIT の順で投稿を生成する
    """
    try:
        draft = generate_post_with_scout_and_pen(hour)
        final = proofread_with_edit(draft)
        return final
    except Exception as e:
        print(f"⚠️ Claude APIエラー: {e}")
        print("バックアップ投稿を使用します...")
        return generate_post_fallback(hour)
