"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("expense/", include("expense.urls")),
    path('accounts/',include('accounts.urls')),
    path('',include('django.contrib.auth.urls')),#djangoがもともと持ってるauthと呼ばれる認証機能を呼び出す
    #expense.urls は、expenseアプリの中にある urls.py につながる。続きは expense/urls.py に任せるという意味です。たとえば expense/urls.py がこうなら、path("", views.expense_list, name="expense_list"),
#URLの流れはこうなります。http://127.0.0.1:8000/expense/ 最後にviews.expense_listが実行されます。流れを一本で書くと、ブラウザ↓ myproject/urls.py↓ expense/urls.py ↓ expense/views.py の expense_list ↓expense_list.html
]
