from django.urls import path
from . import views

app_name = "expense"

urlpatterns = [
    path(
        "upload/",
        views.csv_upload,
        name="csv_upload",
    ),
    path(
        "ginkou_upload/",
        views.ginkou_upload,
        name="ginkou_upload"

    ),
    path(
        "nisa_upload/",
        views.nisa_create,
        name="nisa_upload"
    ),
    
    path("", views.expense_index, name="expense_index"),#ログインした後の遷移先用

    path(
    "<str:month>/",#これで/expense/2026-07/ /expense/2026-08/が使える
    views.expense_month,
    name="expense_month"
    ),
    path(
        "<int:pk>/expense_category/",#<int:pk>は編集する明細のID。たとえばIDが3なら、http://127.0.0.1:8000/expense/3/category/になる。
        views.expense_category_update,
        name="expense_category_update",
    ),
    path(
        "<int:pk>/ginkou_category/",#<int:pk>は編集する明細のID。たとえばIDが3なら、http://127.0.0.1:8000/expense/3/category/になる。
        views.ginkou_category_update,
        name="ginkou_category_update",
    ),
    path(
        "<int:pk>/expense_category/expense_delete",#<int:pk>は編集する明細のID。たとえばIDが3なら、http://127.0.0.1:8000/expense/3/category/になる。
        views.expense_delete,
        name="expense_delete",
    ),
    path(
        "<int:pk>/rakuten_category/ginkou_delete",#<int:pk>は編集する明細のID。たとえばIDが3なら、http://127.0.0.1:8000/expense/3/category/になる。
        views.ginkou_delete,
        name="ginkou_delete",
    ),
    path(
        "expense/bulk-save-rules/",
        views.bulk_save_rules,
        name="bulk_save_rules",
    ),
    path(
            "expense/bank_bulk-save-rules/",
            views.bank_bulk_save_rules,
            name="bank_bulk_save_rules",
    ),
]