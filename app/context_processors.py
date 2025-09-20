from django.conf import settings

def subscription_context(request):
    return {
        "PAYPAL_CLIENT_ID": getattr(settings, "PAYPAL_CLIENT_ID", ""),
        "SUBSCRIPTION_PRICE": getattr(settings, "SUBSCRIPTION_PRICE", 2000),
        "SUBSCRIPTION_CURRENCY": getattr(settings, "SUBSCRIPTION_CURRENCY", "USD"),
    }
