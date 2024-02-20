from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField

from .models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name', 'password',)


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta():
        model = User
        fields = (*UserSerializer.Meta.fields, 'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=author
        ).exists()
