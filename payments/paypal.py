import requests
from django.conf import settings
from base64 import b64encode


class PayPalClient:
    def __init__(self):
        self.base_url = settings.PAYPAL_BASE_URL
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret = settings.PAYPAL_SECRET

    def _headers(self):
        auth = b64encode(
            f"{self.client_id}:{self.secret}".encode()
        ).decode()

        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth}",
        }

    def create_order(self, amount, currency="USD"):
        url = f"{self.base_url}/v2/checkout/orders"

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount),
                    }
                }
            ]
        }

        response = requests.post(
            url, json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def capture_order(self, paypal_order_id):
        url = f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture"

        response = requests.post(
            url, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
