from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custom-admin/', include('custom_admin.urls')),
    path('',include('home.urls'))
]
