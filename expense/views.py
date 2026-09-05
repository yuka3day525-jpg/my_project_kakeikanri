from django.shortcuts import render,redirect,get_object_or_404
import csv
import io
from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from datetime import datetime,date,timedelta
from .models import Expense,ExpenseCategoryRule,BankCategoryRule,Bank,Household
from django.db.models import Sum
from django.views.generic import UpdateView,View
from .forms import ExpenseCategoryForm,BankCategoryForm,CsvUploadForm_Expense,CsvUploadForm_Bank,NisaUploadForm
from .utils import normalize_store_name,classify_category,classify_bank_category

@login_required #「この下の関数を実行する前に、ログインしてるか確認してね」というデコレーター。
def csv_upload(request):#requestには、ブラウザから送られてきた情報が入る。
    household = request.user.households.first()
    if request.method == "POST":#CSVを選んで「取り込む」ボタンを押したときはPOST→入力されたCSVと対象月を受け取る
        form = CsvUploadForm_Expense(#送信された内容をCsvUploadFormに渡している。
            request.POST,#には普通の入力項目が入る。
            request.FILES,#にはアップロードされたファイルが入る。
        )

        

        if form.is_valid():#フォームの入力内容に問題がないかチェック。CSVファイルが選択されているや対象月が入力されている
            csv_file = form.cleaned_data["csv_file"]#検証済みフォームから、アップロードされたCSVファイルを取り出してる。cleaned_dataは、フォームのチェックが終わって、安全に使える状態になった値
            billing_month = form.cleaned_data["billing_month"]#同じように対象月を取り出す。

            ai_target_pks=[]

            text_file = io.TextIOWrapper(#ブラウザからアップロードされたcsv_fileは、そのままだとバイナリデータとして扱われている。つまり、文字として読む準備がまだできてないファイル
#そこで、io.TextIOWrapper(...)を使って、このファイルを文字として読めるようにしてと変換している。
                csv_file.file,#は、アップロードされたファイル本体。
                encoding="utf-8-sig",#このCSVはUTF-8-SIGとして文字を読んでという指定
            )

            reader = csv.reader(text_file)#CSV形式として読む。

            next(reader)#CSVの最初の1行を飛ばす。
          
            for row in reader:#CSVを1行ずつ取り出す。
                if not row:
                    continue

                date_text = row[0].strip()

                if not date_text:
                    continue

                try:
                    used_date = datetime.strptime(
                        date_text,
                        "%Y/%m/%d", 
                    ).date()
                except ValueError:
                    continue#今の1回分の処理をここでやめて、次のrowへ行く

                category, classification_method = classify_category(row[1],household)

                expense,created = Expense.objects.get_or_create(#同じ明細があるか確認して、なければ新しく作る
                    household=household,
                    owner=request.user,
                    used_date=used_date,
                    store_name=row[1],
                    amount=int(row[4]),
                    billing_month=billing_month,
                    defaults={
                        "category": category,
                        "classification_method": classification_method,
                    },
                )

                if expense.category == "未分類":
                    ai_target_pks.append(
                        expense.pk
                    )

            #未分類だけまとめてGeminiへ
            if ai_target_pks:

                ai_target = Expense.objects.filter(
                    pk__in = ai_target_pks,
                    household = household
                )

                store_names = [
                    expense.store_name for expense in ai_target
                ]

                from .ai import gemini_predict_category
                ai_result = gemini_predict_category(store_names)

                for expense,category in zip(
                    ai_target,ai_result
                ):
                    expense.category = category
                    expense.classification_method = "ai"
                    expense.save()

            return redirect(#CSVを全部登録し終えたら、その月の一覧画面へ移動する。
                "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                month=billing_month,#<str:month>に2026-08を渡してる。
            )

    else:
        form = CsvUploadForm_Expense()#新しいCSVアップロードフォームを作る。

    return render(
        request,
        "expense/csv_upload.html",
        {
            "form": form,
        },
    )

@login_required
def ginkou_upload(request):
    household = request.user.households.first()
    if request.method == "POST":#CSVを選んで「取り込む」ボタンを押したときはPOST→入力されたCSVと対象月を受け取る
        form = CsvUploadForm_Bank(#送信された内容をCsvUploadFormに渡している。
            request.POST,#には普通の入力項目が入る。
            request.FILES,#にはアップロードされたファイルが入る。
        )

        if form.is_valid():#フォームの入力内容に問題がないかチェック。CSVファイルが選択されているや対象月が入力されている
            bank_choice = form.cleaned_data["bank_choice"]
            uploaded_file = form.cleaned_data["csv_file"]#検証済みフォームから、アップロードされたCSVファイルを取り出してる。cleaned_dataは、フォームのチェックが終わって、安全に使える状態になった値
            billing_month = form.cleaned_data["billing_month"]#同じように対象月を取り出す。


            # アップロードされたExcelファイルを開く
            workbook = load_workbook(
                uploaded_file,
                data_only=True,
            )

            # Excelの最初のシートを取得
            sheet = workbook.active

            if bank_choice == "rakuten":

                ai_target_pks=[]

                # 2行目から1行ずつ読む
                # min_row=2なので、1行目の見出しは自動的に飛ばす
                for row in sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ):
                    if not row:
                        continue

                    # 1列目：取引日
                    if row[0] is None:
                        continue

                    date_text = str(row[0]).strip()

                    try:
                        used_date = datetime.strptime(
                            date_text,
                            "%Y%m%d",
                        ).date()
                    except ValueError:
                        continue#今の1回分の処理をここでやめて、次のrowへ行く


                    if used_date.strftime("%Y-%m") == billing_month:
                        category, classification_method = classify_bank_category(str(row[3]),household)

                        rakuten,created = Bank.objects.get_or_create(#同じ明細があるか確認して、なければ新しく作る
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row[1]),
                            zankin=int(row[2]),
                            billing_month=billing_month,
                            store_name=str(row[3]),
                            defaults={
                                "category": category,
                                "classification_method": classification_method,
                            },
                    )

                        if rakuten.category == "未分類":
                            ai_target_pks.append(
                                rakuten.pk
                            )

                #未分類だけまとめてGeminiへ
                if ai_target_pks:
    
                    ai_target = Bank.objects.filter(
                        pk__in = ai_target_pks,
                        household = household
                    )
    
                    store_names = [
                        bank.store_name for bank in ai_target
                    ]
    
                    from .ai import bank_gemini_predict_category
                    ai_result = bank_gemini_predict_category(store_names)
    
                    for bank,category in zip(
                        ai_target,ai_result
                    ):
                        bank.category = category
                        bank.classification_method = "ai"
                        bank.save()
                                      

            elif bank_choice == "ufj":
                # 2行目から1行ずつ読む
                # min_row=2なので、1行目の見出しは自動的に飛ばす

                ai_target_pks=[]

                for row in sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ):
                    if not row:
                        continue

                    # 1列目：取引日
                    if row[0] is None:
                        continue

                    if isinstance(row[0], datetime):
                        used_date = row[0].date()
                    else:
                        date_text = str(row[0]).strip()

                        try:
                            used_date = datetime.strptime(
                                date_text,
                                "%Y/%m/%d",
                            ).date()
                        except ValueError:
                            continue
# 何をしているか
# Excelのrow[0]
#        ↓
#        ├─ datetime型？
#        │      ↓ YES
#        │   .date()で日付にする
#        │
#        └─ 文字列？
#               ↓
#         "%Y/%m/%d"で変換

                
                    if used_date.strftime("%Y-%m") == billing_month:
                        category, classification_method = classify_bank_category(str(row[2]),household)
                        ufj,created = Bank.objects.get_or_create(#同じ明細があるか確認して、なければ新しく作る
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row[3]),
                            zankin=int(row[5]),
                            billing_month=billing_month,
                            store_name=str(row[2]),
                           defaults={
                                "category": category,
                                "classification_method": classification_method,
                            },
                        )

                        if ufj.category == "未分類":
                            ai_target_pks.append(
                                ufj.pk
                            )

                #未分類だけまとめてGeminiへ
                if ai_target_pks:
    
                    ai_target = Bank.objects.filter(
                        pk__in = ai_target_pks,
                        household = household
                    )
    
                    store_names = [
                        bank.store_name for bank in ai_target
                    ]
    
                    from .ai import bank_gemini_predict_category
                    ai_result = bank_gemini_predict_category(store_names)
    
                    for bank,category in zip(
                        ai_target,ai_result
                    ):
                        bank.category = category
                        bank.classification_method = "ai"
                        bank.save()

            elif bank_choice == "roukin":

                ai_target_pks=[]

                for row in sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                ):
                    if not row:
                        continue

                    if row[0] is None:
                        continue

                    # 労金の日付はExcelのシリアル値になっている
                    if isinstance(row[0], (int, float)):
                        used_date = from_excel(
                            row[0],
                            workbook.epoch,
                        ).date()

                    elif isinstance(row[0], datetime):
                        used_date = row[0].date()

                    elif isinstance(row[0], date):
                        used_date = row[0]

                    else:
                        date_text = str(row[0]).strip()

                        try:
                            used_date = datetime.strptime(
                                date_text,
                                "%Y/%m/%d",
                            ).date()
                        except ValueError:
                            continue

                    if used_date.strftime("%Y-%m") == billing_month:
                        category, classification_method = classify_bank_category(str(row[6]),household)
                        roukin,created = Bank.objects.get_or_create(
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row[2]),
                            zankin=int(row[5]),
                            billing_month=billing_month,
                            store_name=str(row[6]),
                            defaults={
                                "category": category,
                                "classification_method": classification_method,
                            },
                        )

                        if roukin.category == "未分類":
                            ai_target_pks.append(
                                roukin.pk
                            )

                #未分類だけまとめてGeminiへ
                if ai_target_pks:
    
                    ai_target = Bank.objects.filter(
                        pk__in = ai_target_pks,
                        household = household
                    )
    
                    store_names = [
                        bank.store_name for bank in ai_target
                    ]
    
                    from .ai import bank_gemini_predict_category
                    ai_result = bank_gemini_predict_category(store_names)
    
                    for bank,category in zip(
                        ai_target,ai_result
                    ):
                        bank.category = category
                        bank.classification_method = "ai"
                        bank.save()

            return redirect(#CSVを全部登録し終えたら、その月の一覧画面へ移動する。
                "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                month=billing_month,#<str:month>に2026-08を渡してる。
            )

    else:
        form = CsvUploadForm_Bank()#新しいCSVアップロードフォームを作る。

    return render(
        request,
        "expense/bank_upload.html",
        {
            "form": form,
        },
    )
# 今回
# xlsxをアップロード
# ↓
# load_workbookでExcelとして開く
# ↓
# sheetを取得
# ↓
# 1行ずつ読む

# 今まで
# アップロード
# ↓
# TextIOWrapperで文字に変換
# ↓
# csv.reader
# ↓
# 1行ずつ読む
@login_required
def nisa_create(request):
    if request.method == "POST":
        form = NisaUploadForm(request.POST)

        if form.is_valid():
            nisa = form.save(commit=False) #まだ保存せずNIsaオブジェクトだけ作る、valueしか保存するとこがないがユーザーなどが入ってないため

            nisa.owner = request.user
            nisa.household = request.user.households.first()

            nisa.save()
            month = nisa.recorded_date.strftime("%Y-%m")
            return redirect(#CSVを全部登録し終えたら、その月の一覧画面へ移動する。
                "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                month=month,#<str:month>に2026-08を渡してる。
            )
    else:
        form = NisaUploadForm()#新しいCSVアップロードフォームを作る。
    return render(
        request,
        "expense/nisa_upload.html",
        {
            "form": form,
        },
    )
    
            

@login_required
def expense_index(request):
    today = date.today()
    first_day = today.replace(day=1)
    last_month_day = first_day - timedelta(days=1)
#これで１か月前のexpense_monthのページに行ってくれる
    month = last_month_day.strftime("%Y-%m")
    return redirect("expense:expense_month", month=month)
#自動で/expense/2026-08/へつながる

@login_required
def expense_month(request,month):
    household = request.user.households.first() #でログイン中のユーザーが所属しているHouseholdを取得するfirstはログイン中ユーザーが所属している家計を1個取るいう意味
    expenses_list = Expense.objects.filter(household=household,billing_month=month).order_by("-used_date")
    #Expenseの中から「対象月がmonthと同じデータだけ」に絞り込むって意味。たとえばURLが、/expense/2026-08/なら、def expense_month(request, month):のmonthには、"2026-08"が入る。だからDBの中に、
# 2026-07  ローソン  500円
# 2026-08  Amazon   3000円
# 2026-08  セブン    800円
# とあったら、8月ページでは、
# Amazon  3000円
# セブン   800円 だけ取り出す。
    rakuten_list = Bank.objects.filter(household=household,billing_month=month,bank="rakuten").order_by("-used_date")
    ufj_list = Bank.objects.filter(household=household,billing_month=month,bank="ufj").order_by("-used_date")
    roukin_list = Bank.objects.filter(household=household,billing_month=month,bank="roukin").order_by("-used_date")

    month_list = (
    Expense.objects.filter(household=household).
    values_list("billing_month", flat=True)#はExpenseの全項目じゃなくて、billing_monthだけ取り出す。flat=Trueがないと、
# [("2026-07",), ("2026-07",), ("2026-08",), ("2026-08",)]みたいに1個ずつタプルになる。 今回は月だけ欲しいからflat=Trueで普通の値にしてる。
    .distinct()#重複を消す。
    .order_by("-billing_month")
    )

    my_expenses = Expense.objects.filter(household=household,owner=request.user,billing_month=month,).order_by("-used_date")
    my_rakutens = Bank.objects.filter(household=household,owner=request.user,billing_month=month,bank="rakuten",).order_by("-used_date")
    my_ufjs = Bank.objects.filter(household=household,owner=request.user,billing_month=month,bank="ufj",).order_by("-used_date")
    my_roukins = Bank.objects.filter(household=household,owner=request.user,billing_month=month,bank="roukin",).order_by("-used_date")

    #世帯円グラフ用
    expense_data = Expense.objects.filter(household=household,billing_month=month,).values("used_date","amount","category","owner__username")#owner はユーザーIDになるから変えた
    bank_data = Bank.objects.filter(household=household,billing_month=month,).exclude(
                category__in=["カード引き落とし","送金","入金","給料","サービス(還元など)","その他","未分類"
                ]).values(
                "used_date","amount","category","owner__username",)
    expense_df = pd.DataFrame(expense_data,columns=["used_date","amount","category","owner__username",])
    bank_df = pd.DataFrame(bank_data,columns=["used_date","amount","category","owner__username",])
    bank_df = bank_df[bank_df["amount"] < 0].copy()
    bank_df["amount"] = bank_df["amount"].abs()
    all_df = pd.concat([expense_df, bank_df],ignore_index=True,)
    category_df = (all_df.groupby("category")["amount"].sum().reset_index()) #reset_index() categoryを普通の列に戻す
    # Chart.jsに渡せるPythonのリストに変換する。
    chart_labels = category_df["category"].tolist()
    chart_values = category_df["amount"].tolist()

    #ユーザー割合用
    owner_df = (all_df.groupby("owner__username")["amount"].sum().reset_index())
    owner_labels = owner_df["owner__username"].tolist()
    owner_values = owner_df["amount"].tolist()

    #世帯支出推移
    sisyutu_date = Bank.objects.filter(household=household,category__in=[
        "現金引き出し","国保・住民税・年金類","娯楽・趣味","家賃","NISA","カード引き落とし","家具家電・設備","保険（家や生命など）","日用品","衣類"
    ]).values("billing_month","amount","category",)
    sisyutu_df = pd.DataFrame(sisyutu_date,columns=["billing_month", "amount", "category"])
    sisyutu_df = sisyutu_df[sisyutu_df["amount"] < 0].copy()
    sisyutu_df["amount"] = sisyutu_df["amount"].abs()
    monthly_df = (sisyutu_df.groupby("billing_month")["amount"].sum().reset_index().sort_values("billing_month"))
    
    monthly_labels = monthly_df["billing_month"].tolist()
    monthly_values = monthly_df["amount"].tolist()


                


    bank_data2 = Bank.objects.filter(household=household,billing_month=month,).values("used_date","amount","category","owner",)
    category_totals = (
            Expense.objects.filter(household=household,billing_month=month).
            values("category").#対象月がmonthと同じデータだけカテゴリーごとに分ける。
            annotate(total=Sum("amount")).#そのカテゴリー内の金額を合計して、totalという名前で持たせる。 annotate は、各グループに、合計や件数などの計算結果をくっつける」
            order_by("category") 
        )
    
    return render(
        request,
        "expense/expense_month.html",
        {"expenses": expenses_list,
         "rakutens": rakuten_list,
         "ufjs":ufj_list,
         "roukins":roukin_list,
         "month":month,
         "month_list": month_list,
         "my_expenses":my_expenses,
         "my_rakutens":my_rakutens,
         "my_ufjs":my_ufjs,
         "my_roukins":my_roukins,

         "chart_labels": chart_labels,
         "chart_values": chart_values,
         "monthly_labels" : monthly_labels,
         "monthly_values" : monthly_values,
         "owner_labels": owner_labels,
         "owner_values": owner_values,

         "category_totals": category_totals,

         },
    )

class ExpenseCategoryUpdateView(LoginRequiredMixin,UpdateView):#UpdateViewを継承しているので、これは既存のデータを編集するためのビューになる。今回ならすでにDBにある明細のcategoryを書き換える。
    model = Expense #どのモデルのデータを編集するか指定している。
    form_class = ExpenseCategoryForm
    #編集画面で、どのフォームを使うか指定している。forms.pyで作ったこれ。fields = ["category"]なので、編集できるのはカテゴリーだけ。
    template_name = "expense/category_update.html"#編集画面として表示するHTMLファイルを指定している。

    def get_queryset(self):
        household = self.request.user.households.first()

        return super().get_queryset().filter(
            household=household
        ) #この処理で例えば他Householdの pk=100 に直接アクセスしても、404になる。get_queryset() は「そもそもどのデータを編集対象として探すか」を決める処理

    def form_valid(self, form):#送信されたフォーム。今回なら、選択されたカテゴリー save_as_ruleのチェック状態
        response = super().form_valid(form)#選択されたカテゴリー save_as_ruleのチェック状態が入ってる form_validというメソッドを自分で上書きしている。
        #UpdateViewにはもともとform_valid()というメソッドがあって、フォームの内容に問題がなかったときに呼ばれる。
#これはまず、UpdateViewが本来する保存処理を実行している。今回なら、Expenseのcategoryを更新→DBへ保存→保存後に一覧画面へ移動するレスポンスを作る、superは親クラスであるUpdateView側の処理を使う、という意味。
        if form.cleaned_data["save_as_rule"]:#チェックボックスがオンか確認している。form.cleaned_data:フォームから送られた値を、Djangoが検証して使いやすいPythonの値に変換したもの。
            #チェックしていないなら、中身は{"category": "食費",　"save_as_rule": False,}になる、それでsaveasTrueだけ取り出してる
            normalized_name = normalize_store_name(#utilsからインポートしたもの
                self.object.store_name #今編集して保存されたExpenseデータの店名
            )

            ExpenseCategoryRule.objects.update_or_create(#CategoryRule:models.pyにある分類ルール用のモデル。update_or_create():同じルールがあるか探して、あれば更新なければ新規作成する。
                household=self.object.household,
                keyword=normalized_name,#どのルールを探すか指定している.CategoryRuleモデルの、keywordが、整えた店名と同じデータを探す。たとえば、normalized_name = "AMAZON.CO.JP"ならDBでkeywordがAMAZON.CO.JPのルールを探す。
                defaults={
                "category": self.object.category,},#更新する値、または新規作成時に追加する値。self.object.category今保存した明細の変更後カテゴリー。
            )
        return response

    def get_context_data(self, **kwargs):#これは、HTMLに渡すデータを作るためのメソッド。UpdateView はもともと、勝手に
        # {"object": 今編集しているデータ, "form": 編集フォーム}みたいなデータをHTMLへ渡してくれてる。
        context = super().get_context_data(**kwargs) #で、UpdateViewが元々HTMLに渡そうとしていたデータ一式を受け取る。
        context["kind"] = "expense" #で、その辞書に自分で新しいデータを1個追加してる。{"object": expense,"form": form,"kind": "expense",}になる
        return context

    def get_success_url(self):
        return f"/expense/{self.object.billing_month}/"
    #ここは、カテゴリー編集が終わったあとに「元いた月のページへ戻す」ための処理。self.objectは、今編集していたExpenseデータ。


class BankCategoryUpdateView(LoginRequiredMixin,UpdateView):
    model = Bank
    form_class = BankCategoryForm
    template_name = "expense/category_update.html"

    def get_queryset(self):
        household = self.request.user.households.first()

        return super().get_queryset().filter(
            household=household
        ) #get_queryset() は「そもそもどのデータを編集対象として探すか」を決める処理

    def form_valid(self, form):
        response = super().form_valid(form) #Bankのcategoryを更新→DBへ保存→保存後に一覧画面へ移動するレスポンスを作る
        if form.cleaned_data["save_as_rule"]:
            normalized_name = normalize_store_name(
                self.object.store_name 
            )
            BankCategoryRule.objects.update_or_create(
                household=self.object.household,
                keyword=normalized_name,
                defaults={
                "category": self.object.category,},
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context["kind"] = "bank" 
        return context

    def get_success_url(self):
        return f"/expense/{self.object.billing_month}/"
    
class ExpenseDeleteView(LoginRequiredMixin,View):
    def get(self,request,pk):
        household = request.user.households.first()
        expense = get_object_or_404(Expense,pk=pk,household=household)
        return render(request,"expense/delete.html",{"object":expense})

    def post(self,request,pk):
        household = request.user.households.first()
        expense = get_object_or_404(Expense,pk=pk,household=household)
        billing_month = expense.billing_month #削除前にオブジェクトを残した
        expense.delete()
        return redirect('expense:expense_month', month=billing_month)

class BankDeleteView(LoginRequiredMixin,View):
    def get(self,request,pk):
        household = request.user.households.first()
        bank = get_object_or_404(Bank,pk=pk,household=household)
        return render(request,"expense/delete.html",{"object":bank})

    def post(self,request,pk):
        household = request.user.households.first()
        bank = get_object_or_404(Bank,pk=pk,household=household)
        billing_month = bank.billing_month #削除前にオブジェクトを残した
        bank.delete()
        return redirect('expense:expense_month',month=billing_month)

def bulk_save_rules(request):
    if request.method == "POST":
        household = request.user.households.first()
        selected_pks = request.POST.getlist(
            "selected_expenses"
        )
        month = request.POST.get("month")
        expenses = Expense.objects.filter(
            pk__in=selected_pks,
            household=household,
        )
        for expense in expenses:
            ExpenseCategoryRule.objects.update_or_create(
                household=household,
                keyword=expense.store_name,
                defaults={
                    "category": expense.category
                }
            )
    return redirect('expense:expense_month', month=month)

def bank_bulk_save_rules(request):
    if request.method == "POST":
        household = request.user.households.first()
        selected_pks = request.POST.getlist(
            "selected_expenses"
        )
        month = request.POST.get("month")
        expenses = Bank.objects.filter(
            pk__in=selected_pks,
            household=household,
        )
        for expense in expenses:
            BankCategoryRule.objects.update_or_create(
                household=household,
                keyword=expense.store_name,
                defaults={
                    "category": expense.category
                }
            )
    return redirect('expense:expense_month', month=month)


expense_category_update = ExpenseCategoryUpdateView.as_view()
ginkou_category_update = BankCategoryUpdateView.as_view()
expense_delete = ExpenseDeleteView.as_view()
ginkou_delete=BankDeleteView.as_view()
#UpdateViewはかなり色々自動でやってくれてて、
# model = Expense
# form_class = ExpenseCategoryForm
# template_name = "expense/category_update.html"
# だけで、
# 対象データを探す → フォームを作る → HTMLに渡す → POSTされたら検証する → 保存するまで一通りやってくれる。
#だからrenderがいらない

# コマンドから直接ファイルと月をアップロードする方法
# PS C:\Users\genta\OneDrive\Desktop\my_project> python manage.py import_csv "2026_8.csv" 2026-07
# 2026-07のCSVを登録しました