from django.urls import path
from .views import home
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('scan/', views.scan, name='scan'),
    path('process_image/', views.process_image, name='process_image'),
]

# Tambahkan pengaturan media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

