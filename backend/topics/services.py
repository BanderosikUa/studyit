from django.db.models import Count, Exists, OuterRef, Q, QuerySet
from django.shortcuts import get_object_or_404

from topics.models import Category, Note, Topic, UserTopicStatus


def category_list_with_progress(*, user) -> list[dict]:
    categories = Category.objects.annotate(
        total=Count("topics")
    ).order_by("order", "slug")
    status_counts = (
        UserTopicStatus.objects.filter(user=user)
        .values("topic__category_id", "status")
        .annotate(cnt=Count("id"))
    )
    by_cat = {}
    for row in status_counts:
        cid = row["topic__category_id"]
        if cid not in by_cat:
            by_cat[cid] = {"new": 0, "studied": 0, "review": 0}
        by_cat[cid][row["status"]] = row["cnt"]
    result = []
    for cat in categories:
        counts = by_cat.get(cat.id, {"new": 0, "studied": 0, "review": 0})
        studied = counts["studied"]
        review = counts["review"]
        total = cat.total or 0
        new_count = max(0, total - studied - review)
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "order": cat.order,
            "total_topics": total,
            "studied_count": studied,
            "review_count": review,
            "new_count": new_count,
        })
    return result


def topic_list(
    *,
    user,
    category_slug: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
) -> QuerySet[Topic]:
    qs = Topic.objects.select_related("category").all()
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if search:
        qs = qs.filter(title__icontains=search)
    if status_filter == "new":
        no_status = ~Exists(
            UserTopicStatus.objects.filter(
                topic=OuterRef("pk"), user=user
            )
        )
        has_new = Q(
            user_statuses__user=user,
            user_statuses__status="new",
        )
        qs = qs.filter(no_status | has_new)
    elif status_filter and status_filter in ("studied", "review"):
        qs = qs.filter(
            user_statuses__user=user,
            user_statuses__status=status_filter,
        )
    qs = qs.distinct().order_by("index", "question_id")
    return qs


def topic_get(*, topic_id: int):
    return get_object_or_404(
        Topic.objects.select_related("category"),
        pk=topic_id,
    )


def topic_status_update(*, user, topic_id: int, status: str) -> UserTopicStatus:
    topic = get_object_or_404(Topic, pk=topic_id)
    if status not in ("new", "studied", "review"):
        from core.exceptions import ApplicationError
        raise ApplicationError("Invalid status", extra={"status": status})
    obj, _ = UserTopicStatus.objects.update_or_create(
        user=user,
        topic=topic,
        defaults={"status": status},
    )
    return obj


def note_list(*, user, topic_id: int) -> QuerySet[Note]:
    return Note.objects.filter(
        user=user,
        topic_id=topic_id,
    ).order_by("created_at")


def note_create(*, user, topic_id: int, text: str) -> Note:
    topic = get_object_or_404(Topic, pk=topic_id)
    note = Note(user=user, topic=topic, text=text)
    note.full_clean()
    note.save()
    return note


def note_update(*, user, note_id: int, text: str) -> Note:
    note = get_object_or_404(Note, pk=note_id, user=user)
    note.text = text
    note.full_clean()
    note.save(update_fields=["text", "updated_at"])
    return note


def note_delete(*, user, note_id: int) -> None:
    note = get_object_or_404(Note, pk=note_id, user=user)
    note.delete()
