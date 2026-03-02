from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from topics.models import Note, Topic
from topics.services import (
    category_list_with_progress,
    note_create,
    note_delete,
    note_list,
    note_update,
    topic_get,
    topic_list,
    topic_status_update,
)


class ApiAuthMixin:
    permission_classes = [IsAuthenticated]


class CategoryListApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        slug = serializers.CharField()
        order = serializers.IntegerField()
        total_topics = serializers.IntegerField()
        studied_count = serializers.IntegerField()
        review_count = serializers.IntegerField()
        new_count = serializers.IntegerField()

    def get(self, request):
        data = category_list_with_progress(user=request.user)
        serializer = self.OutputSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class TopicListApi(ApiAuthMixin, APIView):
    class FilterSerializer(serializers.Serializer):
        category = serializers.SlugField(required=False)
        status = serializers.ChoiceField(
            choices=["new", "studied", "review"],
            required=False,
        )
        search = serializers.CharField(required=False, allow_blank=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        question_id = serializers.IntegerField()
        index = serializers.IntegerField()
        category_slug = serializers.CharField(source="category.slug")
        category_name = serializers.CharField(source="category.name")
        status = serializers.SerializerMethodField()

        def get_status(self, obj):
            from topics.models import UserTopicStatus
            s = UserTopicStatus.objects.filter(
                topic=obj,
                user=self.context["request"].user,
            ).values_list("status", flat=True).first()
            return s or "new"

    def get(self, request):
        filters = self.FilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        topics = topic_list(
            user=request.user,
            category_slug=filters.validated_data.get("category"),
            status_filter=filters.validated_data.get("status"),
            search=filters.validated_data.get("search") or None,
        )
        serializer = self.OutputSerializer(
            topics,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class TopicDetailApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        question_id = serializers.IntegerField()
        index = serializers.IntegerField()
        source_url = serializers.URLField(allow_blank=True)
        short_answer = serializers.CharField()
        detailed_explanation = serializers.CharField()
        raw_markdown = serializers.CharField()
        category_slug = serializers.CharField(source="category.slug")
        category_name = serializers.CharField(source="category.name")
        status = serializers.SerializerMethodField()

        def get_status(self, obj):
            from topics.models import UserTopicStatus
            s = UserTopicStatus.objects.filter(
                topic=obj,
                user=self.context["request"].user,
            ).values_list("status", flat=True).first()
            return s or "new"

    def get(self, request, topic_id):
        topic = topic_get(topic_id=topic_id)
        serializer = self.OutputSerializer(
            topic,
            context={"request": request},
        )
        return Response(serializer.data)


class TopicStatusUpdateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=["new", "studied", "review"])

    def post(self, request, topic_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        topic_status_update(
            user=request.user,
            topic_id=topic_id,
            status=serializer.validated_data["status"],
        )
        return Response(status=status.HTTP_200_OK)


class NoteListApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        text = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    class CreateInputSerializer(serializers.Serializer):
        text = serializers.CharField()

    def get(self, request, topic_id):
        notes = note_list(user=request.user, topic_id=topic_id)
        serializer = self.OutputSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request, topic_id):
        inp = self.CreateInputSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        note = note_create(
            user=request.user,
            topic_id=topic_id,
            text=inp.validated_data["text"],
        )
        return Response(
            self.OutputSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )


class NoteUpdateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        text = serializers.CharField()

    def put(self, request, note_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note_update(
            user=request.user,
            note_id=note_id,
            text=serializer.validated_data["text"],
        )
        return Response(status=status.HTTP_200_OK)


class NoteDeleteApi(ApiAuthMixin, APIView):
    def delete(self, request, note_id):
        note_delete(user=request.user, note_id=note_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
