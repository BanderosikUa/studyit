from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from topics.models import Category, Topic
from trainer.models import TrainerAnswer, TrainerSession


def create_test_user(*, email: str = "user@example.com", password: str = "pass1234") -> User:
    user = User(email=email)
    user.set_password(password)
    user.save()
    return user


class SessionCreateApiTests(APITestCase):
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
            for index in range(1, 3)
        ]

    def test_creates_session_for_requested_category(self):
        response = self.client.post(
            reverse("session-create"),
            data={
                "category": self.category.slug,
                "total_questions": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_questions"], 2)
        self.assertEqual(response.data["category_slug"], self.category.slug)
        self.assertFalse(response.data["completed"])

        session = TrainerSession.objects.get(id=response.data["id"])
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.category, self.category)
        self.assertEqual(TrainerAnswer.objects.filter(session=session).count(), 2)


class SessionDetailApiTests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Python", slug="python", order=1)
        self.topic_1 = Topic.objects.create(
            category=self.category,
            title="Question 1",
            question_id=101,
            index=1,
        )
        self.topic_2 = Topic.objects.create(
            category=self.category,
            title="Question 2",
            question_id=102,
            index=2,
        )
        self.session = TrainerSession.objects.create(
            user=self.user,
            category=self.category,
            total_questions=2,
            completed=False,
        )
        TrainerAnswer.objects.create(
            session=self.session,
            topic=self.topic_2,
            user_answer="Second answer",
            self_score=4,
        )
        TrainerAnswer.objects.create(
            session=self.session,
            topic=self.topic_1,
            user_answer="First answer",
            self_score=None,
        )

    def test_returns_nested_questions(self):
        response = self.client.get(
            reverse("session-detail", kwargs={"session_id": self.session.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.session.id)
        self.assertEqual(response.data["total_questions"], 2)
        self.assertEqual(response.data["category_slug"], self.category.slug)
        self.assertFalse(response.data["completed"])
        self.assertEqual(
            response.data["questions"],
            [
                {
                    "topic_id": self.topic_2.id,
                    "title": self.topic_2.title,
                    "user_answer": "Second answer",
                    "self_score": 4,
                },
                {
                    "topic_id": self.topic_1.id,
                    "title": self.topic_1.title,
                    "user_answer": "First answer",
                    "self_score": None,
                },
            ],
        )
