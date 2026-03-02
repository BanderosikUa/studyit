from django.conf import settings
from django.db import models

from core.models import BaseModel


class TrainerSession(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_sessions",
    )
    category = models.ForeignKey(
        "topics.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trainer_sessions",
    )
    total_questions = models.IntegerField()
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = "trainer_trainersession"

    def __str__(self):
        return f"Session {self.id} by {self.user_id}"


class TrainerAnswer(BaseModel):
    session = models.ForeignKey(
        TrainerSession,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    topic = models.ForeignKey(
        "topics.Topic",
        on_delete=models.CASCADE,
        related_name="trainer_answers",
    )
    user_answer = models.TextField(blank=True)
    self_score = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "trainer_traineranswer"
        unique_together = [("session", "topic")]

    def __str__(self):
        return f"Answer for topic {self.topic_id} in session {self.session_id}"
