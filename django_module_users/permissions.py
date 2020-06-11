from six import string_types

from django.db.models import Q
from rest_framework import permissions

from django_module_users.models import Permission


class RolePermission(permissions.BasePermission):
    permission_names = None
    detail_pk = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            # No authenticated, no permissions
            return False

        permission_names = self.get_permissions_names()
        if not permission_names:
            return True

        if self.detail_pk is not None and self.detail_pk in view.kwargs:
            queryset = Permission.objects.filter(
                role__users=request.user,
                name__in=permission_names
            ).filter(
                Q(object_id__isnull=True) | Q(object_id=view.kwargs[self.detail_pk])
            ).distinct()

            return queryset.count() == len(permission_names)

        queryset = Permission.objects.filter(
            role__users=request.user,
            name__in=permission_names
        ).distinct()
        return queryset.count() == len(permission_names)

    def get_permissions_names(self):
        if not self.permission_names:
            return None

        if isinstance(self.permission_names, string_types):
            return tuple(self.permission_names)

        # raises TypeError if self.permission_names is not iterable
        iter(self.permission_names)
        return self.permission_names


class RolePermissionDetail(RolePermission):
    permission_names = None
    detail_pk = None

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            # No authenticated, no permissions
            return False

        permission_names = self.get_permissions_names()
        if not permission_names:
            return True

        if self.detail_pk is not None and self.detail_pk in view.kwargs:
            queryset = Permission.objects.filter(
                role__users=request.user,
                name__in=permission_names
            ).filter(
                Q(object_id__isnull=True) | Q(object_id=view.kwargs[self.detail_pk])
            ).distinct()

            return queryset.count() == len(permission_names)

        queryset = Permission.objects.filter(
            role__users=request.user,
            name__in=permission_names
        ).distinct()
        return queryset.count() == len(permission_names)
