from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.services import user_create


class RegisterApi(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(min_length=8, write_only=True)

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        access = serializers.CharField()
        refresh = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_create(**serializer.validated_data)
        token_serializer = CustomTokenObtainPairSerializer()
        tokens = token_serializer.get_token(user)
        data = {
            "email": user.email,
            "access": str(tokens.access_token),
            "refresh": str(tokens),
        }
        output = self.OutputSerializer(instance=data)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["email"] = self.user.email
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LoginApi(CustomTokenObtainPairView):
    permission_classes = [AllowAny]


class RefreshApi(TokenRefreshView):
    permission_classes = [AllowAny]
