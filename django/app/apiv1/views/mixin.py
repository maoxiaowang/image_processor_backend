from rest_framework.exceptions import PermissionDenied


class SingleObjectIdentityCheckMixin:

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj


class MultipleObjectsIdentityCheckMixin:
    user_field = 'user'

    def get_queryset(self):
        queryset = super().get_queryset()
        for obj in queryset:
            if hasattr(obj, self.user_field):
                if getattr(obj, self.user_field) != self.request.user:
                    raise PermissionDenied
        return super().get_queryset()
