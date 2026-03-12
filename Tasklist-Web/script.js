
let currentUser = null;
let tasks = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadUserSession();
    loadTasks();
    updateUI();
});

// Authentication Functions
function showLogin() {
    window.location.href = 'login.html';
}

function showRegister() {
    window.location.href = 'login.html';
    setTimeout(() => showRegisterForm(), 100);
}

function showLoginForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const successMessage = document.getElementById('successMessage');
    
    if (loginForm) loginForm.classList.remove('hidden');
    if (registerForm) registerForm.classList.add('hidden');
    if (successMessage) successMessage.classList.add('hidden');
}

function showRegisterForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const successMessage = document.getElementById('successMessage');
    
    if (loginForm) loginForm.classList.add('hidden');
    if (registerForm) registerForm.classList.remove('hidden');
    if (successMessage) successMessage.classList.add('hidden');
}

function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Get users from localStorage
    const users = JSON.parse(localStorage.getItem('tasklistUsers') || '[]');
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
        currentUser = user;
        localStorage.setItem('tasklistCurrentUser', JSON.stringify(user));
        
        // Redirect to main page
        window.location.href = 'index.html';
    } else {
        alert('Email ou senha incorretos!');
    }
}

function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    
    // Validation
    if (password !== passwordConfirm) {
        alert('As senhas não coincidem!');
        return;
    }
    
    // Get existing users
    const users = JSON.parse(localStorage.getItem('tasklistUsers') || '[]');
    
    // Check if email already exists
    if (users.some(u => u.email === email)) {
        alert('Este email já está cadastrado!');
        return;
    }
    
    // Create new user
    const newUser = {
        id: Date.now().toString(),
        name: name,
        email: email,
        password: password,
        createdAt: new Date().toISOString()
    };
    
    users.push(newUser);
    localStorage.setItem('tasklistUsers', JSON.stringify(users));
    
    // Show success message
    showSuccessMessage();
}

function showSuccessMessage() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const successMessage = document.getElementById('successMessage');
    
    if (loginForm) loginForm.classList.add('hidden');
    if (registerForm) registerForm.classList.add('hidden');
    if (successMessage) successMessage.classList.remove('hidden');
}

function logout() {
    currentUser = null;
    localStorage.removeItem('tasklistCurrentUser');
    localStorage.removeItem('tasklistTasks');
    window.location.href = 'index.html';
}

function loadUserSession() {
    const saved = localStorage.getItem('tasklistCurrentUser');
    if (saved) {
        currentUser = JSON.parse(saved);
    }
}

// UI Update Functions
function updateUI() {
    const welcomeScreen = document.getElementById('welcomeScreen');
    const dashboard = document.getElementById('dashboard');
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    
    if (currentUser) {
        // User is logged in - show dashboard
        if (welcomeScreen) welcomeScreen.classList.add('hidden');
        if (dashboard) dashboard.classList.remove('hidden');
        if (userInfo) {
            userInfo.style.display = 'block';
            if (userName) userName.textContent = currentUser.name;
        }
        
        updateTasksDisplay();
        updateStats();
    } else {
        // User not logged in - show welcome screen
        if (welcomeScreen) welcomeScreen.classList.remove('hidden');
        if (dashboard) dashboard.classList.add('hidden');
        if (userInfo) userInfo.style.display = 'none';
    }
}

// Task Management Functions
function loadTasks() {
    if (!currentUser) return;
    
    const saved = localStorage.getItem(`tasklistTasks_${currentUser.id}`);
    if (saved) {
        tasks = JSON.parse(saved);
    }
}

function saveTasks() {
    if (!currentUser) return;
    
    localStorage.setItem(`tasklistTasks_${currentUser.id}`, JSON.stringify(tasks));
}

function addTask(event) {
    event.preventDefault();
    
    const titleInput = document.getElementById('taskTitle');
    const descriptionInput = document.getElementById('taskDescription');
    const prioritySelect = document.getElementById('taskPriority');
    
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const priority = prioritySelect.value;
    
    if (!title) {
        alert('Por favor, insira um título para a tarefa!');
        return;
    }
    
    const newTask = {
        id: Date.now().toString(),
        title: title,
        description: description,
        priority: priority,
        completed: false,
        createdAt: new Date().toISOString(),
        userId: currentUser.id
    };
    
    tasks.push(newTask);
    saveTasks();
    
    // Clear form
    titleInput.value = '';
    descriptionInput.value = '';
    prioritySelect.value = 'medium';
    
    updateTasksDisplay();
    updateStats();
    
    // Add animation
    setTimeout(() => {
        const taskElements = document.querySelectorAll('.task-item');
        if (taskElements.length > 0) {
            taskElements[0].classList.add('fade-in');
        }
    }, 100);
}

function toggleTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
        task.completed = !task.completed;
        task.completedAt = task.completed ? new Date().toISOString() : null;
        saveTasks();
        updateTasksDisplay();
        updateStats();
    }
}

function deleteTask(taskId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        tasks = tasks.filter(t => t.id !== taskId);
        saveTasks();
        updateTasksDisplay();
        updateStats();
    }
}

function editTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newTitle = prompt('Novo título:', task.title);
    if (newTitle && newTitle.trim()) {
        task.title = newTitle.trim();
        
        const newDescription = prompt('Nova descrição:', task.description);
        if (newDescription !== null) {
            task.description = newDescription.trim();
        }
        
        saveTasks();
        updateTasksDisplay();
    }
}

function filterTasks() {
    const filterSelect = document.getElementById('filterTasks');
    const filter = filterSelect.value;
    
    updateTasksDisplay(filter);
}

function clearCompleted() {
    const completedCount = tasks.filter(t => t.completed).length;
    
    if (completedCount === 0) {
        alert('Não há tarefas concluídas para limpar!');
        return;
    }
    
    if (confirm(`Excluir ${completedCount} tarefa(s) concluída(s)?`)) {
        tasks = tasks.filter(t => !t.completed);
        saveTasks();
        updateTasksDisplay();
        updateStats();
    }
}

function updateTasksDisplay(filter = 'all') {
    const tasksList = document.getElementById('tasksList');
    if (!tasksList) return;
    
    let filteredTasks = tasks;
    
    switch (filter) {
        case 'pending':
            filteredTasks = tasks.filter(t => !t.completed);
            break;
        case 'completed':
            filteredTasks = tasks.filter(t => t.completed);
            break;
        case 'high':
            filteredTasks = tasks.filter(t => t.priority === 'high');
            break;
    }
    
    // Sort by priority and creation date
    filteredTasks.sort((a, b) => {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
            return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        return new Date(b.createdAt) - new Date(a.createdAt);
    });
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = `
            <div class="text-center" style="padding: 2rem; color: var(--text-muted);">
                <p>📝 Nenhuma tarefa encontrada</p>
                <p style="font-size: 0.875rem;">Adicione uma nova tarefa para começar!</p>
            </div>
        `;
        return;
    }
    
    tasksList.innerHTML = filteredTasks.map(task => {
        const priorityIcon = {
            high: '🔴',
            medium: '🟡',
            low: '🟢'
        };
        
        const priorityText = {
            high: 'Alta',
            medium: 'Média',
            low: 'Baixa'
        };
        
        return `
            <div class="task-item ${task.completed ? 'completed' : ''}">
                <div class="task-content">
                    <div class="task-title">${task.title}</div>
                    ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                </div>
                <div class="flex items-center">
                    <span class="task-priority priority-${task.priority}">
                        ${priorityIcon[task.priority]} ${priorityText[task.priority]}
                    </span>
                    <div class="task-actions">
                        <button onclick="toggleTask('${task.id}')" class="btn-small ${task.completed ? 'btn-secondary' : ''}">
                            ${task.completed ? '↶ Reabrir' : '✅ Concluir'}
                        </button>
                        <button onclick="editTask('${task.id}')" class="btn-small btn-secondary">
                            ✏️ Editar
                        </button>
                        <button onclick="deleteTask('${task.id}')" class="btn-small" style="background: var(--error);">
                            🗑️ Excluir
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updateStats() {
    const totalTasksElement = document.getElementById('totalTasks');
    const completedTasksElement = document.getElementById('completedTasks');
    const pendingTasksElement = document.getElementById('pendingTasks');
    
    if (!totalTasksElement) return;
    
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.completed).length;
    const pendingTasks = totalTasks - completedTasks;
    
    totalTasksElement.textContent = totalTasks;
    completedTasksElement.textContent = completedTasks;
    pendingTasksElement.textContent = pendingTasks;
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export/Import Functions (bonus feature)
function exportTasks() {
    if (tasks.length === 0) {
        alert('Não há tarefas para exportar!');
        return;
    }
    
    const dataStr = JSON.stringify(tasks, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `tasklist-backup-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
}

function importTasks(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importedTasks = JSON.parse(e.target.result);
            
            if (confirm(`Importar ${importedTasks.length} tarefas? Isso irá adicionar às tarefas existentes.`)) {
                // Add user ID to imported tasks
                importedTasks.forEach(task => {
                    task.userId = currentUser.id;
                    task.id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
                });
                
                tasks = [...tasks, ...importedTasks];
                saveTasks();
                updateTasksDisplay();
                updateStats();
                
                alert('Tarefas importadas com sucesso!');
            }
        } catch (error) {
            alert('Erro ao importar arquivo. Verifique se é um arquivo válido.');
        }
    };
    reader.readAsText(file);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + N: Nova tarefa
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        const titleInput = document.getElementById('taskTitle');
        if (titleInput) titleInput.focus();
    }
    
    // Ctrl/Cmd + F: Filtrar tarefas
    if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
        event.preventDefault();
        const filterSelect = document.getElementById('filterTasks');
        if (filterSelect) filterSelect.focus();
    }
});

// Service Worker Registration (for PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Register service worker when we have one
        // navigator.serviceWorker.register('/sw.js');
    });
}

// Initialize demo data for new users
function initializeDemoData() {
    if (tasks.length === 0 && currentUser) {
        const demoTasks = [
            {
                id: 'demo1',
                title: 'Bem-vindo ao Tasklist! 🎉',
                description: 'Esta é uma tarefa de exemplo. Você pode editar, completar ou excluir.',
                priority: 'high',
                completed: false,
                createdAt: new Date().toISOString(),
                userId: currentUser.id
            },
            {
                id: 'demo2',
                title: 'Explore as funcionalidades',
                description: 'Teste adicionar novas tarefas, definir prioridades e filtrar por status.',
                priority: 'medium',
                completed: false,
                createdAt: new Date(Date.now() - 60000).toISOString(),
                userId: currentUser.id
            },
            {
                id: 'demo3',
                title: 'Tarefa concluída',
                description: 'Este é um exemplo de tarefa já concluída.',
                priority: 'low',
                completed: true,
                createdAt: new Date(Date.now() - 120000).toISOString(),
                completedAt: new Date(Date.now() - 30000).toISOString(),
                userId: currentUser.id
            }
        ];
        
        tasks = demoTasks;
        saveTasks();
    }
}

// Auto-initialize demo data on first login
setTimeout(() => {
    if (currentUser && tasks.length === 0) {
        initializeDemoData();
        updateTasksDisplay();
        updateStats();
    }
}, 500);