from .models import Expense,ExpenseCategoryRule,BankCategoryRule,Bank,Nisa,Household
from django.db.models import Sum
import pandas as pd

CATEGORY_GROUP = {
    "食費(外食)": "変動費",
    "食費(自炊)": "変動費",
    "日用品": "変動費",
    "衣類": "変動費",
    "娯楽・趣味": "変動費",
    "サロン代": "変動費",
    "プレゼント": "変動費",
    "交通費": "変動費",

    "車関係（ガソリン・車保険など）": "車関係",
    "ETC": "車関係",

    "旅行・レジャー": "旅費",

    "家賃": "固定費",
    "光熱費": "固定費",
    "国保・住民税・年金類": "固定費",
    "保険（家や生命など）": "固定費",
    "定期代": "固定費",
    "サブスク": "固定費",
    "携帯料金": "固定費",

    "家具家電・設備": "特別費",
    "医療費": "特別費",

    "その他": "その他",
    "現金引き出し": "現金引き出し",

    "NISA": "貯蓄・投資",
}

# カテゴリー別グラフ用。
def make_category_chart(household, month, owner=None):

    expense_filter = {
        "household": household,
        "billing_month": month,
    }

    bank_filter = {
        "household": household,
        "billing_month": month,
    }

    if owner:
        expense_filter["owner"] = owner
        bank_filter["owner"] = owner

    expense_data = Expense.objects.filter(
        **expense_filter
    ).values(
        "used_date",
        "amount",
        "category",
        "owner__username",
    )

    bank_data = (
        Bank.objects.filter(
            **bank_filter
        )
        .exclude(
            category__in=[
                "カード引き落とし",
                "送金",
                "入金",
                "給料",
                "サービス(還元など)",
                "その他",
                "未分類",
            ]
        )
        .values(
            "used_date",
            "amount",
            "category",
            "owner__username",
        )
    )

    expense_df = pd.DataFrame(
        expense_data,
        columns=[
            "used_date",
            "amount",
            "category",
            "owner__username",
        ],
    )

    bank_df = pd.DataFrame(
        bank_data,
        columns=[
            "used_date",
            "amount",
            "category",
            "owner__username",
        ],
    )

    if not bank_df.empty:
        bank_df = bank_df[
            bank_df["amount"] < 0
        ].copy()

        bank_df["amount"] = (
            bank_df["amount"].abs()
        )

    all_df = pd.concat(
        [expense_df, bank_df],
        ignore_index=True,
    )

    if all_df.empty:
        return {
            "labels": [],
            "values": [],
            "detail_labels": [],
            "detail_values": [],
            "owner_labels": [],
            "owner_values": [],
        }

    all_df["category_group"] = (
        all_df["category"]
        .map(CATEGORY_GROUP)
        .fillna("その他")
    )

    category_df = (
        all_df
        .groupby("category_group")["amount"]
        .sum()
        .reset_index()
    )

    detail_category_df = (
        all_df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values(
            "amount",
            ascending=False,
        )
    )

    owner_df = (
        all_df
        .groupby("owner__username")["amount"]
        .sum()
        .reset_index()
    )

    return {
        "labels":
            category_df["category_group"].tolist(),

        "values":
            category_df["amount"].tolist(),

        "detail_labels":
            detail_category_df["category"].tolist(),

        "detail_values":
            detail_category_df["amount"].tolist(),

        "owner_labels":
            owner_df["owner__username"].tolist(),

        "owner_values":
            owner_df["amount"].tolist(),
    }

#支出推移。
def make_expense_trend_chart(
    household,
    owner=None,
):

    bank_filter = {
        "household": household,
        "category__in": [
            "現金引き出し",
            "国保・住民税・年金類",
            "娯楽・趣味",
            "家賃",
            "NISA",
            "カード引き落とし",
            "家具家電・設備",
            "保険（家や生命など）",
            "日用品",
            "衣類",
        ],
    }

    if owner:
        bank_filter["owner"] = owner

    sisyutu_data = Bank.objects.filter(
        **bank_filter
    ).values(
        "billing_month",
        "amount",
        "category",
    )

    sisyutu_df = pd.DataFrame(
        sisyutu_data,
        columns=[
            "billing_month",
            "amount",
            "category",
        ],
    )

    if sisyutu_df.empty:
        return {
            "labels": [],
            "values": [],
        }

    sisyutu_df = sisyutu_df[
        sisyutu_df["amount"] < 0
    ].copy()

    sisyutu_df["amount"] = (
        sisyutu_df["amount"].abs()
    )

    monthly_df = (
        sisyutu_df
        .groupby("billing_month")["amount"]
        .sum()
        .reset_index()
        .sort_values("billing_month")
    )

    return {
        "labels":
            monthly_df["billing_month"].tolist(),

        "values":
            monthly_df["amount"].tolist(),
    }

#食費推移。
def make_food_chart(
    household,
    owner=None,
):

    expense_filter = {
        "household": household,
        "category__in": [
            "食費(外食)",
            "食費(自炊)",
        ],
    }

    bank_filter = {
        "household": household,
        "category__in": [
            "食費(外食)",
            "食費(自炊)",
        ],
    }

    if owner:
        expense_filter["owner"] = owner
        bank_filter["owner"] = owner

    food_expense_data = (
        Expense.objects.filter(
            **expense_filter
        )
        .values(
            "billing_month",
            "amount",
            "category",
        )
    )

    food_bank_data = (
        Bank.objects.filter(
            **bank_filter
        )
        .values(
            "billing_month",
            "amount",
            "category",
        )
    )

    food_expense_df = pd.DataFrame(
        food_expense_data,
        columns=[
            "billing_month",
            "amount",
            "category",
        ],
    )

    food_bank_df = pd.DataFrame(
        food_bank_data,
        columns=[
            "billing_month",
            "amount",
            "category",
        ],
    )

    if not food_bank_df.empty:
        food_bank_df = food_bank_df[
            food_bank_df["amount"] < 0
        ].copy()

        food_bank_df["amount"] = (
            food_bank_df["amount"].abs()
        )

    food_df = pd.concat(
        [
            food_expense_df,
            food_bank_df,
        ],
        ignore_index=True,
    )

    if food_df.empty:
        return {
            "labels": [],
            "out_values": [],
            "home_values": [],
        }

    food_monthly_df = (
        food_df
        .groupby(
            [
                "billing_month",
                "category",
            ]
        )["amount"]
        .sum()
        .reset_index()
    )

    food_pivot = (
        food_monthly_df
        .pivot(
            index="billing_month",
            columns="category",
            values="amount",
        )
        .fillna(0)
        .sort_index()
    )

    labels = food_pivot.index.tolist()

    out_values = (
        food_pivot.get(
            "食費(外食)",
            pd.Series(
                0,
                index=food_pivot.index,
            ),
        )
        .tolist()
    )

    home_values = (
        food_pivot.get(
            "食費(自炊)",
            pd.Series(
                0,
                index=food_pivot.index,
            ),
        )
        .tolist()
    )

    return {
        "labels": labels,
        "out_values": out_values,
        "home_values": home_values,
    }

# 月間収支。
def make_profit_chart(
    household,
    owner=None,
):

    income_filter = {
        "household": household,
        "amount__gt": 0,
        "category__in": [
            "給料",
            "サービス(還元など)",
        ],
    }

    bank_expense_filter = {
        "household": household,
        "amount__lt": 0,
    }

    card_expense_filter = {
        "household": household,
    }

    if owner:
        income_filter["owner"] = owner
        bank_expense_filter["owner"] = owner
        card_expense_filter["owner"] = owner

    income_data = (
        Bank.objects.filter(
            **income_filter
        )
        .values(
            "billing_month",
            "amount",
        )
    )

    expense_bank_data = (
        Bank.objects.filter(
            **bank_expense_filter
        )
        .exclude(
            category__in=[
                "給料",
                "サービス(還元など)",
                "NISA",
                "送金",
                "入金",
                "カード引き落とし",
            ]
        )
        .values(
            "billing_month",
            "amount",
        )
    )

    expense_card_data = (
        Expense.objects.filter(
            **card_expense_filter
        )
        .exclude(
            category__in=[
                "NISA",
            ]
        )
        .values(
            "billing_month",
            "amount",
        )
    )

    income_df = pd.DataFrame(
        income_data,
        columns=[
            "billing_month",
            "amount",
        ],
    )

    expense_bank_df = pd.DataFrame(
        expense_bank_data,
        columns=[
            "billing_month",
            "amount",
        ],
    )

    expense_card_df = pd.DataFrame(
        expense_card_data,
        columns=[
            "billing_month",
            "amount",
        ],
    )

    if not expense_bank_df.empty:
        expense_bank_df["amount"] = (
            expense_bank_df["amount"].abs()
        )

    if not expense_card_df.empty:
        expense_card_df["amount"] = (
            expense_card_df["amount"].abs()
        )

    expense_df = pd.concat(
        [
            expense_bank_df,
            expense_card_df,
        ],
        ignore_index=True,
    )

    if income_df.empty:
        income_monthly = pd.Series(
            dtype="float64"
        )
    else:
        income_monthly = (
            income_df
            .groupby("billing_month")["amount"]
            .sum()
        )

    if expense_df.empty:
        expense_monthly = pd.Series(
            dtype="float64"
        )
    else:
        expense_monthly = (
            expense_df
            .groupby("billing_month")["amount"]
            .sum()
        )

    profit_df = pd.concat(
        [
            income_monthly,
            expense_monthly,
        ],
        axis=1,
        keys=[
            "income",
            "expense",
        ],
    ).fillna(0)

    if profit_df.empty:
        return {
            "labels": [],
            "income_values": [],
            "expense_values": [],
            "profit_values": [],
        }

    profit_df = profit_df.sort_index()

    profit_df["profit"] = (
        profit_df["income"]
        - profit_df["expense"]
    )

    return {
        "labels":
            profit_df.index.tolist(),

        "income_values":
            profit_df["income"].tolist(),

        "expense_values":
            profit_df["expense"].tolist(),

        "profit_values":
            profit_df["profit"].tolist(),
    }