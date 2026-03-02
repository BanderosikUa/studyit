from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from topics.progress_services import progress_export, progress_import, progress_stats


class ApiAuthMixin:
    permission_classes = [IsAuthenticated]


class ProgressExportApi(ApiAuthMixin, APIView):
    def get(self, request):
        data = progress_export(user=request.user)
        return Response(data)


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
