from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('', include('apps.core.urls')),  # Core endpoints (health, organizations, etc.)
        path('auth/', include('apps.authentication.urls')),
        path('ransomware/', include('apps.ransomware.urls')),
        path('breaches/', include('apps.breaches.urls')),
        path('scanner/', include('apps.scanner.urls')),
        path('phishing/', include('apps.phishing.urls')),
        path('alerts/', include('apps.alerts.urls')),
        path('threats/', include('apps.threats.urls')),
        path('telegram/', include('apps.telegram.urls')),
        path('cve/', include('apps.cve.urls')),
        path('monitoring/', include('apps.monitoring.urls')),
        path('malware/', include('apps.malware.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
