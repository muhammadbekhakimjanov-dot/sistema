from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import CustomLoginView  # Биз яратган махсус login view'ни чақирамиз

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),  # auth_views ўрнига CustomLoginView қўйилди
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password/", views.ChangePasswordView.as_view(), name="password_change"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/new/", views.UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/reset/", views.UserResetPasswordView.as_view(), name="user_reset"),
    path("users/<int:pk>/toggle/", views.UserToggleActiveView.as_view(), name="user_toggle"),
]