from django.contrib.auth.views import LoginView,LogoutView
from django.urls import path

#コマンド上：python manage.py startapp accounts

app_name = "accounts"
urlpatterns = [
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
]