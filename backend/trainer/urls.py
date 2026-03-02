from django.urls import path

from trainer.apis import (
    SessionAnswerApi,
    SessionCreateApi,
    SessionDetailApi,
    SessionPromptApi,
)

urlpatterns = [
    path("sessions/", SessionCreateApi.as_view(), name="session-create"),
    path(
        "sessions/<int:session_id>/",
        SessionDetailApi.as_view(),
        name="session-detail",
    ),
    path(
        "sessions/<int:session_id>/answer/",
        SessionAnswerApi.as_view(),
        name="session-answer",
    ),
    path(
        "sessions/<int:session_id>/prompt/",
        SessionPromptApi.as_view(),
        name="session-prompt",
    ),
]
