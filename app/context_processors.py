from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def subscription_context(request):
    user = getattr(request, "user", None)
    is_premium = False
    if user and user.is_authenticated:
        prof = getattr(user, "profile", None)
        is_premium = getattr(prof, "is_premium_active", False)  # <-- 30 días

    return {
        "IS_PREMIUM": is_premium,
        "PAYPAL_CLIENT_ID": getattr(settings, "PAYPAL_CLIENT_ID", ""),
        "SUBSCRIPTION_PRICE": getattr(settings, "SUBSCRIPTION_PRICE", None),
        "SUBSCRIPTION_CURRENCY": getattr(settings, "SUBSCRIPTION_CURRENCY", "USD"),
        "SUBSCRIPTION_DESCRIPTION": getattr(settings, "SUBSCRIPTION_DESCRIPTION", "Suscripción Premium"),
    }
