from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from .models import Task, UserProfile
from django.db.models import Q


MOCK_TASKS = [
    {
        'id': 1,
        'title': 'Bem-vindo ao Tasklist Django! 🎉',
        'description': 'Esta é uma tarefa de exemplo criada no backend Django.',
        'priority': 'high',
        'completed': False,
        'created_at': '2025-10-24T10:00:00Z',
        'user_id': 1,
    },
    {
        'id': 2,
        'title': 'Implementar CRUD completo',
        'description': 'Criar, editar, visualizar e excluir tarefas no Django.',
        'priority': 'medium',
        'completed': False,
        'created_at': '2025-10-24T11:30:00Z',
        'user_id': 1,
    },
    {
        'id': 3,
        'title': 'Configurar templates Django',
        'description': 'Integrar o HTML/CSS existente com templates Django.',
        'priority': 'medium',
        'completed': True,
        'created_at': '2025-10-24T09:15:00Z',
        'user_id': 1,
    },
    {
        'id': 4,
        'title': 'Validação de formulários',
        'description': 'Implementar validações server-side para todos os formulários.',
        'priority': 'high',
        'completed': False,
        'created_at': '2025-10-24T14:20:00Z',
        'user_id': 1,
    },
    {
        'id': 5,
        'title': 'Rotas amigáveis configuradas',
        'description': 'URLs semânticas como /tasks/edit/5/ funcionando.',
        'priority': 'low',
        'completed': True,
        'created_at': '2025-10-24T08:45:00Z',
        'user_id': 1,
    }
]

MOCK_USERS = [
    {
        'id': 1,
        'username': 'admin',
        'email': 'admin@tasklist.com',
        'password': 'admin123',
        'name': 'Administrador'
    },
    {
        'id': 2,
        'username': 'user',
        'email': 'user@tasklist.com', 
        'password': 'user123',
        'name': 'Usuário Teste'
    }
]

def task_list(request):
    if request.user.is_authenticated:
        tasks_queryset = Task.objects.filter(user=request.user)
        filter_type = request.GET.get('filter', 'all')
        if filter_type == 'completed':
            tasks_queryset = tasks_queryset.filter(completed=True)
        elif filter_type == 'pending':
            tasks_queryset = tasks_queryset.filter(completed=False)
        elif filter_type == 'high':
            tasks_queryset = tasks_queryset.filter(priority='high')
        
        tasks = tasks_queryset
        all_tasks = Task.objects.filter(user=request.user)
        total_tasks = all_tasks.count()
        completed_tasks = all_tasks.filter(completed=True).count()
        pending_tasks = total_tasks - completed_tasks
    else:
        tasks = MOCK_TASKS
        filter_type = request.GET.get('filter', 'all')
        if filter_type == 'completed':
            tasks = [t for t in tasks if t['completed']]
        elif filter_type == 'pending':
            tasks = [t for t in tasks if not t['completed']]
        elif filter_type == 'high':
            tasks = [t for t in tasks if t['priority'] == 'high']
        total_tasks = len(MOCK_TASKS)
        completed_tasks = len([t for t in MOCK_TASKS if t['completed']])
        pending_tasks = total_tasks - completed_tasks
    
    context = {
        'tasks': tasks,
        'filter_type': filter_type,
        'stats': {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks
        }
    }
    return render(request, 'tasks/task_list.html', context)

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth:
                login(request, user_auth)
                messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                return redirect('tasks:task_list')
            else:
                messages.error(request, 'Senha incorreta!')
        except User.DoesNotExist:
            messages.error(request, 'Email não encontrado!')
    
    return render(request, 'tasks/login.html')

def user_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        errors = []
        if not name or len(name.strip()) < 2:
            errors.append('Nome deve ter pelo menos 2 caracteres.')
        if not email or '@' not in email:
            errors.append('Email inválido.')
        if not password or len(password) < 6:
            errors.append('Senha deve ter pelo menos 6 caracteres.')
        if password != password_confirm:
            errors.append('Senhas não coincidem.')
        if User.objects.filter(email=email).exists():
            errors.append('Este email já está cadastrado.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{User.objects.count()}"
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                UserProfile.objects.create(
                    user=user,
                    full_name=name
                )
                messages.success(request, 'Conta criada com sucesso! Faça login.')
                return redirect('tasks:user_login')
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'tasks/register.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('tasks:user_login')

@login_required
def task_new(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'medium')
        if not title or len(title.strip()) < 3:
            messages.error(request, 'Título deve ter pelo menos 3 caracteres.')
        else:
            try:
                task = Task.objects.create(
                    title=title.strip(),
                    description=description.strip() if description else '',
                    priority=priority,
                    user=request.user
                )
                messages.success(request, f'Tarefa "{task.title}" criada com sucesso!')
                return redirect('tasks:task_list')
            except Exception as e:
                messages.error(request, f'Erro ao criar tarefa: {str(e)}')
    
    return render(request, 'tasks/task_form.html', {'action': 'Criar'})

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        if not title or len(title.strip()) < 3:
            messages.error(request, 'Título deve ter pelo menos 3 caracteres.')
        else:
            try:
                task.title = title.strip()
                task.description = description.strip() if description else ''
                task.priority = priority
                task.save()
                messages.success(request, f'Tarefa "{task.title}" atualizada com sucesso!')
                return redirect('tasks:task_list')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar tarefa: {str(e)}')
    
    return render(request, 'tasks/task_form.html', {'task': task, 'action': 'Editar'})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        try:
            task_title = task.title
            task.delete()
            messages.success(request, f'Tarefa "{task_title}" excluída com sucesso!')
            return redirect('tasks:task_list')
        except Exception as e:
            messages.error(request, f'Erro ao excluir tarefa: {str(e)}')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    try:
        task.completed = not task.completed
        task.save()
        status = 'concluída' if task.completed else 'reaberta'
        messages.success(request, f'Tarefa "{task.title}" {status}!')
    except Exception as e:
        messages.error(request, f'Erro ao atualizar tarefa: {str(e)}')
    
    return redirect('tasks:task_list')

@login_required
def dashboard(request):
    # Estatísticas avançadas do banco de dados
    all_tasks = Task.objects.filter(user=request.user)
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    high_priority = all_tasks.filter(priority='high').count()
    
    # Tarefas por prioridade
    priority_stats = {
        'high': all_tasks.filter(priority='high').count(),
        'medium': all_tasks.filter(priority='medium').count(),
        'low': all_tasks.filter(priority='low').count(),
    }
    
    # Tarefas mais recentes
    recent_tasks = all_tasks.order_by('-created_at')[:3]
    
    context = {
        'stats': {
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks,
            'high_priority': high_priority,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        },
        'priority_stats': priority_stats,
        'recent_tasks': recent_tasks
    }
    return render(request, 'tasks/dashboard.html', context)

def home(request):
    return redirect('tasks:task_list')

@login_required  
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            full_name=f"{request.user.first_name} {request.user.last_name}".strip()
        )
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        if full_name and len(full_name.strip()) >= 2:
            user_profile.full_name = full_name.strip()
            user_profile.save()
            names = full_name.strip().split()
            request.user.first_name = names[0] if names else ''
            request.user.last_name = ' '.join(names[1:]) if len(names) > 1 else ''
            request.user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
        else:
            messages.error(request, 'Nome deve ter pelo menos 2 caracteres.')
    context = {
        'user_profile': user_profile,
        'user': request.user
    }
    return render(request, 'tasks/profile.html', context)

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    tasks = []
    if query:
        tasks = Task.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-created_at')
    context = {
        'tasks': tasks,
        'query': query,
        'total_results': tasks.count() if query else 0
    }
    return render(request, 'tasks/search.html', context)