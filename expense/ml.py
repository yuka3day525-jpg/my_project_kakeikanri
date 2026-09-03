from sklearn.feature_extraction.text import TfidfVectorizer
# これは、文字列を機械学習が扱える数字のデータに変換する道具。機械学習モデルは、"ローソン"
# みたいな文字をそのまま理解できない。だから、
# ローソン
# ↓
# 文字の特徴を数値化
# ↓
# [0.0, 0.42, 0.81, ...]
# みたいに変換する必要がある。

from sklearn.linear_model import LogisticRegression
# LogisticRegressionは、今回のカテゴリーを予測する機械学習モデル。

from .models import ExpenseCategoryRule,BankCategoryRule
from .utils import normalize_store_name


def expense_train_category_model(household):#カテゴリー分類の機械学習モデルを学習させる関数

    rules = ExpenseCategoryRule.objects.filter(
        household=household
    )

    store_names = []#店名を入れていく。
    categories = []#正解カテゴリーを入れる。

    for rule in rules:
        store_names.append(
            normalize_store_name(rule.keyword)
        )

        categories.append(
            rule.category
        )

    if len(store_names) < 2:
        return None, None #データが少なすぎる場合、機械学習モデルを作らず終了する。

    if len(set(categories)) < 2:
        return None, None #2件以上あってもカテゴリーが全部「食費」だけだと、LogisticRegressionは学習できない。

    vectorizer = TfidfVectorizer( #vectorizerは、店名を数値化する担当
        analyzer="char",
#analyzerは、文字列を何単位で分析する？という指定。"char"なので、文字単位で分析する。例えば、ローソン高坂店
# なら、「単語」ではなく文字の並びを見る。店名は普通の文章じゃないから、文字単位の方が相性がいい。例えば、
# ローソン高坂店
# ローソン川越店
# ローソン東松山店
# なら全部に、
# ローソン
# という文字の並びが含まれてる。機械学習が、「ローソン」という並びがある店は食費になりやすいぞ
# と学習しやすくなる。
        ngram_range=(2, 4),
# 文字を何文字ずつのまとまりで見るか指定してる。(2, 4)なので、2文字、3文字、4文字のまとまりを見る
# という意味。例えば、ローソンなら一部として、
# 2文字
# ロー
# ーソ
# ソン

# 3文字
# ローソ
# ーソン

# 4文字
# ローソン
# みたいな特徴を作る。だから、
# ローソン高坂店
# ローソン川越店
# は、
# ロー
# ーソ
# ソン
# ローソ
# ーソン
# ローソンなどを共通して持つ。これによって「似た店名」を見つけやすくなる。
    )

    X = vectorizer.fit_transform(
        store_names
    )
# まず、store_namesには、
# [
#     "ローソン",
#     "AMAZON.CO.JP",
#     "コミックシーモア",
# ] みたいな店名が入ってる。それを、vectorizer.fit_transform()に渡している。
# fit_transformは実は、fit + transformの2つを一気にやってる。
# fitは、この店名たちにはどんな文字の特徴があるか覚える。
# transformは、覚えたルールを使って店名を数値に変換する。つまり、
# "ローソン"
# "AMAZON.CO.JP"
# "コミックシーモア"
# ↓
# TfidfVectorizer
# ↓
# 機械学習が扱える数字にする。その数値データを、Xに入れる。機械学習では入力データをXと呼ぶことが非常に多い。
    

    model = LogisticRegression(
        max_iter=1000 #学習処理を最大1000回まで繰り返していいよという設定。
    )
#ここで分類する機械学習モデルを作る。modelという変数に、LogisticRegressionのモデルを入れる。まだこの時点では学習前。

    model.fit(
        X,
        categories
    )
# ここが本当に機械学習してる行。fit()は、このデータを使って学習してくださいというメソッド。
# 渡してるのが、Xと、categories。Xは店名を数値化したもの。categoriesは正解。
# 例えば概念的には、
# ローソンを数値化したもの
# → 正解：食費
# Amazonを数値化したもの
# → 正解：日用品
# コミックシーモアを数値化したもの
# → 正解：娯楽を渡してる。
# モデルはここから、こういう文字特徴なら食費になりやすい,こういう文字特徴なら娯楽になりやすいという関係を学ぶ。
# つまり、
# model.fit(X, categories)が今回の**「学習」そのもの**。
    return vectorizer, model
#学習が終わったので2つ返す。なぜモデルだけじゃなく、vectorizerも返すのかが大事。
# 新しい店名、ローソン東松山駅前店を予測するときも、学習時と同じ方法で数値化しないといけないから。
# つまり、
# vectorizer
# → 文字を数字に変える担当

# model
# → 数字を見てカテゴリーを判断する担当
# この2人セットが必要。

# 全体をものすごく簡単にすると、

# CategoryRuleから
# 店名と正解カテゴリーを取る
#         ↓
# store_names
# categories
#         ↓
# TfidfVectorizer
# 店名を数字にする
#         ↓
# X
#         ↓
# LogisticRegression
# Xと正解カテゴリーを使って学習
#         ↓
# 学習済みmodel完成
# という処理。
# 特に今の段階では、**TfidfVectorizerは「文字→数字」、LogisticRegressionは「数字→カテゴリー予測」**の2役だと押さえると分かりやすい。

def bank_train_category_model(household):#カテゴリー分類の機械学習モデルを学習させる関数

    rules = BankCategoryRule.objects.filter(
        household=household
    )

    store_names = []
    categories = []

    for rule in rules:
        store_names.append(
            normalize_store_name(rule.keyword)
        )

        categories.append(
            rule.category
        )

    if len(store_names) < 2:
        return None, None 
    if len(set(categories)) < 2:
        return None, None 
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
    )

    X = vectorizer.fit_transform(
        store_names
    )

    model = LogisticRegression(
        max_iter=1000 
    )

    model.fit(
        X,
        categories
    )
    return vectorizer, model

def expense_predict_category(store_name, household):#これは**「新しい店名を、さっき学習したモデルで予測する関数」**

    vectorizer, model = expense_train_category_model(
        household
    )
#さっき作った、train_category_model()を呼び出してる。
# vectorizer
# → 店名を数値化する担当
# model
# → 数値化された店名からカテゴリーを予測する担当

    if vectorizer is None:
        return "未分類",0
    #学習できなかった時

    normalized_name = normalize_store_name(
        store_name
    )

    X = vectorizer.transform(
        [normalized_name]
    )
#ここで新しい店名を、機械学習モデルが読める数字のデータに変換してる。前の学習時は、
# vectorizer.fit_transform(store_names)だった。
# 今回は、vectorizer.transform(...)だけ。なぜfitしないかというと、もう学習時に、
# ロー
# ーソ
# ソン
# AM
# MA
# ...
# みたいな「どう文字を数値化するか」をvectorizerが覚えてるから。今回はその覚えたルールを使って変換するだけ。

# 学習時
# fit_transform()
# → 特徴を覚える ＋ 数値化

# 予測時
# transform()
# → 覚えた特徴を使って数値化するだけ

    category = model.predict(X)[0]
# ここで実際にカテゴリーを予測する。model.predict(X)は、この数値データXは、どのカテゴリーだと思う？
# とモデルに聞いてる。例えば結果が、["食費"]だったとする。
# predict()は複数件を予測できるので、結果もリストっぽい形で返ってくる。
# 今回は1件だけだから、[0]で最初の結果を取り出す。結果、category = "食費"になる。

    probabilities = model.predict_proba(X)[0]
# 今度は、各カテゴリーっぽさをどれくらい感じてる？を取得してる。
# predict_proba()のprobaはprobability、つまり確率。例えば、
# model.predict_proba(X)が、
# [
#     [0.75, 0.10, 0.10, 0.05]
# ]
# みたいになったとする。これは概念的には、
# 食費     0.75
# 日用品   0.10
# 娯楽     0.10
# 衣類     0.05
# みたいな意味。

# 今回も1件だけ予測してるので、[0]を付けて、probabilitiesを、[0.75, 0.10, 0.10, 0.05]にしてる。

    confidence = probabilities.max()# さっきの確率の中で、一番大きい値を取得してる。いらないかも

    return str(category),float(confidence)

def bank_predict_category(store_name, household):

    vectorizer, model = bank_train_category_model(
        household
    )

    if vectorizer is None:
        return "未分類",0

    normalized_name = normalize_store_name(
        store_name
    )

    X = vectorizer.transform(
        [normalized_name]
    )

    category = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = probabilities.max()# さっきの確率の中で、一番大きい値を取得してる。いらないかも
    
        
    return str(category),float(confidence)