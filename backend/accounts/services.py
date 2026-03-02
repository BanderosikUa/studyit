from django.contrib.auth import get_user_model

User = get_user_model()


def user_create(*, email: str, password: str) -> User:
    user = User(email=email)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user
