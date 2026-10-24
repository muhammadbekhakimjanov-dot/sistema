import secrets

from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from  madrasah.core.audit import log_action
from .forms import DeactivateForm, UserForm
from .models import User
from .permissions import RoleRequiredMixin
from django.contrib.auth.views import LoginView

class UserListView(RoleRequiredMixin, ListView):
    allowed_roles = ["admin"]
    model = User
    template_name = "accounts/user_list.html"
    paginate_by = 30

    def get_queryset(self):
        qs = User.objects.order_by("last_name", "first_name")
        q = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role", "")
        if q:
            qs = qs.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q)
                           | Q(username__icontains=q))
        if role:
            qs = qs.filter(role=role)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["roles"] = User.Role.choices
        return ctx


class UserCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["admin"]
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        user = form.save(commit=False)
        temp = secrets.token_urlsafe(8)
        user.set_password(temp)
        user.must_change_password = True
        user.save()
        log_action(self.request, "create", user, details={"role": user.role})
        messages.success(
            self.request,
            f"Аккаунт түзүлдү. Логин: {user.username} | Убактылуу сырсөз: {temp} "
            "(бир гана жолу көрсөтүлөт, колдонуучуга өткөрүп бериңиз)")
        return redirect(self.success_url)


class UserUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["admin"]
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        old = User.objects.get(pk=self.object.pk)
        resp = super().form_valid(form)
        changed = {f: [str(getattr(old, f)), str(getattr(self.object, f))]
                   for f in form.changed_data}
        log_action(self.request, "update", self.object, details=changed)
        messages.success(self.request, "Маалымат сакталды.")
        return resp


class UserResetPasswordView(RoleRequiredMixin, View):
    allowed_roles = ["admin"]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        temp = secrets.token_urlsafe(8)
        user.set_password(temp)
        user.must_change_password = True
        user.save()
        log_action(request, "reset_password", user)
        messages.success(request, f"{user.username} үчүн жаңы убактылуу сырсөз: {temp}")
        return redirect("user_list")


class UserToggleActiveView(RoleRequiredMixin, View):
    """Аккаунтту өчүрбөстөн жабат/кайра ачат. Себеби, күнү, жооптуу сакталат."""
    allowed_roles = ["admin"]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, "accounts/user_deactivate.html",
                      {"target": user, "form": DeactivateForm()})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            messages.error(request, "Өз аккаунтуңузду жаба албайсыз.")
            return redirect("user_list")
        if user.is_active:
            form = DeactivateForm(request.POST)
            if not form.is_valid():
                return render(request, "accounts/user_deactivate.html",
                              {"target": user, "form": form})
            user.is_active = False
            user.deactivated_at = timezone.now()
            user.deactivation_reason = form.cleaned_data["reason"]
            user.deactivated_by = request.user
            user.save()
            log_action(request, "deactivate", user,
                       details={"reason": user.deactivation_reason})
            messages.success(request, "Аккаунт жабылды (маалыматтар сакталды).")
        else:
            user.is_active = True
            user.deactivated_at = None
            user.deactivation_reason = ""
            user.deactivated_by = None
            user.save()
            log_action(request, "reactivate", user)
            messages.success(request, "Аккаунт кайра активдештирилди.")
        return redirect("user_list")


class ChangePasswordView(PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        resp = super().form_valid(form)
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password"])
        log_action(self.request, "change_password", self.request.user)
        return resp

 

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True