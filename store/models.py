from django.db import models
from django.contrib.auth.models import User



class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    available = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.color or 'No Color'} - {self.size or 'No Size'} -{self.brand or 'No Brand'}"

    def image_url(self):
        if self.image:
            return self.image.url
        return ""
    
    # ✅ ADD THIS NEW MODEL BELOW


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add this
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)  # temporary nullable
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    # New fields for variants
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='cart_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.color}, {self.size}, {self.brand})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"