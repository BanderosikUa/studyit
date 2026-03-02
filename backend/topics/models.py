from django.conf import settings
from django.db import models

from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "topics_category"
        ordering = ["order", "slug"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Topic(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="topics"
    )
    title = models.CharField(max_length=500)
    question_id = models.IntegerField(unique=True)
    index = models.IntegerField(default=0)
    source_url = models.URLField(blank=True, max_length=500)
    short_answer = models.TextField(blank=True)
    detailed_explanation = models.TextField(blank=True)
    raw_markdown = models.TextField(blank=True)

    class Meta:
        db_table = "topics_topic"
        ordering = ["index", "question_id"]

    def __str__(self):
        return self.title


class UserTopicStatus(BaseModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        STUDIED = "studied", "Studied"
        REVIEW = "review", "Needs review"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic_statuses",
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="user_statuses"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW
    )

    class Meta:
        db_table = "topics_usertopicstatus"
        unique_together = [("user", "topic")]
        verbose_name_plural = "User topic statuses"

    def __str__(self):
        return f"{self.user_id} - {self.topic_id}: {self.status}"


class Note(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic_notes",
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="notes"
    )
    text = models.TextField()

    class Meta:
        db_table = "topics_note"

    def __str__(self):
        return f"Note on {self.topic_id} by {self.user_id}"
