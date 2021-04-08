import logging
from django.contrib import admin, messages
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from breathecode.admissions.admin import CohortAdmin
from .models import Asset

logger = logging.getLogger(__name__)

# Register your models here.
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug', 'user__email', 'cohort__slug']
    list_display = ('title', 'slug', 'lang', 'asset_type', 'url_path')
    list_filter = ['asset_type', 'lang']
    def url_path(self,obj):
        return format_html(f"<a rel='noopener noreferrer' target='_blank' href='{obj.url}'>open</a>")