"""
Testes para modelos e views da aplicação Tasklist.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Task, UserProfile


class TaskModelTestCase(TestCase):
    """Testes para o modelo Task."""
    
    def setUp(self):
        """Setup: cria usuário e tarefa para testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.task = Task.objects.create(
            title='Tarefa de Teste',
            description='Descrição da tarefa',
            priority='high',
            user=self.user
        )
    
    def test_task_creation(self):
        """Testa criação de uma tarefa."""
        self.assertEqual(self.task.title, 'Tarefa de Teste')
        self.assertEqual(self.task.user, self.user)
        self.assertFalse(self.task.completed)
    
    def test_task_str(self):
        """Testa representação em string da tarefa."""
        expected = f"Tarefa de Teste (Alta)"
        self.assertEqual(str(self.task), expected)
    
    def test_task_priority_choices(self):
        """Testa opções de prioridade."""
        low_task = Task.objects.create(
            title='Baixa Prioridade',
            priority='low',
            user=self.user
        )
        self.assertEqual(low_task.get_priority_display(), 'Baixa')
    
    def test_task_completed_marks_date(self):
        """Testa se completar tarefa registra data."""
        self.task.completed = True
        self.task.save()
        self.assertIsNotNone(self.task.completed_at)


class UserAuthenticationTestCase(TestCase):
    """Testes para autenticação de usuários."""
    
    def setUp(self):
        """Setup: cria cliente HTTP e usuário."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login_valid(self):
        """Testa login com credenciais válidas."""
        response = self.client.post(reverse('tasks:user_login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirecionamento para task_list
    
    def test_user_login_invalid_password(self):
        """Testa login com senha incorreta."""
        response = self.client.post(reverse('tasks:user_login'), {
            'email': 'test@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Mantém na página de login
    
    def test_user_register(self):
        """Testa registro de novo usuário."""
        response = self.client.post(reverse('tasks:user_register'), {
            'name': 'Novo Usuário',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        })
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())


class TaskCRUDTestCase(TestCase):
    """Testes para CRUD de tarefas."""
    
    def setUp(self):
        """Setup: cria usuário autenticado e tarefa."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.task = Task.objects.create(
            title='Tarefa Original',
            description='Descrição original',
            priority='medium',
            user=self.user
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_task_list_authenticated(self):
        """Testa listagem de tarefas para usuário autenticado."""
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarefa Original')
    
    def test_task_list_unauthenticated(self):
        """Testa listagem com mock data para usuário não autenticado."""
        self.client.logout()
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_task_create(self):
        """Testa criação de nova tarefa."""
        response = self.client.post(reverse('tasks:task_new'), {
            'title': 'Nova Tarefa',
            'description': 'Descrição nova',
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Nova Tarefa').exists())
    
    def test_task_edit(self):
        """Testa edição de tarefa existente."""
        response = self.client.post(
            reverse('tasks:task_edit', args=[self.task.id]),
            {
                'title': 'Tarefa Editada',
                'description': 'Descrição editada',
                'priority': 'high'
            }
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Tarefa Editada')
    
    def test_task_delete(self):
        """Testa deleção de tarefa."""
        task_id = self.task.id
        self.client.post(reverse('tasks:task_delete', args=[task_id]))
        self.assertFalse(Task.objects.filter(id=task_id).exists())
    
    def test_task_complete_toggle(self):
        """Testa alteração de status de conclusão."""
        self.assertFalse(self.task.completed)
        self.client.get(reverse('tasks:task_complete', args=[self.task.id]))
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
    
    def test_task_filter_by_priority(self):
        """Testa filtro de tarefas por prioridade."""
        response = self.client.get(reverse('tasks:task_list'), {'filter': 'high'})
        self.assertEqual(response.status_code, 200)
    
    def test_task_search(self):
        """Testa busca de tarefas."""
        response = self.client.get(reverse('tasks:search'), {'q': 'Original'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarefa Original')


class TaskAccessControlTestCase(TestCase):
    """Testes para controle de acesso."""
    
    def setUp(self):
        """Setup: cria dois usuários e tarefas."""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.task1 = Task.objects.create(
            title='Tarefa do Usuário 1',
            user=self.user1
        )
    
    def test_user_cannot_edit_other_user_task(self):
        """Testa que usuário não pode editar tarefa de outro."""
        self.client.login(username='user2', password='pass123')
        response = self.client.post(
            reverse('tasks:task_edit', args=[self.task1.id]),
            {'title': 'Tarefa Hackeada', 'priority': 'high'}
        )
        # Deve redirecionar ou mostrar erro
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Tarefa do Usuário 1')
    
    def test_authenticated_user_required_for_edit(self):
        """Testa que usuário não autenticado não pode editar."""
        response = self.client.get(reverse('tasks:task_edit', args=[self.task1.id]))
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)


class DashboardTestCase(TestCase):
    """Testes para dashboard."""
    
    def setUp(self):
        """Setup: cria usuário com múltiplas tarefas."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Cria tarefas com diferentes status e prioridades
        Task.objects.create(title='Tarefa 1', priority='high', user=self.user)
        Task.objects.create(title='Tarefa 2', priority='medium', user=self.user, completed=True)
        Task.objects.create(title='Tarefa 3', priority='low', user=self.user)
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_statistics(self):
        """Testa se dashboard mostra estatísticas corretas."""
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['total'], 3)
        self.assertEqual(response.context['stats']['completed'], 1)
        self.assertEqual(response.context['stats']['pending'], 2)
