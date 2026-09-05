from django.forms import BooleanField,ModelForm #formの基底クラス
from .models import Expense,Bank,Nisa
from django import forms

class BaseCategoryForm(ModelForm):
    save_as_rule = BooleanField(#forms.BooleanField:Djangoフォームの真か偽かを入力する項目。画面上ではチェックボックスになる。□ この店名を今後も選択したカテゴリーに分類する
    label="この店名を今後も選択したカテゴリーに分類する",
    required=False,#このチェックボックスを必須にしない設定。つまり、チェックしなくてもフォームを保存できる。今回の動きは、チェックなし→ 今回の明細だけカテゴリー変更
# チェックあり→ 今回の明細を変更→ 今後の分類ルールとしても保存
    )
    class Meta:
        # model = Expense #どのモデルのデータを編集するか指定している。
        fields = ["category"]

# ==========================================
# クレジットカード用カテゴリー編集フォーム
# ==========================================
class ExpenseCategoryForm(BaseCategoryForm):
    class Meta(BaseCategoryForm.Meta):
        model = Expense
#BaseCategoryFormの内容を引き継いで、保存先だけExpenseにする

# ==========================================
# 楽天銀行用カテゴリー編集フォーム
# ==========================================
class BankCategoryForm(BaseCategoryForm):
    class Meta(BaseCategoryForm.Meta):
        model = Bank




class CsvUploadForm_Expense(forms.Form):#CsvUploadFormはモデルと直接結びつかない（編集しない）ので、ModelFormではなく、forms.Formを使ってる。今回は、
#CSVファイルを選ぶ,対象月を入力するためのフォームだから、forms.Formを使う。

    csv_file = forms.FileField(#これは、フォームにファイル選択欄を作る。
        label="CSVファイル"
    )

    billing_month = forms.CharField(
        label="対象月",
        max_length=7,
        help_text="例：2026-08",
    )


class CsvUploadForm_Bank(forms.Form):#CsvUploadFormはモデルと直接結びつかない（編集しない）ので、ModelFormではなく、forms.Formを使ってる。今回は、
#CSVファイルを選ぶ,対象月を入力するためのフォームだから、forms.Formを使う。

    bank_choice = forms.ChoiceField(
        label="銀行",
        choices=Bank.BANK_CHOICES,
    )

    csv_file = forms.FileField(#これは、フォームにファイル選択欄を作る。
        label="CSVファイル"
    )

    billing_month = forms.CharField(
        label="対象月",
        max_length=7,
        help_text="例：2026-08",
    )

class NisaUploadForm(ModelForm):
    class Meta:
        model = Nisa
        fields = ["value"]
        lebels = {"value":"NISA評価額"}

    