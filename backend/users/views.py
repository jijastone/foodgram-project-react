from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import SubscriptionSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('POST', 'DELETE'),
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribtion(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError('не самого себя нельзя')
        if request.method == 'POST':
            _, created = Subscription.objects.get_or_create(
                user=user, author=author)
            if not created:
                raise ValidationError('Не создано')
            serializer = SubscriptionSerializer(
                author, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError('Не существует')
        subscribtion = Subscription.objects.filter(user=user, author=author)
        subscribtion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',),
            detail=False,
            url_path='subscriptions',
            permission_classes=(IsAuthenticated,))
    def get_subscribtions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(subscriptions__user=request.user))
        serializer = SubscriptionSerializer(
            pages, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)
