from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/',views.login_user, name='login'),
    path('signup/', views.signup_user, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
