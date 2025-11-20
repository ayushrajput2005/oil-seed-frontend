import requests
from decimal import Decimal
from django.conf import settings

import requests

API_KEY = "YOUR_API_KEY_HERE"

def format_commodity_name(name: str) -> str:
    """
    Converts any oilseed or by-product into API-friendly commodity code.
    Example:
        'soy meal' -> 'SOYMEAL'
        'cotton seed' -> 'COTTONSEED'
        'groundnut cake' -> 'GROUNDNUTCAKE'
    """
    return name.replace(" ", "").replace("-", "").upper()


def get_price_per_kg_in_inr(product_name):
    # Step 1 — Standardize the input
    commodity_code = format_commodity_name(product_name)

    # Step 2 — API endpoint
    url = (
        f"https://commodities-api.com/api/latest"
        f"?access_key={API_KEY}&symbols={commodity_code}&base=INR"
    )

    # Step 3 — API call
    response = requests.get(url).json()

    if "data" not in response:
        return {"error": "Invalid commodity or API error", "raw": response}

    try:
        price_per_unit = response["data"]["rates"][commodity_code]  # Price per TON or UNIT
    except KeyError:
        return {"error": "Commodity not found in API", "raw": response}

    # ❗ Most commodity APIs give **price per metric ton (1000 kg)**
    # Convert TON → KG
    price_per_kg = price_per_unit / 1000

    return price_per_kg

