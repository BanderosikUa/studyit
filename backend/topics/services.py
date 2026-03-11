from typing import Any

from django.db.models import CharField, Count, Exists, OuterRef, Q, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import User
from core.exceptions import ApplicationError
from topics.models import Category, Note, Topic, UserTopicStatus
from trainer.models import TrainerAnswer


def _topics_with_user_status(*, user: User) -> QuerySet[Topic]:
    user_status = UserTopicStatus.objects.filter(
        topic=OuterRef("pk"),
        user=user,
    ).values("status")[:1]
    return Topic.objects.select_related("category").annotate(
        status=Coalesce(
            Subquery(user_status),
            Value(UserTopicStatus.Status.NEW),
            output_field=CharField(),
        )
    )


def category_list_with_progress(*, user: User) -> list[dict]:
    categories = Category.objects.annotate(total=Count("topics")).order_by(
        "order", "slug"
    )

    status_counts = (
        UserTopicStatus.objects.filter(user=user)
        .values("topic__category_id", "status")
        .annotate(cnt=Count("id"))
    )

    by_cat = {}
    for row in status_counts:
        cid = row["topic__category_id"]

        if cid not in by_cat:
            by_cat[cid] = {value: 0 for value in UserTopicStatus.Status.values}

        by_cat[cid][row["status"]] = row["cnt"]

    result_by_slug: dict[str, dict] = {}

    for cat in categories:
        counts = by_cat.get(
            cat.id, {value: 0 for value in UserTopicStatus.Status.values}
        )
        slug = cat.slug
        name = cat.name

        if slug not in result_by_slug:
            result_by_slug[slug] = {
                "id": cat.id,
                "name": name,
                "slug": slug,
                "order": cat.order,
                "total_topics": 0,
                "studied_count": 0,
                "review_count": 0,
                "new_count": 0,
            }
        else:
            result_by_slug[slug]["id"] = cat.id
            result_by_slug[slug]["name"] = name

        result_by_slug[slug]["order"] = min(result_by_slug[slug]["order"], cat.order)
        result_by_slug[slug]["total_topics"] += cat.total or 0
        result_by_slug[slug]["studied_count"] += counts[UserTopicStatus.Status.STUDIED]
        result_by_slug[slug]["review_count"] += counts[UserTopicStatus.Status.REVIEW]

    result = list(result_by_slug.values())

    for item in result:
        new_count = item["total_topics"] - item["studied_count"] - item["review_count"]
        item["new_count"] = max(0, new_count)

    result.sort(key=lambda x: (x["order"], x["slug"]))
    return result


def topic_list(
    *,
    user: User,
    category_slug: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
) -> QuerySet[Topic]:
    user_status = UserTopicStatus.objects.filter(topic=OuterRef("pk"), user=user).values(
        "status"
    )[:1]
    qs = _topics_with_user_status(user=user)
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if search:
        search = search.strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(short_answer__icontains=search)
                | Q(detailed_explanation__icontains=search)
                | Q(raw_markdown__icontains=search)
            )

    if status_filter == UserTopicStatus.Status.NEW:
        no_status = ~Exists(
            UserTopicStatus.objects.filter(topic=OuterRef("pk"), user=user)
        )
        has_new = Q(
            user_statuses__user=user,
            user_statuses__status=UserTopicStatus.Status.NEW,
        )
        qs = qs.filter(no_status | has_new)

    elif status_filter and status_filter in (
        UserTopicStatus.Status.STUDIED,
        UserTopicStatus.Status.REVIEW,
    ):
        qs = qs.filter(
            user_statuses__user=user,
            user_statuses__status=status_filter,
        )

    qs = qs.distinct().order_by("index", "question_id")
    return qs


def topic_get(*, user: User, topic_id: int) -> Topic:
    return get_object_or_404(
        _topics_with_user_status(user=user),
        pk=topic_id,
    )


def topic_status_update(
    *, user: User, topic_id: int, status: str
) -> UserTopicStatus:
    topic = get_object_or_404(Topic, pk=topic_id)

    try:
        normalized_status = UserTopicStatus.Status(status)
    except ValueError as exc:
        raise ApplicationError("Invalid status", extra={"status": status}) from exc

    obj, _ = UserTopicStatus.objects.update_or_create(
        user=user,
        topic=topic,
        defaults={"status": normalized_status},
    )
    return obj


def note_list(*, user: User, topic_id: int) -> QuerySet[Note]:
    return Note.objects.filter(
        user=user,
        topic_id=topic_id,
    ).order_by("created_at")


def note_create(*, user: User, topic_id: int, text: str) -> Note:
    topic = get_object_or_404(Topic, pk=topic_id)
    note = Note(user=user, topic=topic, text=text)
    note.full_clean()
    note.save()
    return note


def note_update(*, user: User, note_id: int, text: str) -> Note:
    note = get_object_or_404(Note, pk=note_id, user=user)
    note.text = text
    note.full_clean()
    note.save(update_fields=["text", "updated_at"])
    return note


def note_delete(*, user: User, note_id: int) -> None:
    note = get_object_or_404(Note, pk=note_id, user=user)
    note.delete()


def progress_export(*, user: User) -> dict[str, Any]:
    statuses = UserTopicStatus.objects.filter(user=user).select_related("topic")
    notes = Note.objects.filter(user=user).select_related("topic")
    answers = TrainerAnswer.objects.filter(session__user=user).select_related(
        "topic", "session"
    )
    return {
        "exported_at": timezone.now(),
        "user": user.email,
        "statuses": [
            {"question_id": s.topic.question_id, "status": s.status} for s in statuses
        ],
        "notes": [{"question_id": n.topic.question_id, "text": n.text} for n in notes],
        "trainer_scores": [
            {
                "question_id": a.topic.question_id,
                "self_score": a.self_score,
                "session_date": a.session.created_at.date(),
            }
            for a in answers
            if a.self_score is not None
        ],
    }


def progress_import(*, user: User, data: dict) -> None:
    statuses = data.get("statuses") or []
    notes_data = data.get("notes") or []
    topic_by_qid = {
        t.question_id: t
        for t in Topic.objects.filter(
            question_id__in=set(
                [s["question_id"] for s in statuses]
                + [n["question_id"] for n in notes_data]
            )
        )
    }
    for item in statuses:
        qid = item.get("question_id")
        status_val = item.get("status")

        if qid is None or status_val not in UserTopicStatus.Status.values:
            continue

        topic = topic_by_qid.get(qid)

        if not topic:
            continue

        UserTopicStatus.objects.update_or_create(
            user=user,
            topic=topic,
            defaults={"status": status_val},
        )

    notes_by_qid = {}
    for item in notes_data:
        qid = item.get("question_id")
        text = item.get("text", "")

        if qid is None:
            continue

        notes_by_qid.setdefault(qid, []).append(text)

    for qid, texts in notes_by_qid.items():
        topic = topic_by_qid.get(qid)

        if not topic:
            continue

        Note.objects.filter(user=user, topic=topic).delete()

        for text in texts:
            Note.objects.create(user=user, topic=topic, text=text)


def progress_stats(*, user: User) -> list[dict]:
    return category_list_with_progress(user=user)
