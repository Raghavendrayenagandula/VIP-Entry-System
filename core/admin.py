from django.contrib import admin
from .models import VIPVisitor, EntryExitLog

@admin.register(VIPVisitor)
class VIPVisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'organization', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('full_name', 'email', 'phone', 'pass_id')

@admin.register(EntryExitLog)
class EntryExitLogAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'action', 'timestamp')
    list_filter = ('action',)
    search_fields = ('visitor__full_name', 'visitor__pass_id')