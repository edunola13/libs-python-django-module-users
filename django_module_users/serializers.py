# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from django.utils.translation import gettext as _
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation

from .models import ApiKey, Role, Permission

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            'id', 'name', 'content_type', 'object_id'
        )


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_id = serializers.PrimaryKeyRelatedField(
        source='permissions', queryset=Permission.objects.all(), write_only=True, many=True
    )

    class Meta:
        model = Role
        fields = (
            'id', 'name', 'permissions', 'permissions_id',
        )


class RoleSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = (
            'id', 'name',
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class ApiKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = ApiKey
        fields = (
            'id', 'key', 'user', 'created_at',
        )


class ApiKeyCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, many=False
    )

    class Meta:
        model = ApiKey
        fields = (
            'user',
        )


class ApiKeyUserSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()

    class Meta:
        model = ApiKey
        fields = (
            'id', 'key', 'created_at',
        )

    def get_key(self, obj):
        return "{}...".format(obj.key[:10])


class UserMinSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_confirmed', 'is_active', 'type')


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    groups_id = serializers.PrimaryKeyRelatedField(source='groups', queryset=Group.objects.all(), write_only=True, many=True)
    roles = RoleSimpleSerializer(source='role_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_confirmed', 'is_staff', 'is_active',
                  'type', 'groups', 'groups_id', 'roles',
                  'date_joined', 'last_login')
        extra_kwargs = {
            'email': {'read_only': True},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    groups_id = serializers.PrimaryKeyRelatedField(
        source='groups', queryset=Group.objects.all(), write_only=True, many=True, required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password',
                  'is_staff', 'is_active', 'type', 'groups_id')

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user = User.create(**validated_data)
        user.groups.add(*groups)

        return user


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password', 'type')

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        user = User.create(**validated_data)

        return user


class UserMeSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    roles = RoleSerializer(source="role_set", many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_confirmed', 'is_staff', 'is_active',
                  'type', 'roles', 'groups')
        extra_kwargs = {
            'username': {'read_only': True},  # Mientras se maneje como uno con el email
            'email': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
            'is_confirmed': {'read_only': True},
        }


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    key = serializers.CharField(max_length=6, required=True)


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, value):
        """Check if user already exist."""
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError(_("Email not available."))
        except User.DoesNotExist:
            pass

        return value


class ChangePasswordSerializer(serializers.Serializer):
    actual_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
