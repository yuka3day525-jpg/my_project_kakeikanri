from django.shortcuts import render,redirect,get_object_or_404
import csv
import io
from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Subquery

from datetime import datetime,date,timedelta
from .models import Expense,ExpenseCategoryRule,BankCategoryRule,Bank,Nisa,Household
from django.db.models import Sum
from django.views.generic import UpdateView,View
from .forms import ExpenseCategoryForm,BankCategoryForm,CsvUploadForm_Expense,CsvUploadForm_Bank,NisaUploadForm
from .utils import normalize_store_name,classify_category,classify_bank_category
from .chart import (
    make_category_chart,make_expense_trend_chart,make_food_chart,make_profit_chart,
)

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
                # "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                # month=billing_month,#<str:month>に2026-08を渡してる。
                f"/expense/?new_month={billing_month}"
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
            
            if bank_choice == "rakuten":

                text_file = io.TextIOWrapper(
                    uploaded_file.file,
                    encoding="cp932",
                )

                reader = csv.reader(text_file)
                next(reader)  # 見出しを飛ばす

                ai_target_pks=[]

                for row in reader:

                    if not row:
                        continue

                    # 1列目：取引日
                    if not row[0]:
                        continue

                    date_text = row[0].strip()

                    try:
                        used_date = datetime.strptime(
                            date_text,
                            "%Y%m%d",
                        ).date()
                    except ValueError:
                        continue#今の1回分の処理をここでやめて、次のrowへ行く


                    if used_date.strftime("%Y-%m") == billing_month:
                        store_name = row[3].strip()
                        category, classification_method = classify_bank_category(store_name,household)

                        rakuten,created = Bank.objects.get_or_create(#同じ明細があるか確認して、なければ新しく作る
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row[1]),
                            zankin=int(row[2]),
                            billing_month=billing_month,
                            store_name=store_name,
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

                uploaded_file.seek(0) #ファイルの先頭に戻れ
                text = uploaded_file.read().decode("cp932")
# decode("cp932")を使うと、
# バイナリ
# ↓
# cp932として解読
# ↓
# 日本語の文字列
                df = pd.read_csv(
                    io.StringIO(text)
                )
# はCSVファイルっぽいものを受け取りたいから、
# 普通の文字列
# ↓
# StringIO
# ↓
# 仮想的なCSVファイル

# にして渡してる。

                ai_target_pks = []

                 # 金額を数値化,「お支払金額の列を数値型に変換。変換できないものはNaNにする」
                df["支払い金額"] = pd.to_numeric(
                    df["支払い金額"].astype(str).str.replace(",", "",regex=False),
                    errors="coerce"
                )

                df["預かり金額"] = pd.to_numeric(
                    df["預かり金額"].astype(str).str.replace(",", "",regex=False),
                    errors="coerce"
                )

                df["差引残高"] = pd.to_numeric(
                    df["差引残高"].astype(str).str.replace(",", "",regex=False),
                    errors="coerce"
                )

                 # 入出金列を作る
                df["入出金"] = (
                    df["預かり金額"].fillna(0)
                    -
                    df["支払い金額"].fillna(0)
                )

                for _, row in df.iterrows():#これは、DataFrameの中身を1行ずつ取り出して処理するための書き方だよ。

                    if pd.isna(row["日付"]):
                        continue

                    date_text = str(row["日付"]).strip()

                    try:
                        used_date = datetime.strptime(
                            date_text,
                            "%Y/%m/%d",
                        ).date()
                    except ValueError:
                        print("エラー起きてる")
                        continue

                
                    if used_date.strftime("%Y-%m") == billing_month:
                        store_name = str(row["摘要内容"])
                        category, classification_method = classify_bank_category(store_name,household)
                        ufj,created = Bank.objects.get_or_create(#同じ明細があるか確認して、なければ新しく作る
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row["入出金"]),
                            zankin=int(row["差引残高"]),
                            billing_month=billing_month,
                            store_name=store_name,
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

                uploaded_file.seek(0) #ファイルの先頭に戻れ
                text = uploaded_file.read().decode("cp932")

                df = pd.read_csv(
                    io.StringIO(text)
                )

                ai_target_pks=[]

# replace に対して、「これは正規表現として解釈しないで、普通の文字として置き換えてね」がregex=False

                 # 金額を数値化,「お支払金額の列を数値型に変換。変換できないものはNaNにする」
                df["お支払金額"] = pd.to_numeric(
                    df["お支払金額"].astype(str)
                    .str.replace("\\", "", regex=False)
                    .str.replace(",", "", regex=False),
                    errors="coerce"
                )

                df["お預り金額"] = pd.to_numeric(
                    df["お預り金額"].astype(str)
                    .str.replace("\\", "", regex=False)
                    .str.replace(",", "", regex=False),
                    errors="coerce"
                )

                df["残高"] = pd.to_numeric(
                    df["残高"].astype(str)
                    .str.replace("\\", "", regex=False)
                    .str.replace(",", "", regex=False),
                    errors="coerce"
                )

                 # 入出金列を作る
                df["入出金"] = (
                    df["お預り金額"].fillna(0)
                    -
                    df["お支払金額"].fillna(0)
                )
# たとえば、
# お預り金額   お支払金額
# 10000       NaN
# NaN         3000
# 5000        NaN
# なら、fillna(0) で空欄を0にしてから計算するから、
# お預り金額   お支払金額   入出金
# 10000       0            10000
# 0           3000         -3000
# 5000        0            5000

                for _, row in df.iterrows():#これは、DataFrameの中身を1行ずつ取り出して処理するための書き方だよ。

                    if pd.isna(row["取扱日付"]):
                        continue

                    date_text = str(row["取扱日付"]).strip()
                    year = int(billing_month[:4])

                    try:
                        used_date = datetime.strptime(
                            f"{year}年{date_text}",
                            "%Y年%m月%d日",
                        ).date()
                    except ValueError:
                        continue

                    if used_date.strftime("%Y-%m") == billing_month:

                        store_name = str(row["摘要"])
                        category, classification_method = classify_bank_category(store_name,household)
                        roukin,created = Bank.objects.get_or_create(
                            household=household,
                            owner=request.user,
                            bank=bank_choice,
                            used_date=used_date,
                            amount=int(row["入出金"]),
                            zankin=int(row["残高"]),
                            billing_month=billing_month,
                            store_name=store_name,
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
                # "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                # month=billing_month,#<str:month>に2026-08を渡してる。
                "expense:expense_index",
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
                # "expense:expense_month",#billing_month = "2026-08"なら/expense/2026-08/へ
                # month=month,#<str:month>に2026-08を渡してる。
                "expense:expense_index",
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
#     today = date.today()
#     first_day = today.replace(day=1)
#     last_month_day = first_day - timedelta(days=1)
# #これで１か月前のexpense_monthのページに行ってくれる
#     month = last_month_day.strftime("%Y-%m")
    household = request.user.households.first() #でログイン中のユーザーが所属しているHouseholdを取得するfirstはログイン中ユーザーが所属している家計を1個取るいう意味
    month_list = (
    Expense.objects.filter(household=household).
    values_list("billing_month", flat=True)#はExpenseの全項目じゃなくて、billing_monthだけ取り出す。flat=Trueがないと、
# [("2026-07",), ("2026-07",), ("2026-08",), ("2026-08",)]みたいに1個ずつタプルになる。 今回は月だけ欲しいからflat=Trueで普通の値にしてる。
    .distinct()#重複を消す。
    .order_by("-billing_month")
    )
    new_month = request.GET.get("new_month")
    latest_nisa = Nisa.objects.filter(household=household,owner=OuterRef("owner")).order_by("-recorded_date","-pk",)
    nisa_list = (Nisa.objects.filter(household=household,pk=Subquery(latest_nisa.values("pk")[:1])).select_related("owner"))

    latest_bank = Bank.objects.filter(household=household,owner=OuterRef("owner"),bank=OuterRef("bank"),).order_by("-used_date","-pk",)
    bank_balances = (Bank.objects.filter(household=household,pk=Subquery(latest_bank.values("pk")[:1])).select_related("owner"))

    asset_by_user = {}

    for bank in bank_balances:
        username = bank.owner.username

        if username not in asset_by_user:
            asset_by_user[username] = {
                "bank": 0,
                "nisa": 0,
                "total": 0,
            }

        asset_by_user[username]["bank"] += bank.zankin

    for nisa in nisa_list:
        username = nisa.owner.username

        if username not in asset_by_user:
            asset_by_user[username] = {
                "bank": 0,
                "nisa": 0,
                "total": 0,
            }

        asset_by_user[username]["nisa"] += nisa.value

    for data in asset_by_user.values():
        data["total"] = (
            data["bank"]
            + data["nisa"]
        )

    household_total_assets = sum(
        data["total"]
        for data in asset_by_user.values()
    )
    return render(
            request,"expense/index.html",
            {
             "month_list": month_list,
             "new_month": new_month,
             "nisa_list": nisa_list,
             "bank_balances": bank_balances,
             "asset_by_user": asset_by_user,
             "household_total_assets": household_total_assets,
            }
        )

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

    household_category = (
        make_category_chart(
            household,
            month,
        )
    )

    household_expense_trend = (
        make_expense_trend_chart(
            household
        )
    )

    household_food = (
        make_food_chart(
            household
        )
    )

    household_profit = (
        make_profit_chart(
            household
        )
    )

    my_category = (
        make_category_chart(
            household,
            month,
            request.user,
        )
    )

    my_expense_trend = (
        make_expense_trend_chart(
            household,
            request.user,
        )
    )

    my_food = (
        make_food_chart(
            household,
            request.user,
        )
    )

    my_profit = (
        make_profit_chart(
            household,
            request.user,
        )
    )
    
          
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

         # 世帯カテゴリー
        "chart_labels":
            household_category["labels"],

        "chart_values":
            household_category["values"],

        "detail_chart_labels":
            household_category[
                "detail_labels"
            ],

        "detail_chart_values":
            household_category[
                "detail_values"
            ],

        # 利用者別
        "owner_labels":
            household_category[
                "owner_labels"
            ],

        "owner_values":
            household_category[
                "owner_values"
            ],

        # 世帯支出推移
        "monthly_labels":
            household_expense_trend[
                "labels"
            ],

        "monthly_values":
            household_expense_trend[
                "values"
            ],

        # 世帯食費
        "food_monthly_labels":
            household_food["labels"],

        "food_out_values":
            household_food[
                "out_values"
            ],

        "food_home_values":
            household_food[
                "home_values"
            ],

        # 世帯収支
        "profit_labels":
            household_profit[
                "labels"
            ],

        "profit_income_values":
            household_profit[
                "income_values"
            ],

        "profit_expense_values":
            household_profit[
                "expense_values"
            ],

        "profit_values":
            household_profit[
                "profit_values"
            ],

        # 個人カテゴリー
        "my_chart_labels":
            my_category["labels"],

        "my_chart_values":
            my_category["values"],

        "my_detail_chart_labels":
            my_category[
                "detail_labels"
            ],

        "my_detail_chart_values":
            my_category[
                "detail_values"
            ],

        # 個人支出推移
        "my_monthly_labels":
            my_expense_trend[
                "labels"
            ],

        "my_monthly_values":
            my_expense_trend[
                "values"
            ],

        # 個人食費
        "my_food_monthly_labels":
            my_food["labels"],

        "my_food_out_values":
            my_food[
                "out_values"
            ],

        "my_food_home_values":
            my_food[
                "home_values"
            ],

        # 個人収支
        "my_profit_labels":
            my_profit[
                "labels"
            ],

        "my_profit_income_values":
            my_profit[
                "income_values"
            ],

        "my_profit_expense_values":
            my_profit[
                "expense_values"
            ],

        "my_profit_values":
            my_profit[
                "profit_values"
            ],

        "category_totals":
            category_totals,
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
            "selected_banks"
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