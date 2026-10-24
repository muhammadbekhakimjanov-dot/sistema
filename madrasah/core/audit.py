from .models import AuditLog


def get_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    return fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR")


def log_action(request, action, obj=None, model_name="", details=None):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=model_name or (obj.__class__.__name__ if obj else ""),
        object_id=str(obj.pk) if obj is not None and obj.pk else "",
        details=details or {},
        ip_address=get_ip(request),
    )
