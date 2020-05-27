# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from rest_framework.exceptions import (
    ValidationError,
)

from .models import ApiKey, Role, Permission

from .serializers import (
    UserSerializer, UserCreateSerializer,
    ApiKeySerializer, ApiKeyUserSerializer, ApiKeyCreateSerializer,
    PermissionSerializer, RoleSerializer,
)

User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all().prefetch_related('groups', 'role_set')
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )

    __basic_fields = ('username',)
    filter_fields = __basic_fields + ('groups', 'is_staff', 'is_active', 'type')
    search_fields = __basic_fields
    ordering_fields = __basic_fields + ('data_joined',)
    ordering = 'username'

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            serializer_response = UserSerializer(user)
            return Response(
                serializer_response.data,
                status=status.HTTP_201_CREATED
            )

        raise ValidationError(
            detail=serializer.errors,
        )

    @action(methods=['get'], detail=True)
    def roles(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        roles = Role.objects.filter(
            users__id=user.id
        ).prefetch_related('permissions').order_by('name')
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def keys(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        keys = ApiKey.objects.filter(
            user__id=user.id
        ).order_by('created_at')
        serializer = ApiKeyUserSerializer(keys, many=True)
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def validate_email(self, request, pk=None):
        user = self.get_object()
        if not user.is_confirmed:
            user.validate_email()

        return Response({}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def resend_email(self, request, pk=None):
        user = self.get_object()
        if not user.is_confirmed:
            user.send_email_verification()

        return Response({}, status=status.HTTP_200_OK)


class ApiKeyViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]

    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer

    __basic_fields = ('name',)
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = ['name']

    def create(self, request, *args, **kwargs):
        serializer = ApiKeyCreateSerializer(data=request.data)

        if serializer.is_valid():
            key = serializer.save()

            serializer_response = ApiKeySerializer(key)
            return Response(
                serializer_response.data,
                status=status.HTTP_201_CREATED
            )

        raise ValidationError(
            detail=serializer.errors,
        )


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = Role.objects.all().prefetch_related('permissions')
    serializer_class = RoleSerializer

    __basic_fields = ('name',)
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = ['name']

    @action(methods=['get'], detail=True)
    def users(self, request, pk=None, *args, **kwargs):
        role = self.get_object()

        serializer = UserSerializer(
            role.users.all().order_by('username').prefetch_related('groups', 'role_set'),
            many=True
        )
        return Response(serializer.data)

    @action(methods=['put'], detail=True, url_path='adduser')
    def adduser(self, request, pk=None, *args, **kwargs):
        role = self.get_object()
        if 'user' not in request.data:
            return Response({'detail': _('Invalid request')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=request.data['user'])
            role.users.add(user)

            serializer = self.get_serializer(role)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['put'], detail=True, url_path='deleteuser')
    def deleteuser(self, request, pk=None, *args, **kwargs):
        role = self.get_object()
        if 'user' not in request.data:
            return Response({'detail': _('Invalid request')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=request.data['user'])
            role.users.remove(user)

            serializer = self.get_serializer(role)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    __basic_fields = ('name',)
    search_fields = __basic_fields
    ordering_fields = __basic_fields
    ordering = ['name']
