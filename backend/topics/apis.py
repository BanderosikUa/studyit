from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import LimitOffsetPagination, get_paginated_response
from topics.models import Note, Topic, UserTopicStatus
from topics.services import (
    category_list_with_progress,
    note_create,
    note_delete,
    note_list,
    note_update,
    progress_export,
    progress_import,
    progress_stats,
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


class ProgressExportApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        class StatusSerializer(serializers.Serializer):
            question_id = serializers.IntegerField()
            status = serializers.ChoiceField(choices=UserTopicStatus.Status.choices)

        class NoteSerializer(serializers.Serializer):
            question_id = serializers.IntegerField()
            text = serializers.CharField()

        class TrainerScoreSerializer(serializers.Serializer):
            question_id = serializers.IntegerField()
            self_score = serializers.IntegerField(min_value=1, max_value=5)
            session_date = serializers.DateField()

        exported_at = serializers.DateTimeField()
        user = serializers.EmailField()
        statuses = StatusSerializer(many=True)
        notes = NoteSerializer(many=True)
        trainer_scores = TrainerScoreSerializer(many=True)

    def get(self, request):
        data = progress_export(user=request.user)
        serializer = self.OutputSerializer(instance=data)

        return Response(serializer.data)


class ProgressImportApi(ApiAuthMixin, APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return Response(
                {"message": "Invalid JSON", "extra": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        progress_import(user=request.user, data=data)
        
        return Response(status=status.HTTP_200_OK)


class ProgressStatsApi(ApiAuthMixin, APIView):
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
        data = progress_stats(user=request.user)
        serializer = self.OutputSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)


class TopicListApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 30
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
        category = serializers.SlugField(required=False)
        status = serializers.ChoiceField(
            choices=UserTopicStatus.Status.choices,
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
        status = serializers.CharField()

    def get(self, request):
        filters = self.FilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)

        data = filters.validated_data
        topics = topic_list(
            user=request.user,
            category_slug=data.get("category"),
            status_filter=data.get("status"),
            search=data.get("search") or None,
        )

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=topics,
            request=request,
            view=self,
        )


class TopicDetailApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        question_id = serializers.IntegerField()
        index = serializers.IntegerField()
        short_answer = serializers.CharField()
        detailed_explanation = serializers.CharField()
        raw_markdown = serializers.CharField()
        category_slug = serializers.CharField(source="category.slug")
        category_name = serializers.CharField(source="category.name")
        status = serializers.CharField()

    def get(self, request, topic_id):
        topic = topic_get(user=request.user, topic_id=topic_id)
        serializer = self.OutputSerializer(topic)
        
        return Response(serializer.data)


class TopicStatusUpdateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=UserTopicStatus.Status.choices)

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
