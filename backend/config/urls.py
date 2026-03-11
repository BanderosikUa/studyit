from django.contrib import admin
from django.urls import include, path

from topics.urls import progress_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/topics/", include("topics.urls")),
    path("api/trainer/", include("trainer.urls")),
    path("api/progress/", include((progress_patterns, "progress"))),
]
