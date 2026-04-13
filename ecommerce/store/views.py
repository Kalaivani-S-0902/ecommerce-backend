from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import F


# ----------------------------------------
# Home View (for testing root URL)
# ----------------------------------------
def home(request):
    return JsonResponse({
        "message": "Welcome to Voice-Based E-Commerce API"
    })


# ----------------------------------------
# Product List API
# ----------------------------------------
# views.py
def product_list(request):
    products = Product.objects.all()

    data = []
    for p in products:
        images = []
        for img in p.images.all():  # all related ProductImage objects
            images.append({
                "url": request.build_absolute_uri(img.image.url) if img.image else "",
                "color": img.color or "",
                "size": img.size or "",
                "brand": img.brand or "",
            })

        data.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": str(p.price),
            "available": p.available,
            "images": images,  # ✅ send all images with details
        })

    return JsonResponse(data, safe=False)

# ----------------------------------------
# Voice Login (Temporary placeholder)
# ----------------------------------------
@api_view(['POST'])
def voice_login_api(request):
    """
    Voice login API
    POST: { "username": "", "voice_data": "<base64_audio>" }
    """
    username = request.data.get('username')
    voice_data = request.data.get('voice_data')  # base64 audio

    if not username or not voice_data:
        return Response({"error": "Username and voice data required"}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # Placeholder for voice verification logic
    if voice_data.startswith("VALID"):  # Replace with actual verification
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"success": True, "token": token.key, "message": "Voice login successful"})
    else:
        return Response({"success": False, "message": "Voice authentication failed"}, status=401)





# ----------------------------------------
# Add to Cart API
# ----------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    user = request.user
    quantity = int(request.data.get("quantity", 1))
    color = request.data.get("color", "")
    size = request.data.get("size", "")
    brand = request.data.get("brand", "")

    # Get or create the user's cart
    cart, _ = Cart.objects.get_or_create(user=user)

    # Check if same product with same attributes exists in this cart
    existing_item = CartItem.objects.filter(
        cart=cart,
        product_id=product_id,
        color=color,
        size=size,
        brand=brand
    ).first()

    if existing_item:
        # Merge quantities
        existing_item.quantity = F('quantity') + quantity
        existing_item.save()
        existing_item.refresh_from_db()
    else:
        # Create new cart item
        CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            quantity=quantity,
            color=color,
            size=size,
            brand=brand
        )

    return JsonResponse({
        "message": "Product added to cart",
        "quantity": existing_item.quantity if existing_item else quantity
    })
# ----------------------------------------
# Checkout API
# ----------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user

    if not user:
        return JsonResponse({"error": "No user found"}, status=400)

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return JsonResponse({"message": "Cart is empty"}, status=400)

    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return JsonResponse({"message": "Cart is empty"}, status=400)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    # Create Order
    order = Order.objects.create(
        user=user,
        total_price=total,
        completed=True
    )

    # Create OrderItems from CartItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
    )

    # Clear cart
    cart_items.delete()

    return JsonResponse({
        "message": "Order placed successfully",
        "order_id": order.id,
        "total_price": total
    })
# ----------------------------------------
# View Cart API
# ----------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return JsonResponse({"items": [], "total_cart_price": "0.0"})

    cart_items = CartItem.objects.filter(cart=cart)

    items = []
    total_price = 0

    for item in cart_items:
        item_total = item.quantity * item.product.price
        total_price += item_total

        # ✅ STEP 1: find correct image for this variant
        image_url = ""

        for img in item.product.images.all():
            if (
                img.color == item.color and
                img.size == item.size and
                img.brand == item.brand
            ):
                image_url = request.build_absolute_uri(img.image.url)
                break

        # ✅ STEP 2: append item
        items.append({
            "product_id": item.product.id,
            "product_name": item.product.name,
            "price": str(item.product.price),
            "quantity": item.quantity,
            "item_total": str(item_total),
            "description": item.product.description,
            "image": image_url,

            "color": item.color or "",
            "size": item.size or "",
            "brand": item.brand or ""
        })

    # ✅ IMPORTANT: return OUTSIDE loop
    return JsonResponse({
        "items": items,
        "total_cart_price": str(total_price)
    })


    # ----------------------------------------
# Remove From Cart API
# ----------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)

        color = request.data.get("color", "")
        size = request.data.get("size", "")
        brand = request.data.get("brand", "")

        cart_item = CartItem.objects.get(
            cart=cart,
            product_id=product_id,
            color=color,
            size=size,
            brand=brand
        )

        quantity = int(request.data.get("quantity", 1))

        if quantity >= cart_item.quantity:
          cart_item.delete()  # remove completely if equal or more
        else:
          cart_item.quantity -= quantity
          cart_item.save()

        return JsonResponse({"message": "Item removed from cart"})

    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart not found"}, status=404)

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    except CartItem.DoesNotExist:
        return JsonResponse({"error": "Item not in cart"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ----------------------------------------
# Update Cart Quantity API
# ----------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart(request, product_id, quantity):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
        product = Product.objects.get(id=product_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)

        cart_item.quantity = quantity
        cart_item.save()
    except:
        return JsonResponse({"message": "Item not found"}, status=400)

    return JsonResponse({
        "message": "Quantity updated",
        "new_quantity": cart_item.quantity
    })
# ----------------------------------------
# Order History API
# ----------------------------------------
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request):
    user = request.user

    # ✅ Auto delete orders older than 24 hours
    Order.objects.filter(
        user=user,
        created_at__lt=timezone.now() - timedelta(hours=24)
    ).delete()

    orders = Order.objects.filter(user=user).order_by('-id')

    data = []

    for order in orders:
        items = OrderItem.objects.filter(order=order)

        item_list = []

        for item in items:
            image_url = ""
            color = ""
            size = ""
            brand = ""

            # ✅ get first image (like cart)
            for img in item.product.images.all():
                image_url = request.build_absolute_uri(img.image.url)
                color = img.color or ""
                size = img.size or ""
                brand = img.brand or ""
                break

            item_list.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "image": image_url,
                "color": color,
                "size": size,
                "brand": brand
            })

        data.append({
            "id": order.id,
            "total_price": str(order.total_price),
            "created_at": order.created_at,
            "items": item_list
        })

    return JsonResponse({"orders": data})

@api_view(['POST'])
def voice_register_login(request):
    username = request.data.get('username')

    if not username:
        return Response({"error": "Username is required"}, status=400)

    # ✅ If user exists → login directly
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"password": "demo_password"}
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "token": token.key,
        "message": "Login successful (Demo Mode) ✅"
    })