"""
API Views (ViewSets) para Django REST Framework.
Implementa CRUD completo para tarefas e usuários.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone

from .models import Task, UserProfile, TaskAttachment
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskDetailSerializer,
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    TaskAttachmentSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usuários."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name']
    
    def get_serializer_class(self):
        """Retorna serializer diferente para criação."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Endpoint para registro de novo usuário."""
        payload = request.data.copy()
        base_username = (payload.get('username') or '').strip()
        if base_username:
            candidate = base_username
            suffix = 1
            while User.objects.filter(username=candidate).exists():
                candidate = f'{base_username}_{suffix}'
                suffix += 1
            payload['username'] = candidate

        serializer = UserCreateSerializer(data=payload)
        if serializer.is_valid():
            user = serializer.save()
            # Cria profile do usuário
            UserProfile.objects.create(
                user=user,
                full_name=request.data.get('first_name', user.username)
            )
            return Response(
                {
                    'message': 'Usuário registrado com sucesso!',
                    'user_id': user.id,
                    'username': user.username,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna dados do usuário autenticado."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """Muda senha do usuário."""
        user = self.get_object()
        
        # Apenas o próprio usuário pode mudar sua senha
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Você não tem permissão para mudar essa senha.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Senha antiga incorreta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Senha alterada com sucesso!'})


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar tarefas."""
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority', 'completed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Retorna apenas tarefas do usuário autenticado."""
        return Task.objects.filter(user=self.request.user).prefetch_related('attachments')
    
    def get_serializer_class(self):
        """Retorna serializer diferente baseado na ação."""
        if self.action == 'retrieve':
            return TaskDetailSerializer
        elif self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Associa tarefa ao usuário autenticado."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Marca tarefa como concluída."""
        task = self.get_object()
        task.completed = True
        task.completed_at = timezone.now()
        task.save()
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_incomplete(self, request, pk=None):
        """Marca tarefa como não concluída."""
        task = self.get_object()
        task.completed = False
        task.completed_at = None
        task.save()
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Retorna estatísticas das tarefas do usuário."""
        tasks = self.get_queryset()
        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        pending = total - completed
        
        # Tarefas por prioridade
        by_priority = {
            'high': tasks.filter(priority='high').count(),
            'medium': tasks.filter(priority='medium').count(),
            'low': tasks.filter(priority='low').count(),
        }
        
        return Response({
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'by_priority': by_priority,
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Retorna apenas tarefas pendentes."""
        tasks = self.get_queryset().filter(completed=False)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Retorna apenas tarefas concluídas."""
        tasks = self.get_queryset().filter(completed=True)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Retorna tarefas de alta prioridade."""
        tasks = self.get_queryset().filter(priority='high')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar anexos de tarefas."""
    
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Retorna apenas anexos de tarefas do usuário."""
        return TaskAttachment.objects.filter(task__user=self.request.user)
    
    def perform_create(self, serializer):
        """Salva arquivo e metadados."""
        file_obj = self.request.FILES['file']
        serializer.save(
            uploaded_by=self.request.user,
            file_size=file_obj.size,
            file_name=file_obj.name
        )
    
    @action(detail=False, methods=['get'])
    def by_task(self, request):
        """Retorna anexos de uma tarefa específica."""
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attachments = self.get_queryset().filter(task_id=task_id)
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar perfis de usuário."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas perfil do usuário autenticado."""
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna perfil do usuário autenticado."""
        profile = UserProfile.objects.get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
