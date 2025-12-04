from django.contrib import admin
from .models import CVE, CVEComment


@admin.register(CVE)
class CVEAdmin(admin.ModelAdmin):
    list_display = ['cve_id', 'title', 'severity', 'cvss_v3_score', 'has_exploit', 'status', 'published_date']
    list_filter = ['severity', 'status', 'has_exploit', 'poc_available', 'is_verified']
    search_fields = ['cve_id', 'title', 'description', 'vendor']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(CVEComment)
class CVECommentAdmin(admin.ModelAdmin):
    list_display = ['cve', 'user', 'upvotes', 'created_at']
    list_filter = ['is_verified_expert', 'created_at']
    search_fields = ['content', 'cve__cve_id', 'user__username']

