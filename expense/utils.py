##すでにimport_csv.pyの中に同じ処理がある。CSV取込の中だけで使うなら、わざわざutils.pyを作らなくても動く。
# ただ今回の目標は、CSV取込時にも店名をそろえる,カテゴリー編集時にルール保存するときも店名をそろえるの両方で同じ処理を使うこと。
# 今のままだと、店名をそろえる処理はCommandクラス内にあるから、views.pyからは使いにくい。はCommandクラスのメソッドなので、管理コマンド専用に近い形になってる。
# そのため、共通処理だけをutils.pyへ出す。
# 今
# import_csv.pyの中だけに表記統一処理がある

# 変更後
# utils.pyに共通処理を置く
# ↓
# import_csv.pyからも使う
# views.pyからも使う

import unicodedata
from .models import  ExpenseCategoryRule,BankCategoryRule

                         #↓これ変数
def normalize_store_name(store_name):
    normalized_name = unicodedata.normalize("NFKC",store_name,)#upper()は英字用、normalize("NFKC", ...)は半角・全角の表記ゆれをそろえる用、という違い。

    return normalized_name.strip().upper()

def classify_category(store_name,household):
        normalized_name = normalize_store_name(store_name)

        # 保存した分類ルールを取得
        rules = ExpenseCategoryRule.objects.filter(household=household)

        # 長いキーワードから先に判定する
        rules = sorted(
            rules,
            key=lambda rule: len(rule.keyword),#何を基準に並べる？という指定　なので、キーワードの文字数で並べる。
            reverse=True,#これが大事なのは、AMAZON.CO.JPという店名には、AMAZONも含まれてるから。もし短いAMAZONを先に判定すると、if "AMAZON" in "AMAZON.CO.JP":
     #が先にTrueになって、AMAZON.CO.JP → 娯楽の細かいルールまで到達しない。だから、より具体的な長いルールを先に見る。
        )
        for rule in rules:
            normalized_keyword = normalize_store_name(rule.keyword)#保存されているルール側の店名も、表記をそろえる。たとえば、ａｍａｚｏｎ．ｃｏ．ｊｐなら、AMAZON.CO.JPみたいに統一する。

            if normalized_keyword in normalized_name:#ルールのキーワードが、実際の店名の中に含まれているか？
                return rule.category,"memory" #一致したら、そのルールのカテゴリーを返す。

        if "ローソン" in normalized_name or "セブン" in normalized_name or "マミー" in normalized_name or "マツヤ" in normalized_name:
            return "食費(外食)","rule"

        if "AMAZON" in normalized_name:
            return "日用品","rule"

        if "APPLE.COM" in normalized_name:
            return "サブスク","rule"


        if "コミック" in normalized_name:
            return "娯楽・趣味","rule"

        if "グレイル" in normalized_name or "QOO10" in normalized_name:
            return "衣類","rule"

        if "楽天証券" in normalized_name:
            return "NISA","rule"

        # ③ 機械学習
        from .ml import expense_predict_category

        predicted_category, confidence = expense_predict_category(
            store_name,
            household,
        )

        # 機械学習がある程度自信あり
        if confidence >= 0.6:
            return predicted_category,"ml"

        return "未分類",""


        # # ④ 機械学習が自信なし → Gemini
        # from .ai import gemini_predict_category

        # ai_category = gemini_predict_category(
        #     store_name
        # )

        # return ai_category

def classify_bank_category(store_name,household):
    normalized_name = normalize_store_name(store_name)

    rules = BankCategoryRule.objects.all()

    rules = sorted(
        rules,
        key=lambda rule: len(rule.keyword),
        reverse=True,
    )

    for rule in rules:
        normalized_keyword = normalize_store_name(rule.keyword)

        if normalized_keyword in normalized_name:
            return rule.category,"memory"

    # 銀行用の固定ルール
    if "トウプレ" in normalized_name:
        return "給料","rule"

    if "ラクテンカード" in normalized_name:
        return "カード引き落とし","rule"

    if "ダイイチセイメイ" in normalized_name:
        return "保険","rule"

    # ③ 機械学習
    from .ml import bank_predict_category

    predicted_category, confidence = bank_predict_category(
        store_name,
        household,
    )
    
    # 機械学習がある程度自信あり
    if confidence >= 0.6:
        return predicted_category,"ml"

    return "未分類",""
    
    
    # # ④ 機械学習が自信なし → Gemini
    # from .ai import bank_gemini_predict_category

    # ai_category = bank_gemini_predict_category(
    #     store_name
    # )

    # return ai_category

