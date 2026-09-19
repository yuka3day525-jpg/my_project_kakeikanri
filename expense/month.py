from collections import defaultdict

from django.utils import timezone

from .models import Expense


def get_month_navigation(household):

    # 現在の西暦
    current_year = timezone.localdate().year

    # 家計に登録されている月を取得
    month_list = (
        Expense.objects.filter(
            household=household
        )
        .values_list(
            "billing_month",
            flat=True
        )
        .distinct()
        .order_by("-billing_month")
    )

    # 今年の月
    current_months = []

    # 過去年度
    past_years = defaultdict(list)

    for month in month_list:

        year, month_number = map(
            int,
            month.split("-")
        )

        month_data = {
            "value": month,
            "label": f"{month_number}月"
        }

        if year == current_year:

            current_months.append(
                month_data
            )

        elif year < current_year:

            past_years[year].append(
                month_data
            )

    # 年度の新しい順に並べる
    past_years = dict(
        sorted(
            past_years.items(),
            reverse=True
        )
    )

    return current_months, past_years

# [
#     {"value": "2026-08", "label": "8月"},
#     {"value": "2026-07", "label": "7月"},
#     {"value": "2026-06", "label": "6月"},
# ]