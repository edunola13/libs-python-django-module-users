# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.exceptions import (
    ValidationError,
)

from .serializers import (
    UserRegisterSerializer, UserMeSerializer,
    ConfirmEmailSerializer, ResendEmailSerializer,
    ChangeEmailSerializer, ChangePasswordSerializer,
)

User = get_user_model()


class UserRegisterView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)

        if User.objects.filter(username=request.data.get('username')).exists():
            return Response(
                {'detail': _('There is already an account created with this email.')},
                status=status.HTTP_409_CONFLICT
            )

        if serializer.is_valid():
            user = serializer.save()

            serializer_response = UserMeSerializer(user)
            return Response(
                serializer_response.data,
                status=status.HTTP_201_CREATED
            )

        raise ValidationError(
            detail=serializer.errors,
        )


class UserMeView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        user = request.user

        serializer = UserMeSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        raise ValidationError(
            detail=serializer.errors,
        )


class ConfirmEmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key = serializer.validated_data['key']
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            user.confirm_email(key)
        except:
            raise ValidationError(
                detail=_('Invalid validation code.'),
            )

        serializer_response = UserMeSerializer(user)
        return Response(
            serializer_response.data,
            status=status.HTTP_200_OK
        )


class ResendEmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ResendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            if not user.is_confirmed:
                user.send_email_verification()
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response({}, status=status.HTTP_200_OK)


class ChangeEmailView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if not request.user.check_password(password):
            return Response(
                {'detail': _('Incorrect Password.')},
                status=status.HTTP_409_CONFLICT
            )

        request.user.change_email(new_email)

        return Response({}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actual_password = serializer.validated_data['actual_password']
        new_password = serializer.validated_data['new_password']

        if not request.user.check_password(actual_password):
            return Response(
                {'detail': _('Incorrect Password.')},
                status=status.HTTP_409_CONFLICT
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response({}, status=status.HTTP_200_OK)
