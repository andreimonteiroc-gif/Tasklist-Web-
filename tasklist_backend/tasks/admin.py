from django.contrib import admin
from .models import Task, UserProfile, TaskAttachment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'completed', 'user', 'created_at']
    list_filter = ['priority', 'completed', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['completed', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'created_at']
    search_fields = ['full_name', 'user__username', 'user__email']
    ordering = ['-created_at']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'task', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'task']
    search_fields = ['file_name', 'task__title']
    readonly_fields = ['file_size', 'uploaded_at', 'uploaded_by']
    ordering = ['-uploaded_at']
