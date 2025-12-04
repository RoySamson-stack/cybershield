from django.contrib import admin
from .models import C2Server, OnionSite, OnionDataPost, LeakedCredential, ThreatIntelligence


@admin.register(C2Server)
class C2ServerAdmin(admin.ModelAdmin):
    list_display = ['domain', 'ip_address', 'c2_family', 'threat_level', 'is_active', 'last_seen']
    list_filter = ['threat_level', 'is_active', 'c2_family', 'country']
    search_fields = ['domain', 'ip_address', 'hostname', 'c2_family']


@admin.register(OnionSite)
class OnionSiteAdmin(admin.ModelAdmin):
    list_display = ['onion_address', 'site_type', 'title', 'is_active', 'last_checked']
    list_filter = ['site_type', 'is_active']
    search_fields = ['onion_address', 'title', 'description']


@admin.register(OnionDataPost)
class OnionDataPostAdmin(admin.ModelAdmin):
    list_display = ['post_title', 'onion_site', 'affected_organization', 'posted_date', 'discovered_date']
    list_filter = ['is_verified', 'posted_date']
    search_fields = ['post_title', 'affected_organization', 'onion_site__onion_address']


@admin.register(LeakedCredential)
class LeakedCredentialAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'domain', 'breach_source', 'leak_date', 'is_exposed']
    list_filter = ['is_exposed', 'is_verified', 'breach_source']
    search_fields = ['email', 'username', 'domain', 'breach_source']


@admin.register(ThreatIntelligence)
class ThreatIntelligenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'threat_type', 'severity', 'first_seen', 'is_verified']
    list_filter = ['threat_type', 'severity', 'is_verified']
    search_fields = ['title', 'description', 'source']

