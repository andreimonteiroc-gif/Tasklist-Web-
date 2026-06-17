from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
   
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título da tarefa (máximo 200 caracteres)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada da tarefa"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Prioridade"
    )
    
    completed = models.BooleanField(
        default=False,
        verbose_name="Concluída"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Concluído em"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Usuário"
    )
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    def save(self, *args, **kwargs):
       
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    full_name = models.CharField(
        max_length=100,
        verbose_name="Nome Completo"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Cadastrado em"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        
    def __str__(self):
        return f"Perfil: {self.full_name}"


class TaskAttachment(models.Model):
    """Modelo para arquivos anexados a tarefas"""
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Tarefa"
    )
    
    file = models.FileField(
        upload_to='task_attachments/%Y/%m/%d/',
        verbose_name="Arquivo"
    )
    
    file_name = models.CharField(
        max_length=255,
        verbose_name="Nome do Arquivo"
    )
    
    file_size = models.IntegerField(
        verbose_name="Tamanho (bytes)"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Enviado em"
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Enviado por"
    )
    
    class Meta:
        verbose_name = "Anexo de Tarefa"
        verbose_name_plural = "Anexos de Tarefas"
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.file_name} - {self.task.title}"
