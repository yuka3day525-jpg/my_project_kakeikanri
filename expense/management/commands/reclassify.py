from django.core.management.base import BaseCommand

from expense.models import Expense, Bank
from expense.utils import classify_category, classify_bank_category


class Command(BaseCommand):
    help = "未分類の既存明細をカテゴリー再分類します"
    def handle(self, *args, **options):

        # ==========================================
        # 楽天カードの未分類データを再分類
        # ==========================================
        expenses = Expense.objects.filter(
            category="未分類"
        )

        expense_count = 0

        for expense in expenses:

            new_category = classify_category(
                expense.store_name,expense.household,

            )

            # 再分類しても未分類のままなら更新しない
            if new_category == "未分類":
                continue

            expense.category = new_category
            expense.save()

            expense_count += 1


        # ==========================================
        # 銀行の未分類データを再分類
        # ==========================================
        banks = Bank.objects.filter(
            category="未分類"
        )

        bank_count = 0

        for bank in banks:

            new_category = classify_bank_category(
                bank.store_name,bank.household,
            )

            # 再分類しても未分類のままなら更新しない
            if new_category == "未分類":
                continue

            bank.category = new_category
            bank.save()

            bank_count += 1


        # ==========================================
        # 結果表示
        # ==========================================
        self.stdout.write(
            self.style.SUCCESS(
                f"再分類完了："
                f"楽天カード {expense_count}件、"
                f"銀行 {bank_count}件を更新しました"
            )
        )