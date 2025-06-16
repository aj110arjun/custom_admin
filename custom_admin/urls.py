from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('adminlogin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_then_redirect, name='admin_logout'),
    path('', views.custom_admin_home, name='custom_admin_home'),
    path('users/', views.users, name='users'),
    path('nonstaffs/', views.nonstaffs, name='nonstaffs'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

