from django.urls import path

from accounts.apis import LoginApi, RefreshApi, RegisterApi

urlpatterns = [
    path("register/", RegisterApi.as_view(), name="register"),
    path("login/", LoginApi.as_view(), name="login"),
    path("refresh/", RefreshApi.as_view(), name="refresh"),
]
