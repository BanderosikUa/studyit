from datetime import datetime, timezone
from typing import Any

from topics.models import Note, Topic, UserTopicStatus
from trainer.models import TrainerAnswer


def progress_export(*, user) -> dict[str, Any]:
    statuses = UserTopicStatus.objects.filter(user=user).select_related("topic")
    notes = Note.objects.filter(user=user).select_related("topic")
    answers = (
        TrainerAnswer.objects.filter(session__user=user)
        .select_related("topic", "session")
    )
    return {
        "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "user": user.email,
        "statuses": [
            {"question_id": s.topic.question_id, "status": s.status}
            for s in statuses
        ],
        "notes": [
            {"question_id": n.topic.question_id, "text": n.text}
            for n in notes
        ],
        "trainer_scores": [
            {
                "question_id": a.topic.question_id,
                "self_score": a.self_score,
                "session_date": a.session.created_at.date().isoformat(),
            }
            for a in answers
            if a.self_score is not None
        ],
    }


def progress_import(*, user, data: dict) -> None:
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
        if qid is None or status_val not in ("new", "studied", "review"):
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


def progress_stats(*, user) -> list[dict]:
    from topics.services import category_list_with_progress
    return category_list_with_progress(user=user)
