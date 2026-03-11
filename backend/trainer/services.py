from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from accounts.models import User
from topics.models import Category, Topic
from trainer.models import TrainerAnswer, TrainerSession


def trainer_session_create(
    *,
    user: User,
    category_slug: str | None = None,
    total_questions: int,
) -> TrainerSession:
    category = None
    qs = Topic.objects.all().order_by("?")

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        qs = qs.filter(category=category)

    topics = list(qs[:total_questions])
    if len(topics) < total_questions:
        from core.exceptions import ApplicationError

        raise ApplicationError(
            "Not enough topics",
            extra={
                "requested": total_questions,
                "available": len(topics),
            },
        )

    session = TrainerSession.objects.create(
        user=user,
        category=category,
        total_questions=len(topics),
        completed=False,
    )

    for order, topic in enumerate(topics):
        TrainerAnswer.objects.create(
            session=session,
            topic=topic,
            user_answer="",
            self_score=None,
        )
    return session


def trainer_session_get(*, user: User, session_id: int) -> TrainerSession:
    return get_object_or_404(
        TrainerSession.objects.select_related("category").prefetch_related(
            Prefetch(
                "answers",
                queryset=TrainerAnswer.objects.select_related("topic").order_by("id"),
            )
        ),
        pk=session_id,
        user=user,
    )


def trainer_session_submit_answer(
    *,
    user: User,
    session_id: int,
    topic_id: int,
    user_answer: str,
    self_score: int | None = None,
) -> TrainerAnswer:
    session = get_object_or_404(TrainerSession, pk=session_id, user=user)
    answer = get_object_or_404(
        TrainerAnswer,
        session=session,
        topic_id=topic_id,
    )
    answer.user_answer = user_answer

    if self_score is not None and 1 <= self_score <= 5:
        answer.self_score = self_score

    answer.save(update_fields=["user_answer", "self_score", "updated_at"])
    return answer


def trainer_session_generate_prompt(*, user: User, session_id: int) -> str:
    session = trainer_session_get(user=user, session_id=session_id)
    lines = [
        "Ти — інтерв'юер, який оцінює знання кандидата з Python/Backend.",
        "Нижче наведені питання та відповіді кандидата.",
        "",
        "Для кожної відповіді:",
        "1. Оціни від 1 до 10",
        "2. Поясни, що було правильно і що пропущено",
        "3. Дай коротку рекомендацію",
        "",
    ]

    for i, answer in enumerate(
        session.answers.select_related("topic").order_by("id"), 1
    ):
        lines.append(f"Питання {i}: {answer.topic.title}")
        lines.append(f"Відповідь кандидата: {answer.user_answer or '(порожньо)'}")
        lines.append("")

    lines.extend(
        [
            "В кінці:",
            "- Дай загальний бал від 1 до 10",
            "- Перелічи теми, які потребують додаткового вивчення",
            "- Дай рекомендації щодо підготовки",
        ]
    )
    return "\n".join(lines)
