from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product-list'),
    path('api/voice-login/', views.voice_login_api, name='voice-login'),
    path('add-to-cart-default/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('add-to-cart/<int:product_id>/<int:quantity>/', views.add_to_cart, name='add-to-cart-with-quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('view-cart/', views.view_cart, name='view-cart'),  # corrected
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('update-cart/<int:product_id>/<int:quantity>/', views.update_cart, name='update-cart'),
    path('orders/', views.order_history, name='orders'),
    path('voice-register-login/', views.voice_register_login, name='voice-register-login'),
    path('api/login/', obtain_auth_token, name='api-login'),
]