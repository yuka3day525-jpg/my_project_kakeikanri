from django.db import models
from django.conf import settings

class Household(models.Model):
    name = models.CharField(
        "家計名",
        max_length=100,
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,#Djangoで現在使っているUserモデルを指定している
        related_name="households",#逆方向から取るため
    )
# 1つの家計に複数ユーザーが入れるからManyToManyField
#Household「ふたりの家計」   
  # ├─ user1
  # └─ user2
# さらに仕組み上は、
# user1
#  ├─ ふたりの家計
#  └─ 自分だけの家計 みたいに、1人のユーザーが複数Householdに所属することもできる。つまり、多対多になってる。
    
# household.members.all()はこの household の members に登録されているユーザーを全部取る あなた/彼氏
# 逆に、「このユーザーが所属している家計は？」って調べたいこともある。そのとき related_name="households" があるから、
# user.households.all() =Household（二人の家計） でとれるようになる
    def __str__(self):
        return self.name

class Expense(models.Model):
    CATEGORY_CHOICES=[("食費(自炊)", "食費(自炊)"),
        ("食費(外食)", "食費(外食)"),             
        ("日用品", "日用品"),
        ("衣類", "衣類"),
        ("娯楽・趣味", "娯楽・趣味"),
        ("保険（家や生命など）", "保険（家や生命など）"),
        ("NISA", "NISA"),
        ("プレゼント","プレゼント"),
        ("旅行・レジャー", "旅行・レジャー"),
        ("定期代", "定期代"),
        ("交通費", "交通費"),
        ("サブスク", "サブスク"),
        ("光熱費", "光熱費"),
        ("サロン代", "サロン代"),
        ("車関係（ガソリン・車保険など）", "車関係（ガソリン・車保険など）"),
        ("ETC", "ETC"),
        ("携帯料金", "携帯料金"),
        ("家具家電・設備", "家具家電・設備"),
        ("医療費", "医療費"),
        ("その他", "その他"),
        ("未分類", "未分類"),
    ]
    CLASSIFICATION_CHOICES = [
    ("ai", "AI分類"),
    ("memory", "記憶分類"),
    ("ml", "機械学習"),
    ("rule","ルール付け分類")
    ]
 
    used_date = models.DateField("利用日")
    store_name = models.CharField("利用店名", max_length=255)
    amount = models.IntegerField("利用金額")
    billing_month = models.CharField("対象月",max_length=7,)
    # 最初は空欄でも登録できるようにする
    category = models.CharField(
        "カテゴリー",
        max_length=50,
        # blank=True,
        default="未分類",
        choices=CATEGORY_CHOICES,
    ) #blank=True 入力フォームや管理画面で、カテゴリーを空欄のままでもOKにする。これがない場合、この項目は必須ですとなる。
    #default="" カテゴリーを指定しなかった場合、データベースには初期値として未分類を入れる。
    created_at = models.DateTimeField("登録日時", auto_now_add=True) #←このデータが初めて作成されたその時の日時を保存
    household = models.ForeignKey(#Expense 1件1件を「どの家計グループのデータか」に紐づけるための項目
    Household,#Expense は1つの Household に所属する ForeignKey は 多対1 の関係。
    on_delete=models.CASCADE,#紐づいてるHouseholdを削除したら、そのHouseholdのExpenseも削除する
    null=True,#これは データベース上で household が空でもOK という意味。今回これを付けてる理由は、今まで作った既存のExpenseデータがもうあるから
    blank=True,#フォームやadmin上でも空欄を許可する
    related_name="expenses",
    )#これがあることで、Household側から、household.expenses.all()って書ける。つまりこのHouseholdに所属してるExpenseを全部取る
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        null=True,
        blank=True,
    )
    classification_method = models.CharField(
    max_length=10,
    choices=CLASSIFICATION_CHOICES,
    blank=True,
    )

    def __str__(self):
        return f"{self.used_date} {self.store_name} {self.amount}円" #そのオブジェクトを文字として表示するときに何を出すか決めるメソッド。__str__：文字列として表示するとき自動で呼ばれる 最近行った操作のところ！
    # 銀行　年金まとめる国民健康保険、、
class Bank(models.Model):
    BANK_CHOICES = [("rakuten","楽天銀行"),("ufj","三菱UFJ"),("roukin","ろうきん")]
    CATEGORY_CHOICES=[("給料", "給料"),
        ("入金","入金"),
        ("送金","送金"),
        ("現金引き出し", "現金引き出し"),
        ("国保・住民税・年金類", "国保・住民税・年金類"),
        ("娯楽・趣味", "娯楽・趣味"),
        ("NISA", "NISA"),
        ("家賃","家賃"),
        ("カード引き落とし", "カード引き落とし"),
        ("サービス(還元など)", "サービス(還元など)"),
        ("家具家電・設備", "家具家電・設備"),
        ("保険（家や生命など）", "保険（家や生命など）"),
        ("日用品", "日用品"),
        ("食費", "食費"),
        ("衣類", "衣類"),
        ("その他", "その他"),
        ("未分類", "未分類"),
    ]
    CLASSIFICATION_CHOICES = [
        ("ai", "AI分類"),
        ("memory", "記憶分類"),
        ("ml", "機械学習"),
        ("rule","ルール付け分類")
    ]
    bank = models.CharField("銀行",max_length=15,choices=BANK_CHOICES)
    used_date = models.DateField("取引日")
    amount = models.IntegerField("入出金")
    zankin = models.IntegerField("取引後残高")
    store_name = models.CharField("内容", max_length=255)
    # 最初は空欄でも登録できるようにする
    billing_month = models.CharField("対象月",max_length=7,blank=True)
    category = models.CharField(
        "カテゴリー",
        max_length=50,
        # blank=True,
        default="未分類",
        choices=CATEGORY_CHOICES,
    ) #blank=True 入力フォームや管理画面で、カテゴリーを空欄のままでもOKにする。これがない場合、この項目は必須ですとなる。
    #default="" カテゴリーを指定しなかった場合、データベースには初期値として未分類を入れる。
    created_at = models.DateTimeField("登録日時", auto_now_add=True) #←このデータが初めて作成されたその時の日時を保存
    household = models.ForeignKey(
    Household,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="banks",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="banks",
        null=True,
        blank=True,
    )
    classification_method = models.CharField(
        "分類方法",
        max_length=10,
        choices=CLASSIFICATION_CHOICES,
        blank=True,
    )
    

    def __str__(self):
        return f"{self.bank} {self.used_date} {self.amount} {self.zankin}円" #そのオブジェクトを文字として表示するときに何を出すか決めるメソッド。__str__：文字列として表示するとき自動で呼ばれる 最近行った操作のところ！

# 共同家計
# │
# ├─ Expense
# │   ├─ ローソン 500円
# │   ├─ Amazon 3000円
# │   └─ GRL 4000円
# │
# └─ Rakuten
#     ├─ 給与振込
#     ├─ ATM
#     └─ 口座振替


class ExpenseCategoryRule(models.Model):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="expense_category_rules",
    )

    keyword = models.CharField(
        "店名キーワード",
        max_length=255,
        # unique=True,#その項目に同じ値を2件以上登録できないようにする設定,別世帯でも同じkeywordを
        # 登録できなくなるので消した
    )

    category = models.CharField(
            "カテゴリー",
            max_length=50,
            choices=Expense.CATEGORY_CHOICES,
    )

    def __str__(self):
        return f"{self.keyword} → {self.category}"

class BankCategoryRule(models.Model):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bank_category_rules",
    )

    keyword = models.CharField(
        "店名キーワード",
        max_length=255,
        # unique=True,#その項目に同じ値を2件以上登録できないようにする設定,別世帯でも同じkeywordを
        # 登録できなくなるので消した
    )

    category = models.CharField(
            "カテゴリー",
            max_length=50,
            choices=Bank.CATEGORY_CHOICES,
    )

    def __str__(self):
        return f"{self.keyword} → {self.category}"

class Nisa(models.Model):
    household = models.ForeignKey(
            Household,
            on_delete=models.CASCADE,
            null=True,
            blank=True,
            related_name="nisa",
    )

    owner = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="nisa",
            null=True,
            blank=True,
    )
    value = models.IntegerField("NISA残高")
    recorded_date = models.DateField("更新日時",auto_now_add=True)#←このデータが初めて作成されたその時の日時を保存



 


