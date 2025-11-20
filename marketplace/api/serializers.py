from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields="__all__"
        read_only_fields=["owner", "market_price_per_kg_inr"]
