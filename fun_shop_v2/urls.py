from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('fakha0/', admin.site.urls),
    path('', include("website.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
