from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path('', views.main, name='main'),
    path('create', views.create, name='create'),
    path('register', views.register, name='register'),
    path('get_csrf', views.get_csrf, name='get_csrf'),
    path('rooms', views.rooms, name='rooms'),
    path('connect', views.connect, name='connect'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
