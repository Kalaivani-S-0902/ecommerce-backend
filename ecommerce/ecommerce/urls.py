from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static  # Add this import
from rest_framework.authtoken.views import obtain_auth_token
from store.views import add_to_cart

urlpatterns = [
    path('', lambda request: HttpResponse("Backend is running successfully")),
    path('admin/', admin.site.urls),
    path('api/login/',obtain_auth_token),
    path('api/', include('store.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)