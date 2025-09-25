# app/paypal_client.py
import json
import base64
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import requests
from django.conf import settings

log = logging.getLogger(__name__)

PAYPAL_BASE = "https://api-m.sandbox.paypal.com" if getattr(settings, "PAYPAL_ENV", "sandbox") == "sandbox" else "https://api-m.paypal.com"


@dataclass
class PayPalToken:
    access_token: str
    token_type: str
    expires_in: int


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("utf-8")


def get_access_token() -> PayPalToken:
    """Obtiene un access_token de PayPal con logs claros si falla."""
    url = f"{PAYPAL_BASE}/v1/oauth2/token"
    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET

    headers = {
        "Authorization": _basic_auth_header(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    log.info("[PayPal] Solicitando access_token → %s", url)
    resp = requests.post(url, headers=headers, data=data, timeout=30)
    log.info("[PayPal] access_token status=%s", resp.status_code)

    if resp.status_code != 200:
        log.error("[PayPal] Error access_token (%s): %s", resp.status_code, resp.text)
        raise RuntimeError(f"PayPal token error {resp.status_code}: {resp.text}")

    j = resp.json()
    return PayPalToken(
        access_token=j["access_token"],
        token_type=j.get("token_type", "Bearer"),
        expires_in=j.get("expires_in", 0),
    )


def create_order(amount: str, currency: str, description: str) -> str:
    """Crea una orden y devuelve el orderID."""
    token = get_access_token()

    url = f"{PAYPAL_BASE}/v2/checkout/orders"
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": currency,
                    "value": amount,
                },
                "description": description,
            }
        ],
        # Puedes habilitar estas URLs si quieres usar redirect (aquí usamos el popup):
        # "application_context": {
        #     "return_url": "https://example.com/return",
        #     "cancel_url": "https://example.com/cancel",
        # }
    }

    log.info("[PayPal] Crear orden → %s body=%s", url, json.dumps(body))
    resp = requests.post(url, headers=headers, json=body, timeout=30)
    log.info("[PayPal] Crear orden status=%s", resp.status_code)

    if resp.status_code not in (201, 200):
        log.error("[PayPal] Error crear orden (%s): %s", resp.status_code, resp.text)
        raise RuntimeError(f"PayPal create order error {resp.status_code}: {resp.text}")

    order = resp.json()
    order_id = order.get("id")
    if not order_id:
        log.error("[PayPal] Respuesta sin id: %s", resp.text)
        raise RuntimeError("PayPal create order: respuesta sin 'id'")
    return order_id


def capture_order(order_id: str) -> Tuple[str, dict]:
    """Captura una orden ya aprobada. Devuelve (status, json_completo)."""
    token = get_access_token()

    url = f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "Content-Type": "application/json",
    }

    log.info("[PayPal] Capturar orden → %s", url)
    resp = requests.post(url, headers=headers, json={}, timeout=30)
    log.info("[PayPal] Capturar orden status=%s", resp.status_code)

    if resp.status_code not in (201, 200):
        log.error("[PayPal] Error capturar (%s): %s", resp.status_code, resp.text)
        raise RuntimeError(f"PayPal capture error {resp.status_code}: {resp.text}")

    j = resp.json()
    status = j.get("status", "UNKNOWN")
    return status, j
import os
from django.conf import settings
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment

def get_paypal_client() -> PayPalHttpClient:
    """Devuelve el cliente PayPal en sandbox o live según settings.PAYPAL_ENV."""
    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET

    if settings.PAYPAL_ENV.lower() == "live":
        env = LiveEnvironment(client_id=client_id, client_secret=client_secret)
    else:
        env = SandboxEnvironment(client_id=client_id, client_secret=client_secret)

    return PayPalHttpClient(env)

