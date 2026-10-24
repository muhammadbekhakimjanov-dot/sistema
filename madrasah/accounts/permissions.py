from django.contrib.auth.mixins import AccessMixin


class RoleRequiredMixin(AccessMixin):
    """Сервер тарабында ролду текшерет. allowed_roles = ['admin', 'accountant']"""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in self.allowed_roles:
            self.raise_exception = True
            return self.handle_no_permission()  # 403
        return super().dispatch(request, *args, **kwargs)
