from django.urls import path

from topics.progress_apis import (
    ProgressExportApi,
    ProgressImportApi,
    ProgressStatsApi,
)

urlpatterns = [
    path("export/", ProgressExportApi.as_view(), name="export"),
    path("import/", ProgressImportApi.as_view(), name="import"),
    path("stats/", ProgressStatsApi.as_view(), name="stats"),
]
