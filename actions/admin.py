from django.contrib import admin
from .models import Action

# Register your models here.
@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'verb', 'content_type', 'object_id')
    list_filter = ('created',)
    search_fields = ('verb',)
