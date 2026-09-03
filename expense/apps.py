from django.apps import AppConfig


class ExpenseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField" #これは、モデルに主キーを自分で書かなかったときに、Djangoが自動で作るidの種類を指定してる。BigAutoFieldは、その番号にかなり大きな数まで使える型という意味。
    name = 'expense'
