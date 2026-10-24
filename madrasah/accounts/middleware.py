from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Админ сырсөздү калыбына келтиргенден кийин жаңы сырсөз коюуга мажбурлайт."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        # getattr колдонуп, must_change_password талаасы бар болсо гана текшеребиз:
        if user.is_authenticated and getattr(user, 'must_change_password', False):
            allowed = {reverse("password_change"), reverse("logout")}
            if request.path not in allowed and not request.path.startswith("/static/"):
                return redirect("password_change")
        return self.get_response(request)
