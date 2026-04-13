from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Product, Cart, CartItem, Order


class CartTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="123")

        self.product = Product.objects.create(
            name="Test Product",
            price=100,
            available=10,
            description="Test item"
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user.username, "test")

    def test_product_creation(self):
        product = Product.objects.create(
            name="Test Shoe",
            price=1000,
            available=5,
            description="Good shoe"
        )
        self.assertEqual(product.name, "Test Shoe")

    def test_add_to_cart(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(item.quantity, 2)

    def test_cart_total(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        total = item.quantity * self.product.price
        self.assertEqual(total, 200)

    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            total_price=500,
            completed=True
        )
        self.assertEqual(order.completed, True)

    def test_view_cart_api(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get('/api/view-cart/')
        self.assertEqual(response.status_code, 200)