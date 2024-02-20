from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.serializers import SubscriptionSerializer

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    @action(methods=('POST', 'DELETE'),
            detail=True,
            url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribtion(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError('a')
        if request.method == 'POST':
            _, created = Subscription.objects.get_or_create(
                user=user, author=author)
            if not created:
                raise ValidationError('SUBSCRIPTION_EXIST_MESSAGE')
            serializer = SubscriptionSerializer(
                author, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribtion = get_object_or_404(
            Subscription, user=user, author=author)
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
