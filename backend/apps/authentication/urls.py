from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
    path('change-password/', views.change_password, name='change_password'),
    path('refresh/', views.refresh_token, name='refresh_token'),
]

