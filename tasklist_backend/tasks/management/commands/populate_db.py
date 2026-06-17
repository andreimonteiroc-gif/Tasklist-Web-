"""
Comando para popular o banco de dados com dados de teste.

Uso: python manage.py populate_db
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Task, UserProfile


class Command(BaseCommand):
    """Comando para popular banco de dados com dados de teste."""
    
    help = 'Popula o banco de dados com usuários e tarefas de teste'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('🌱 Iniciando população do banco de dados...'))
        
        # Cria usuários
        users = self.create_users()
        
        # Cria tarefas
        self.create_tasks(users)
        
        self.stdout.write(self.style.SUCCESS('✅ Banco de dados população concluída!'))
    
    def clear_data(self):
        """Remove dados existentes."""
        self.stdout.write('🗑️  Limpando dados existentes...')
        Task.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(username__in=['admin', 'user1', 'user2', 'user3']).delete()
        self.stdout.write(self.style.SUCCESS('✅ Dados limpos'))
    
    def create_users(self):
        """Cria usuários de teste."""
        self.stdout.write('👥 Criando usuários de teste...')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@tasklist.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'Tasklist',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'user1',
                'email': 'user1@tasklist.com',
                'password': 'user123',
                'first_name': 'João',
                'last_name': 'Silva',
            },
            {
                'username': 'user2',
                'email': 'user2@tasklist.com',
                'password': 'user123',
                'first_name': 'Maria',
                'last_name': 'Santos',
            },
            {
                'username': 'user3',
                'email': 'user3@tasklist.com',
                'password': 'user123',
                'first_name': 'Pedro',
                'last_name': 'Oliveira',
            },
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'  ✓ Usuário {user_data["username"]} criado')
            
            # Cria ou atualiza perfil
            full_name = f"{user.first_name} {user.last_name}".strip()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'full_name': full_name}
            )
            
            users.append(user)
        
        return users
    
    def create_tasks(self, users):
        """Cria tarefas de teste para os usuários."""
        self.stdout.write('📋 Criando tarefas de teste...')
        
        tasks_data = [
            # Tarefas para admin
            {
                'user_index': 0,
                'title': 'Setup inicial do projeto',
                'description': 'Configurar Django, banco de dados e estrutura base',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 0,
                'title': 'Implementar autenticação',
                'description': 'Sistema de login, registro e logout',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 0,
                'title': 'CRUD de tarefas',
                'description': 'Criar, ler, atualizar e deletar tarefas',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 0,
                'title': 'Implementar middlewares',
                'description': 'Controle de acesso e validação de autenticação',
                'priority': 'medium',
                'completed': True,
            },
            {
                'user_index': 0,
                'title': 'Deploy em servidor',
                'description': 'Subir aplicação para produção',
                'priority': 'high',
                'completed': False,
            },
            
            # Tarefas para user1
            {
                'user_index': 1,
                'title': 'Estudar Django',
                'description': 'Aprender conceitos fundamentais de Django',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 1,
                'title': 'Criar models do banco',
                'description': 'Definir estrutura de dados',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 1,
                'title': 'Escrever testes',
                'description': 'Testes unitários para CRUD',
                'priority': 'medium',
                'completed': False,
            },
            {
                'user_index': 1,
                'title': 'Documentação',
                'description': 'Criar README e documentação técnica',
                'priority': 'medium',
                'completed': False,
            },
            
            # Tarefas para user2
            {
                'user_index': 2,
                'title': 'Comprar livro de Django',
                'description': 'Two Scoops of Django',
                'priority': 'low',
                'completed': True,
            },
            {
                'user_index': 2,
                'title': 'Completar curso online',
                'description': 'Udemy - Django for Beginners',
                'priority': 'medium',
                'completed': False,
            },
            {
                'user_index': 2,
                'title': 'Fazer projeto prático',
                'description': 'Criar projeto pessoal com Django',
                'priority': 'medium',
                'completed': False,
            },
            
            # Tarefas para user3
            {
                'user_index': 3,
                'title': 'Setup do ambiente Python',
                'description': 'Instalar Python 3.11 e virtualenv',
                'priority': 'high',
                'completed': True,
            },
            {
                'user_index': 3,
                'title': 'Explorar ORM do Django',
                'description': 'Aprender QuerySets e operações básicas',
                'priority': 'high',
                'completed': False,
            },
            {
                'user_index': 3,
                'title': 'Integrar com PostgreSQL',
                'description': 'Migrar de SQLite para PostgreSQL',
                'priority': 'medium',
                'completed': False,
            },
        ]
        
        created_count = 0
        for task_data in tasks_data:
            user = users[task_data['user_index']]
            task, created = Task.objects.get_or_create(
                user=user,
                title=task_data['title'],
                defaults={
                    'description': task_data['description'],
                    'priority': task_data['priority'],
                    'completed': task_data['completed'],
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'  ✓ {created_count} tarefas criadas')
        self.stdout.write(
            f'  ℹ️  Total de tarefas no banco: {Task.objects.count()}'
        )
