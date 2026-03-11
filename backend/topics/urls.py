from django.urls import path

from topics.apis import (
    CategoryListApi,
    NoteDeleteApi,
    NoteListApi,
    NoteUpdateApi,
    ProgressExportApi,
    ProgressImportApi,
    ProgressStatsApi,
    TopicDetailApi,
    TopicListApi,
    TopicStatusUpdateApi,
)

progress_patterns = [
    path("export/", ProgressExportApi.as_view(), name="export"),
    path("import/", ProgressImportApi.as_view(), name="import"),
    path("stats/", ProgressStatsApi.as_view(), name="stats"),
]

urlpatterns = [
    path("categories/", CategoryListApi.as_view(), name="categories"),
    path("", TopicListApi.as_view(), name="list"),
    path("<int:topic_id>/", TopicDetailApi.as_view(), name="detail"),
    path("<int:topic_id>/status/", TopicStatusUpdateApi.as_view(), name="status"),
    path("<int:topic_id>/notes/", NoteListApi.as_view(), name="note-list"),
    path("notes/<int:note_id>/", NoteUpdateApi.as_view(), name="note-update"),
    path("notes/<int:note_id>/delete/", NoteDeleteApi.as_view(), name="note-delete"),
]
