from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import jwt, datetime
from django.conf import settings
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import ProductSerializer
from .services import get_price_per_kg_in_inr
from .models import Product
from rest_framework.parsers import MultiPartParser, FormParser

#Registration
@api_view(['POST'])
def register(request):
    username=request.data.get("username")
    email=request.data.get("email")
    password=request.data.get("password")
    mobile_no=request.data.get("mobile_no")

    if not username or not email or not password or not mobile_no:
        return Response({"error":"All fields required "},status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error":"Username already exists"},status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error":"email already exists"},status=400)

    user=User.objects.create_user(username=username,email=email,password=password)
    
    from .models import UserProfile
    UserProfile.objects.create(user=user, mobile_no=mobile_no)

    return Response({"message":"User registered successfully"})

#Login
@api_view(['POST'])
def login(request):
    email=request.data.get("email")
    password=request.data.get("password")
    #email
    try:
        user=User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"Invalid credentials"},status=400)
    #password
    user_auth=authenticate(username=user.username,password=password)
    if not user_auth:
        return Response({"error":"Invalid credentials"},status=400)

    #JWT token
    payload={
        "id": user.id,
        "exp": datetime.datetime.utcnow()+datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload,settings.SECRET_KEY,algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return Response({"token":token,"username":user.username})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        "username":user.username,
        "email":user.email,
    })

#LOGOUT
@api_view(['POST'])
def logout(request):
    return Response({"message":"Logout handled on client side"})

#PRODUCT LISTING
class CreateproductAPIView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request):
        return Response({"message": "Use POST to create product"})

    def post(self, request):
        user = request.user
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save(owner=user)

            return Response({
                "message": "Product stored successfully",
                "product_type": product.type,
                "product_name": product.product_name,
                "date_of_listing": product.date_of_listing,
                "certification_file": product.certificate.url,
                "amount_available_kg": str(product.amount_kg),
                "price_per_kg_inr": str(product.market_price_per_kg_inr),
                "image": product.image.url if product.image else None,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SeedListingAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        seeds=Product.objects.filter(owner=request.user,type="seeds")
        serializer=ProductSerializer(seeds, many=True)
        return Response(serializer.data)

class ByproductListingAPIView(APIView):
    permission_classees=[IsAuthenticated]
    def get(self,request):
        items = Product.objects.filter(owner=request.user,type="byproduct")
        serializer=ProductSerializer(items,many=True)
        return Response(serializer.data)

import decimal
class SeedMarketView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        products = Product.objects.filter(type="seeds", amount_kg__gt=0)
        data = []
        for p in products:
            data.append({
                "id": p.id,
                "product_name": p.product_name,
                "type": p.type,
                "amount_kg": p.amount_kg,
                "price_per_kg": p.market_price_per_kg_inr,
                "owner": p.owner.username,
                "certificate": p.certificate.url if p.certificate else None,
                "image": p.image.url if p.image else None
            })
        return Response(data)

class ByproductMarketView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        products = Product.objects.filter(type="byproduct", amount_kg__gt=0)
        data = []
        for p in products:
            data.append({
                "id": p.id,
                "product_name": p.product_name,
                "type": p.type,
                "amount_kg": p.amount_kg,
                "price_per_kg": p.market_price_per_kg_inr,
                "owner": p.owner.username,
                "certificate": p.certificate.url if p.certificate else None,
                "image": p.image.url if p.image else None
            })
        return Response(data)

class BuyProductView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        product_id = request.data.get('product_id')

        from django.db import transaction

        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=product_id)
                
                quantity_to_buy = product.amount_kg
                
                if quantity_to_buy <= 0:
                     return Response({"error": "Product is out of stock"}, status=status.HTTP_400_BAD_REQUEST)

                product.amount_kg = 0
                product.save()
                
                return Response({"message": f"Successfully purchased {quantity_to_buy}kg of {product.product_name}"})
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)




















