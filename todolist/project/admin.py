from django.contrib import admin
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'completed', 'created_by', 'created')
    list_filter = ('completed', 'created')
    search_fields = ('name', 'description')
