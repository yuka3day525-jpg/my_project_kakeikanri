# ai apiの組み込み方
# python -m pip install -U google-genai
# APIキーはコードに直書きせず、PowerShellなら例えば、
# $env:GEMINI_API_KEY="取得したキーの番号入れる"としておく。Google公式も環境変数での設定を案内してる。
# そのあとexpense/ai.pyを作る

from google import genai
client = genai.Client()

def gemini_predict_category(store_names):

    joined_names = "\n".join(
        f"{i}:{name}" for i,name in enumerate(store_names)
    )

    prompt = f"""
次の利用店名を、以下のカテゴリーから必ず1つだけ選んでください。

食費(外食)
食費(自炊) 
日用品
衣類
娯楽・趣味
家具家電・設備
サロン代
医療費
NISA
旅行・レジャー
その他
未分類
       
利用店名:
{joined_names}

入力されたすべての利用店名について、
入力と同じ順番・同じ番号で回答してください。

カテゴリー名は上記のカテゴリー名をそのまま使用してください。
説明や理由は書かないでください。

回答形式:
0: カテゴリー
1: カテゴリー
2: カテゴリー
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    lines = response.text.strip().splitlines()
# で、
# [
#     "0: 食費(外食)",
#     "1: 日用品",
#     "2: 旅行・レジャー",
# ]
# に分割。
    categories = []

    for line in lines:
        if ":" not in line:
            continue

        category = line.split(":", 1)[1].strip()
        categories.append(category)
# line = "0: 食費"だったとする。まず、line.split(":", 1)で、["0", " 食費"]になる。
# ここで 1 は、: で分割するのは最初の1回だけって意味。
# 次の、[1]で2個目を取るから、" 食費"になる。最後に、.strip()で前後の空白を消して、"食費"になる。   

    return categories


def bank_gemini_predict_category(store_names):

    joined_names = "\n".join(
        f"{i}:{name}" for i,name in enumerate(store_names)
    )
    prompt = f"""
次の利用店名を、以下のカテゴリーから必ず1つだけ選んでください。

給料
入金
送金
現金引き出し
国保・住民税・年金類
娯楽・趣味
食費
NISA
家賃
カード引き落とし
サービス(還元など)
家具家電・設備
保険（家や生命など）
日用品
その他
未分類
       
利用店名:
{joined_names}

入力されたすべての利用店名について、
入力と同じ順番・同じ番号で回答してください。

カテゴリー名は上記のカテゴリー名をそのまま使用してください。
説明や理由は書かないでください。

回答形式:
0: カテゴリー
1: カテゴリー
2: カテゴリー
"""

    response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
    lines = response.text.strip().splitlines()
    # で、
    # [
    #     "0: 食費(外食)",
    #     "1: 日用品",
    #     "2: 旅行・レジャー",
    # ]
    # に分割。
    categories = []
    
    for line in lines:
        if ":" not in line:
            continue

        category = line.split(":", 1)[1].strip()
        categories.append(category)
# line = "0: 食費"だったとする。まず、line.split(":", 1)で、["0", " 食費"]になる。
# ここで 1 は、: で分割するのは最初の1回だけって意味。
# 次の、[1]で2個目を取るから、" 食費"になる。最後に、.strip()で前後の空白を消して、"食費"になる。   

    return categories

# https://aistudio.google.com/usage?timeRange=last-28-days API使用履歴など