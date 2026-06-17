"""
Serializers para conversão de modelos para JSON (suporte a API).
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, UserProfile, TaskAttachment


class UserSerializer(serializers.ModelSerializer):
    """Serializer para modelo User."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuário."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer para tarefas."""
    
    user = UserSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'completed', 'user', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'user']
    
    def validate_title(self, value):
        """Valida título da tarefa."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError('Título deve ter pelo menos 3 caracteres.')
        return value.strip()
    
    def validate_priority(self, value):
        """Valida prioridade."""
        valid_priorities = ['low', 'medium', 'high']
        if value not in valid_priorities:
            raise serializers.ValidationError(f'Prioridade deve ser uma de: {valid_priorities}')
        return value
    
    def create(self, validated_data):
        """Cria nova tarefa associada ao usuário autenticado."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Atualiza tarefa existente."""
        # Garante que o usuário não tente mudar o dono da tarefa
        validated_data.pop('user', None)
        return super().update(instance, validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de tarefas."""
    
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'priority_display', 'completed',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para visualização de tarefa individual."""
    
    user = UserSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'completed', 'user', 'created_at', 'updated_at', 'completed_at',
            'completion_percentage'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'user']
    
    def get_completion_percentage(self, obj):
        """Calcula percentual de conclusão (útil para estatísticas)."""
        if obj.completed:
            return 100
        return 0


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuário."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password', 'password_confirm']
    
    def validate(self, data):
        """Valida que as senhas coincidem."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'As senhas não coincidem.'})
        return data
    
    def validate_email(self, value):
        """Valida email único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email já está registrado.')
        return value
    
    def validate_username(self, value):
        """Valida username único."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nome de usuário já existe.')
        return value
    
    def create(self, validated_data):
        """Cria novo usuário."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer para anexos de tarefas."""
    
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'file_name', 'file_size', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'file_size', 'uploaded_at', 'uploaded_by']
    
    def validate_file(self, value):
        """Valida arquivo (máximo 10MB)."""
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Arquivo não pode ser maior que 10MB.')
        return value
