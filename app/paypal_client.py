from django.conf import settings
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment

def get_paypal_client():
    if getattr(settings, "PAYPAL_ENV", "sandbox") == "live":
        env = LiveEnvironment(
            client_id=settings.PAYPAL_CLIENT_ID,
            client_secret=settings.PAYPAL_CLIENT_SECRET
        )
    else:
        env = SandboxEnvironment(
            client_id=settings.PAYPAL_CLIENT_ID,
            client_secret=settings.PAYPAL_CLIENT_SECRET
        )
    return PayPalHttpClient(env)
