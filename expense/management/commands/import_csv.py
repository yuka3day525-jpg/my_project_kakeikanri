import csv
from datetime import datetime
from django.core.management.base import BaseCommand #これがあることで、python manage.py import_csvという独自コマンドを作れる。
from expense.models import Expense,CategoryRule #expenseアプリのmodels.pyに作ったExpenseモデルを読み込んでいる。
import unicodedata
from expense.utils import normalize_store_name


class Command(BaseCommand): #djangoの独自コマンド本体を作っている。クラス名は必ず、Commandにする。BaseCommandを継承することで、Djangoのコマンドとして動く。
    help = "楽天カードのCSVを取り込みます"

    def add_arguments(self, parser):#この独自コマンドは、実行するときにどんな追加情報を受け取るの？を教える場所
        parser.add_argument("file_path")#1個目の追加情報を受け取って、それをfile_pathという名前で扱います
        parser.add_argument("billing_month")#2個目の追加情報をbilling_monthという名前で扱います

    def classify_category(self, store_name):
        normalized_name = normalize_store_name(store_name)

        # 保存した分類ルールを取得
        rules = CategoryRule.objects.all()

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
                return rule.category#一致したら、そのルールのカテゴリーを返す。

        if "ローソン" in normalized_name or "セブン" in normalized_name or "マミー" in normalized_name or "マツヤ" in normalized_name:
            return "食費"

        if "AMAZON" in normalized_name:
            return "日用品"

        if "APPLE.COM" in normalized_name:
            return "サブスク"

        if "保険" in normalized_name:
            return "保険"

        if "コミック" in normalized_name:
            return "娯楽"

        if "グレイル" in normalized_name or "QOO10" in normalized_name:
            return "衣類"

        if "楽天証券" in normalized_name:
            return "NISA"

        return "未分類"

    def handle(self, *args, **options): #コマンドを実行したときに動く処理を書くメソッド。つまり、python manage.py import_csvを実行すると、このhandleの中が上から順番に動く
#*argsと**optionsは、コマンドに追加の値やオプションを渡すときに使う。今は使っていないけど、Djangoのコマンドでは基本的に書いておく。
        file_path = options["file_path"]
        billing_month = options["billing_month"]#これは、add_arguments()で受け取った値を、handle()の中で使いやすい変数に入れ直している。

        with open(
            file_path,
            "r",
            encoding="utf-8-sig",
            newline="" #newline="" は、CSVを読み書きするときの改行処理をPythonに勝手に変えさせない設定だよ。
        ) as f:
            reader = csv.reader(f)

            # 見出し行を1行飛ばす
            next(reader) #最初の行は、利用 利用店名とかという見出しなので、データベースには登録しない。

            for row in reader:
                if not row:
                    continue

                date_text = row[0].strip()

                if not date_text:
                    continue

                try: #今回のCSVには、ご利用キャンセルなど のような、日付ではない行も入っていた。そのような行でプログラム全体が止まらないようにしている。
                    used_date = datetime.strptime( #文字列の日付を、Pythonの日付データに変換し始めている。
                        date_text,
                        "%Y/%m/%d"
                    ).date() #datetime.strptime()で作った日時データから、日付部分だけを取り出している。結果は、datetime.date(2026, 6, 30)のような日付データになる。
                    # これをする理由はdatetime.strptime()だけだと、日付＋時刻を持つ datetime 型になるから。
                except ValueError:
                    continue

                Expense.objects.get_or_create( #Expenseモデルを使って、新しいデータを1件データベースへ登録するget_or_create(...)は、同じ条件の明細があれば追加しない。
                    used_date=used_date,
                    store_name=row[1],
                    amount=int(row[4]),
                    billing_month=billing_month,
                    defaults={"category": self.classify_category(row[1])} #defaults=→ 新しくデータを作る場合の初期値 "category"→ Expenseモデルのcategoryという項目名 
                    #→ 店名からカテゴリを判定した結果 → row[1]→ CSVの店名
                )

        self.stdout.write( #ターミナルへメッセージを表示する。普通のprint()でも表示できるけど、Djangoの独自コマンドではself.stdout.write()を使うのが正式な書き方。
            self.style.SUCCESS(f"{billing_month}のCSVを登録しました") #Djangoの管理コマンドではself.stdout.write()を使って、成功時はself.style.SUCCESS()を付ける書き方がよく使われる。
            # ほかにも例えば、self.style.WARNING("注意があります") self.style.ERROR("エラーが発生しました")などがある。
        )

# importという自作コマンドとして見つけてもらうために必要。Djangoは、どこにあるPythonファイルでも勝手にコマンドとして読み込むわけではなく、決められた場所だけを探すためこの形。
# __init__.pyは、そのフォルダーをPythonのパッケージとして扱いやすくするためのファイル。中身は空で大丈夫。
# つまりこれは、CSV処理そのものに必要というより、manage.py import_csvという形で実行するためのDjango側のルールだよ。

# 今回のimport_csvを実行すると、import_csv.pyの中の
# class Command(BaseCommand):
#     def handle(self, *args, **options):
# このhandle()の中身が動いて、CSVを読み込んでデータベースに登録する。つまり、import_csv.pyを直接実行するのではなく、
# Djangoに「CSVを登録して」と命令する仕組みにしてる感じ。