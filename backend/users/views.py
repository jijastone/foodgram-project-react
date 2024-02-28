from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (SubscriptionSerializer,
                             SubscriptionCreateSerializer)
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self):
        if self.request.path == '/api/users/me/':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=('POST',),
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribtion(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        data = {'author': author.id, 'user': user.id}
        serializer = SubscriptionCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribtion.mapping.delete
    def delete_subscribtion(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        obj = Subscription.objects.filter(user=user, author=author).delete()
        if obj[0] == 0:
            return Response(
                {'errors': 'Подписка уже удалена!'},
                status=status.HTTP_400_BAD_REQUEST)
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
