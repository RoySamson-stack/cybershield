from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook, name='telegram_webhook'),
    path('link/', views.link_account, name='telegram_link'),
    path('link-code/', views.get_linking_code, name='telegram_link_code'),
    path('test/', views.send_test_notification, name='telegram_test'),
]

