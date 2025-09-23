# app/paypal_client.py
import json
import requests
from django.conf import settings

PAYPAL_BASE = "https://api-m.sandbox.paypal.com"  # sandbox
CLIENT_ID = getattr(settings, "PAYPAL_CLIENT_ID", "")
CLIENT_SECRET = getattr(settings, "PAYPAL_CLIENT_SECRET", "")

# Ajustes de suscripción (usa CLP sin decimales)
SUBSCRIPTION_AMOUNT = "2000"      # CLP es 0-decimal -> "2000" (no 2000.00)
SUBSCRIPTION_CURRENCY = "CLP"     # Debe coincidir con el SDK del front

def _get_access_token():
    resp = requests.post(
        f"{PAYPAL_BASE}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def create_order():
    """
    Crea la orden en PayPal con CLP y sin decimales.
    """
    access_token = _get_access_token()
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": SUBSCRIPTION_CURRENCY,
                    "value": SUBSCRIPTION_AMOUNT,  # "2000" para CLP
                },
                "description": "EcoIntercambio - Suscripción Premium",
            }
        ],
        "application_context": {
            "brand_name": "EcoIntercambio",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW",
            # Opcional: páginas de retorno si usaras redirect (con botones estándar no hace falta)
        },
    }
    resp = requests.post(
        f"{PAYPAL_BASE}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        data=json.dumps(payload),
        timeout=30,
    )
    # Si hay error, lanza excepción (útil para ver en consola)
    resp.raise_for_status()
    return resp.json()

def capture_order(order_id: str):
    access_token = _get_access_token()
    resp = requests.post(
        f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
