from django.contrib import admin
from .models import Product, ProductImage, Cart

# Inline admin for product variants/images
class ProductImageInline(admin.TabularInline):  # or admin.StackedInline
    model = ProductImage
    extra = 1  # Number of empty slots shown by default
    fields = ('image', 'color', 'size', 'brand')

# Main product admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')
    inlines = [ProductImageInline]  # attach the inline

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)