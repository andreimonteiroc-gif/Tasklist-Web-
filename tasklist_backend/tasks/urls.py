from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import TaskViewSet, UserViewSet, TaskAttachmentViewSet, UserProfileViewSet

# Roteador para API REST
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'attachments', TaskAttachmentViewSet, basename='attachment')
router.register(r'profiles', UserProfileViewSet, basename='profile')

app_name = 'tasks'

urlpatterns = [
    # API REST v1
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # Views tradicionais (opcional, para compatibilidade)
    path('', views.task_list, name='task_list'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('new/', views.task_new, name='task_new'),
    path('edit/<int:task_id>/', views.task_edit, name='task_edit'),
    path('delete/<int:task_id>/', views.task_delete, name='task_delete'),
    path('complete/<int:task_id>/', views.task_complete, name='task_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
]