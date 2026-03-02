from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from trainer.services import (
    trainer_session_create,
    trainer_session_generate_prompt,
    trainer_session_get,
    trainer_session_submit_answer,
)


class ApiAuthMixin:
    permission_classes = [IsAuthenticated]


class SessionCreateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        category = serializers.SlugField(required=False, allow_null=True)
        total_questions = serializers.IntegerField(min_value=1, max_value=50)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        total_questions = serializers.IntegerField()
        category_slug = serializers.SerializerMethodField()
        completed = serializers.BooleanField()

        def get_category_slug(self, obj):
            return obj.category.slug if obj.category else None

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        session = trainer_session_create(
            user=request.user,
            category_slug=data.get("category"),
            total_questions=data["total_questions"],
        )
        output = self.OutputSerializer(session)
        return Response(output.data, status=status.HTTP_201_CREATED)


class SessionDetailApi(ApiAuthMixin, APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        total_questions = serializers.IntegerField()
        category_slug = serializers.SerializerMethodField()
        completed = serializers.BooleanField()
        questions = serializers.SerializerMethodField()

        def get_category_slug(self, obj):
            return obj.category.slug if obj.category else None

        def get_questions(self, obj):
            return [
                {
                    "topic_id": a.topic_id,
                    "title": a.topic.title,
                    "user_answer": a.user_answer,
                    "self_score": a.self_score,
                }
                for a in obj.answers.select_related("topic").order_by("id")
            ]

    def get(self, request, session_id):
        session = trainer_session_get(user=request.user, session_id=session_id)
        serializer = self.OutputSerializer(session)
        return Response(serializer.data)


class SessionAnswerApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        topic_id = serializers.IntegerField()
        user_answer = serializers.CharField(allow_blank=True)
        self_score = serializers.IntegerField(
            min_value=1, max_value=5, required=False, allow_null=True
        )

    def post(self, request, session_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        trainer_session_submit_answer(
            user=request.user,
            session_id=session_id,
            topic_id=data["topic_id"],
            user_answer=data.get("user_answer", ""),
            self_score=data.get("self_score"),
        )
        return Response(status=status.HTTP_200_OK)


class SessionPromptApi(ApiAuthMixin, APIView):
    def get(self, request, session_id):
        prompt = trainer_session_generate_prompt(
            user=request.user,
            session_id=session_id,
        )
        return Response({"prompt": prompt})
