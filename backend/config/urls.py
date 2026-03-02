from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/topics/", include("topics.urls")),
    path("api/progress/", include("topics.progress_urls")),
    path("api/trainer/", include("trainer.urls")),
]
