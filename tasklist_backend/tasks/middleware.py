"""
Middlewares customizados para autenticação e controle de acesso.
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from functools import wraps


class AuthenticationMiddleware:
    """
    Middleware para verificar autenticação e sessão.
    Redireciona usuários não autenticados para login.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_urls = [
            '/new/',
            '/edit/',
            '/delete/',
            '/complete/',
            '/dashboard/',
            '/profile/',
            '/search/',
        ]
    
    def __call__(self, request):
        # Verifica se a rota atual precisa autenticação
        for protected_url in self.protected_urls:
            if request.path.startswith(protected_url):
                if not request.user.is_authenticated:
                    return redirect('tasks:user_login')
        
        response = self.get_response(request)
        return response


class AccessControlMiddleware:
    """
    Middleware para validar permissões e controlar acesso a recursos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Adiciona informações de acesso ao request
        request.has_task_access = False
        
        if request.user.is_authenticated:
            request.has_task_access = True
        
        response = self.get_response(request)
        return response


def task_owner_required(function):
    """
    Decorador para garantir que apenas o dono da tarefa pode editá-la ou deletá-la.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        from tasks.models import Task
        
        task_id = kwargs.get('task_id')
        if not task_id:
            return redirect('tasks:task_list')
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return redirect('tasks:task_list')
        
        # Verifica se o usuário é o dono da tarefa
        if task.user != request.user:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Você não tem permissão para acessar esta tarefa.")
        
        return function(request, *args, **kwargs)
    
    return wrap


def session_activity_middleware():
    """
    Middleware para rastrear atividade de sessão.
    Útil para implementar timeout de sessão baseado em inatividade.
    """
    def middleware(get_response):
        def process_request(request):
            if request.user.is_authenticated:
                # Atualiza o timestamp da última atividade
                request.session['last_activity'] = __import__('time').time()
            
            response = get_response(request)
            return response
        
        return process_request
    
    return middleware
