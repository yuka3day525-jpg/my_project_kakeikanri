from django.contrib import admin
from .models import Expense,ExpenseCategoryRule,BankCategoryRule,Bank,Household,Nisa

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "used_date",
        "store_name",
        "amount",
        "category",
        "classification_method"
    )

@admin.register(ExpenseCategoryRule)
class CategoryRuleAdmin(admin.ModelAdmin):
    list_display = (
        "keyword",
        "category",
    )

@admin.register(BankCategoryRule)
class CategoryRuleAdmin(admin.ModelAdmin):
    list_display = (
        "keyword",
        "category",
    )

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "bank",
        "used_date",
        "amount",
        "zankin",
        "store_name",
        "category",
        "classification_method",
    )

@admin.register(Nisa)
class NisaAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "value",
        "recorded_date"
    )

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("id","name")
    #ID      Name
    # 1     ふたりの家計
    # 2     自分だけの家計
    filter_horizontal = ("members",)
    #を指定すると、Admin画面でこんな感じの左右2つのボックスになります。
# 利用可能なユーザー        選択されたユーザー
# □ user3                    □ あなた
# □ user4                    □ 彼氏
# □ user5
# ユーザーを選んで、矢印で右側に移動できます。
# つまりHouseholdに所属するユーザー（members）を、Admin画面で選びやすくするための設定
