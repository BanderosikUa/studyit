from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from topics.models import Category, Note, Topic, UserTopicStatus
from trainer.models import TrainerAnswer, TrainerSession


def create_test_user(*, email: str = "user@example.com", password: str = "pass1234") -> User:
    user = User(email=email)
    user.set_password(password)
    user.save()
    return user


class ProgressExportApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)

    def test_returns_export_payload_with_serialized_dates(self):
        category = Category.objects.create(name="Python", slug="python", order=1)
        topic = Topic.objects.create(
            category=category,
            title="Question",
            question_id=101,
            index=1,
        )
        UserTopicStatus.objects.create(
            user=self.user,
            topic=topic,
            status=UserTopicStatus.Status.STUDIED,
        )
        Note.objects.create(user=self.user, topic=topic, text="Remember this")
        session = TrainerSession.objects.create(
            user=self.user,
            category=category,
            total_questions=1,
            completed=True,
        )
        session.created_at = timezone.make_aware(datetime(2026, 1, 2, 3, 4, 5))
        session.save(update_fields=["created_at"])
        TrainerAnswer.objects.create(
            session=session,
            topic=topic,
            user_answer="Answer",
            self_score=4,
        )

        response = self.client.get(reverse("progress:export"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.email)
        self.assertIsInstance(response.data["exported_at"], str)
        self.assertEqual(
            response.data["statuses"],
            [
                {
                    "question_id": topic.question_id,
                    "status": UserTopicStatus.Status.STUDIED,
                }
            ],
        )
        self.assertEqual(
            response.data["notes"],
            [{"question_id": topic.question_id, "text": "Remember this"}],
        )
        self.assertEqual(
            response.data["trainer_scores"],
            [
                {
                    "question_id": topic.question_id,
                    "self_score": 4,
                    "session_date": "2026-01-02",
                }
            ],
        )


class ProgressImportApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Python", slug="python", order=1)
        self.topic = Topic.objects.create(
            category=self.category,
            title="Question",
            question_id=101,
            index=1,
        )

    def test_imports_statuses_and_replaces_notes(self):
        Note.objects.create(user=self.user, topic=self.topic, text="Old note")

        response = self.client.post(
            reverse("progress:import"),
            data={
                "statuses": [
                    {
                        "question_id": self.topic.question_id,
                        "status": UserTopicStatus.Status.REVIEW,
                    }
                ],
                "notes": [
                    {
                        "question_id": self.topic.question_id,
                        "text": "Fresh note",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            UserTopicStatus.objects.get(user=self.user, topic=self.topic).status,
            UserTopicStatus.Status.REVIEW,
        )
        self.assertEqual(
            list(
                Note.objects.filter(user=self.user, topic=self.topic).values_list(
                    "text",
                    flat=True,
                )
            ),
            ["Fresh note"],
        )

    def test_rejects_non_object_payload(self):
        response = self.client.post(
            reverse("progress:import"),
            data=[],
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "Invalid JSON", "extra": {}},
        )


class TopicStatusUpdateApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Python", slug="python", order=1)
        self.topic = Topic.objects.create(
            category=self.category,
            title="Question",
            question_id=101,
            index=1,
        )

    def test_updates_topic_status(self):
        response = self.client.post(
            reverse("status", kwargs={"topic_id": self.topic.id}),
            data={"status": UserTopicStatus.Status.REVIEW},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            UserTopicStatus.objects.get(user=self.user, topic=self.topic).status,
            UserTopicStatus.Status.REVIEW,
        )


class TopicListApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Python", slug="python", order=1)
        self.topics = [
            Topic.objects.create(
                category=self.category,
                title=f"Question {index}",
                question_id=100 + index,
                index=index,
            )
            for index in range(1, 4)
        ]
        UserTopicStatus.objects.create(
            user=self.user,
            topic=self.topics[1],
            status=UserTopicStatus.Status.REVIEW,
        )

    def test_returns_limit_offset_paginated_response(self):
        response = self.client.get(
            reverse("list"),
            data={"limit": 2, "offset": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["limit"], 2)
        self.assertEqual(response.data["offset"], 1)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["previous"], "http://testserver/api/topics/?limit=2")
        self.assertEqual(response.data["next"], None)
        self.assertEqual(
            [item["id"] for item in response.data["results"]],
            [self.topics[1].id, self.topics[2].id],
        )
        self.assertEqual(response.data["results"][0]["category_slug"], self.category.slug)
        self.assertEqual(response.data["results"][0]["category_name"], self.category.name)
        self.assertEqual(response.data["results"][0]["status"], UserTopicStatus.Status.REVIEW)
        self.assertEqual(response.data["results"][1]["status"], UserTopicStatus.Status.NEW)


class TopicDetailApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Python", slug="python", order=1)
        self.topic = Topic.objects.create(
            category=self.category,
            title="Question",
            question_id=101,
            index=1,
            short_answer="Short",
            detailed_explanation="Detailed",
            raw_markdown="# Raw",
        )

    def test_returns_annotated_status_and_category_fields(self):
        UserTopicStatus.objects.create(
            user=self.user,
            topic=self.topic,
            status=UserTopicStatus.Status.REVIEW,
        )

        response = self.client.get(
            reverse("detail", kwargs={"topic_id": self.topic.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.topic.id)
        self.assertEqual(response.data["category_slug"], self.category.slug)
        self.assertEqual(response.data["category_name"], self.category.name)
        self.assertEqual(response.data["status"], UserTopicStatus.Status.REVIEW)

    def test_returns_new_status_when_user_has_no_saved_status(self):
        response = self.client.get(
            reverse("detail", kwargs={"topic_id": self.topic.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], UserTopicStatus.Status.NEW)
