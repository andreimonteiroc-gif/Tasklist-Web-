from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
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