
const API_URL = 'http://localhost:8000/api/v1';
let currentUser = null;
let tasks = [];
let authToken = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadUserSession();
    if (currentUser) {
        loadTasks();
    }
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

function getAuthHeaders(username, password) {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${btoa(username + ':' + password)}`
    };
}

function loadUserProfile(username, password) {
    return fetch(`${API_URL}/users/me/`, {
        method: 'GET',
        headers: getAuthHeaders(username, password)
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Falha ao carregar perfil do usuário');
        }
        return response.json();
    });
}

function showEditDialog(title, fields) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.inset = '0';
        overlay.style.background = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = '9999';

        const dialog = document.createElement('div');
        dialog.style.background = '#fff';
        dialog.style.padding = '1rem';
        dialog.style.borderRadius = '10px';
        dialog.style.width = 'min(480px, 92vw)';
        dialog.style.boxShadow = '0 12px 36px rgba(0,0,0,0.2)';

        const heading = document.createElement('h3');
        heading.textContent = title;
        heading.style.margin = '0 0 0.75rem 0';
        dialog.appendChild(heading);

        const controls = {};
        fields.forEach((field) => {
            const label = document.createElement('label');
            label.textContent = field.label;
            label.style.display = 'block';
            label.style.margin = '0.5rem 0 0.25rem';
            dialog.appendChild(label);

            let control;
            if (field.type === 'select') {
                control = document.createElement('select');
                field.options.forEach((option) => {
                    const optionEl = document.createElement('option');
                    optionEl.value = option.value;
                    optionEl.textContent = option.label;
                    if (option.value === field.value) {
                        optionEl.selected = true;
                    }
                    control.appendChild(optionEl);
                });
            } else {
                control = document.createElement('input');
                control.type = field.type || 'text';
                control.value = field.value || '';
                if (field.placeholder) {
                    control.placeholder = field.placeholder;
                }
            }

            control.style.width = '100%';
            control.style.padding = '0.6rem';
            control.style.border = '1px solid #ccc';
            control.style.borderRadius = '8px';

            controls[field.key] = control;
            dialog.appendChild(control);
        });

        const actions = document.createElement('div');
        actions.style.display = 'flex';
        actions.style.justifyContent = 'flex-end';
        actions.style.gap = '0.5rem';
        actions.style.marginTop = '1rem';

        const cancelButton = document.createElement('button');
        cancelButton.type = 'button';
        cancelButton.textContent = 'Cancelar';
        cancelButton.onclick = () => {
            document.body.removeChild(overlay);
            resolve(null);
        };

        const saveButton = document.createElement('button');
        saveButton.type = 'button';
        saveButton.textContent = 'Salvar';
        saveButton.onclick = () => {
            const values = {};
            fields.forEach((field) => {
                values[field.key] = controls[field.key].value;
            });
            document.body.removeChild(overlay);
            resolve(values);
        };

        actions.appendChild(cancelButton);
        actions.appendChild(saveButton);
        dialog.appendChild(actions);
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
    });
}

function handleLogin(event) {
    event.preventDefault();
    
    const loginInput = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!loginInput || !password) {
        alert('Por favor, preencha email/usuário e senha!');
        return;
    }

    const loginForm = document.querySelector('#loginForm form');
    if (loginForm) {
        loginForm.style.opacity = '0.6';
        loginForm.style.pointerEvents = 'none';
    }

    // Tenta autenticar direto com o valor informado (username)
    const tryDirectAuth = fetch(`${API_URL}/tasks/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${btoa(loginInput + ':' + password)}`
        }
    });

    tryDirectAuth
        .then(async (response) => {
            if (response.ok) {
                return { username: loginInput };
            }

            // Se não autenticou e parece email, tenta resolver username pelo backend
            if (!loginInput.includes('@')) {
                throw new Error('Usuário ou senha inválidos.');
            }

            const usersResponse = await fetch(`${API_URL}/users/?search=${encodeURIComponent(loginInput)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!usersResponse.ok) {
                throw new Error('Não foi possível validar o login.');
            }

            const usersData = await usersResponse.json();
            const users = Array.isArray(usersData) ? usersData : (usersData.results || []);
            const found = users.find((u) => (u.email || '').toLowerCase() === loginInput.toLowerCase());

            if (!found || !found.username) {
                throw new Error('Usuário não encontrado para este email.');
            }

            const usernameFromEmail = found.username;
            const authResponse = await fetch(`${API_URL}/tasks/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${btoa(usernameFromEmail + ':' + password)}`
                }
            });

            if (!authResponse.ok) {
                throw new Error('Usuário ou senha inválidos.');
            }

            return { username: usernameFromEmail };
        })
        .then(async ({ username }) => {
            const userData = await loadUserProfile(username, password)
                .catch(() => ({ username: username, first_name: username, email: loginInput.includes('@') ? loginInput : '' }));

            localStorage.setItem('tasklistUsername', username);
            localStorage.setItem('tasklistPassword', password);
            currentUser = {
                username: userData.username || username,
                name: userData.first_name || userData.username || username,
                email: userData.email || '',
                id: userData.id || username
            };
            localStorage.setItem('tasklistCurrentUser', JSON.stringify(currentUser));
            window.location.href = 'index.html';
        })
        .catch((error) => {
            alert(error.message || 'Erro ao fazer login.');
            if (loginForm) {
                loginForm.style.opacity = '1';
                loginForm.style.pointerEvents = 'auto';
            }
        });
}

function handleRegister(event) {
    event.preventDefault();
    
    const fullName = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    
    // Validation
    if (password !== passwordConfirm) {
        alert('As senhas não coincidem!');
        return;
    }
    
    if (password.length < 6) {
        alert('A senha deve ter no mínimo 6 caracteres!');
        return;
    }
    
    // Gerar username a partir do email (pegar parte antes do @)
    const username = email.split('@')[0];
    
    // Faz registro usando a API Django
    const registerForm = document.querySelector('#registerForm form');
    registerForm.style.opacity = '0.6';
    registerForm.style.pointerEvents = 'none';
    
    fetch(`${API_URL}/users/register/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            password_confirm: passwordConfirm,
            first_name: fullName
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(JSON.stringify(data));
            });
        }
        return response.json();
    })
    .then(data => {
        const registeredUsername = data.username || username;
        alert(`Conta criada com sucesso! Username: ${registeredUsername}`);
        
        // Salvar credenciais e fazer login automático
        localStorage.setItem('tasklistUsername', registeredUsername);
        localStorage.setItem('tasklistPassword', password);
        localStorage.setItem('tasklistCurrentUser', JSON.stringify({
            username: registeredUsername,
            name: registeredUsername,
            id: registeredUsername
        }));
        
        // Redirecionar para dashboard
        window.location.href = 'index.html';
    })
    .catch(error => {
        console.error('Erro ao registrar:', error);
        try {
            const errorData = JSON.parse(error.message);
            const errorMsg = Object.entries(errorData)
                .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                .join('\n');
            alert('Erro ao registrar:\n' + errorMsg);
        } catch (e) {
            alert('Erro ao registrar: ' + error.message);
        }
        registerForm.style.opacity = '1';
        registerForm.style.pointerEvents = 'auto';
        registerForm.style.opacity = '1';
        registerForm.style.pointerEvents = 'auto';
    });
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
    localStorage.removeItem('tasklistUsername');
    localStorage.removeItem('tasklistPassword');
    localStorage.removeItem('tasklistTasks');
    window.location.href = 'index.html';
}

function loadUserSession() {
    const saved = localStorage.getItem('tasklistCurrentUser');
    if (saved) {
        currentUser = JSON.parse(saved);
        if (currentUser && !currentUser.name) {
            currentUser.name = currentUser.username || 'Usuário';
        }
    }
    
    // Também verificar se as credenciais existem
    const username = localStorage.getItem('tasklistUsername');
    const password = localStorage.getItem('tasklistPassword');
    
    if (!username || !password) {
        currentUser = null;
    }
}

function isAuthErrorStatus(status) {
    return status === 401 || status === 403;
}

function handleAuthFailure() {
    alert('Sua sessão expirou ou as credenciais estão inválidas. Faça login novamente.');
    logout();
}

// UI Update Functions
function updateUI() {
    const welcomeScreen = document.getElementById('welcomeScreen');
    const dashboard = document.getElementById('dashboard');
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    const navLinks = document.getElementById('navLinks');
    
    if (currentUser) {
        // User is logged in - show dashboard
        if (welcomeScreen) welcomeScreen.classList.add('hidden');
        if (dashboard) dashboard.classList.remove('hidden');
        if (userInfo) {
            userInfo.style.display = 'block';
            if (userName) userName.textContent = currentUser.name;
        }
        if (navLinks) navLinks.style.display = 'flex';
        
        updateTasksDisplay();
        updateStats();
    } else {
        // User not logged in - show welcome screen
        if (welcomeScreen) welcomeScreen.classList.remove('hidden');
        if (dashboard) dashboard.classList.add('hidden');
        if (userInfo) userInfo.style.display = 'none';
        if (navLinks) navLinks.style.display = 'none';
    }
}

// Task Management Functions
function loadTasks() {
    if (!currentUser) return;
    
    const username = localStorage.getItem('tasklistUsername');
    const password = localStorage.getItem('tasklistPassword');
    
    if (!username || !password) return;
    
    fetch(`${API_URL}/tasks/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${btoa(username + ':' + password)}`
        }
    })
    .then(response => {
        if (isAuthErrorStatus(response.status)) {
            throw new Error('AUTH_ERROR');
        }
        if (!response.ok) throw new Error('Erro ao carregar tarefas');
        return response.json();
    })
    .then(data => {
        tasks = Array.isArray(data) ? data : (data.results || []);
        updateTasksDisplay();
        updateStats();
    })
    .catch(error => {
        console.error('Erro ao carregar tarefas:', error);

        if (error.message === 'AUTH_ERROR') {
            handleAuthFailure();
            return;
        }

        // Fallback para localStorage se a API falhar
        const saved = localStorage.getItem(`tasklistTasks_${currentUser.id}`);
        if (saved) {
            tasks = JSON.parse(saved);
            updateTasksDisplay();
            updateStats();
        }
    });
}

function saveTasks() {
    // Não é necessário salvar manualmente quando usando API
    // A API Django gerencia os dados
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

    if (title.length < 3) {
        alert('O título da tarefa deve ter pelo menos 3 caracteres.');
        return;
    }
    
    const username = localStorage.getItem('tasklistUsername');
    const password = localStorage.getItem('tasklistPassword');
    
    if (!username || !password) {
        alert('Você precisa estar autenticado!');
        return;
    }
    
    // Cria tarefa via API
    fetch(`${API_URL}/tasks/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${btoa(username + ':' + password)}`
        },
        body: JSON.stringify({
            title: title,
            description: description,
            priority: priority,
            completed: false
        })
    })
    .then(response => {
        if (isAuthErrorStatus(response.status)) {
            throw new Error('AUTH_ERROR');
        }
        if (!response.ok) {
            return response.json()
                .then((data) => {
                    const details = Object.values(data || {})
                        .flat()
                        .join(' ')
                        .trim();
                    throw new Error(details || 'Erro ao criar tarefa');
                })
                .catch(() => {
                    throw new Error('Erro ao criar tarefa');
                });
        }
        return response.json();
    })
    .then(newTask => {
        tasks.unshift(newTask);
        
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
    })
    .catch(error => {
        console.error('Erro ao adicionar tarefa:', error);
        if (error.message === 'AUTH_ERROR') {
            handleAuthFailure();
            return;
        }
        alert(error.message || 'Erro ao criar tarefa. Tente novamente.');
    });
}

function toggleTask(taskId) {
    const task = tasks.find(t => String(t.id) === String(taskId));
    if (!task) return;
    
    const username = localStorage.getItem('tasklistUsername');
    const password = localStorage.getItem('tasklistPassword');
    
    if (!username || !password) {
        alert('Você precisa estar autenticado!');
        return;
    }
    
    const endpoint = task.completed ? 'mark_incomplete' : 'mark_complete';
    
    fetch(`${API_URL}/tasks/${taskId}/${endpoint}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Basic ${btoa(username + ':' + password)}`
        }
    })
    .then(response => {
        if (isAuthErrorStatus(response.status)) {
            throw new Error('AUTH_ERROR');
        }
        if (!response.ok) throw new Error('Erro ao atualizar tarefa');
        return response.json();
    })
    .then(updatedTask => {
        task.completed = updatedTask.completed;
        task.completed_at = updatedTask.completed_at;
        updateTasksDisplay();
        updateStats();
    })
    .catch(error => {
        console.error('Erro ao atualizar tarefa:', error);
        if (error.message === 'AUTH_ERROR') {
            handleAuthFailure();
            return;
        }
        alert('Erro ao atualizar tarefa. Tente novamente.');
    });
}

function deleteTask(taskId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        const username = localStorage.getItem('tasklistUsername');
        const password = localStorage.getItem('tasklistPassword');
        
        if (!username || !password) {
            alert('Você precisa estar autenticado!');
            return;
        }
        
        fetch(`${API_URL}/tasks/${taskId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Basic ${btoa(username + ':' + password)}`
            }
        })
        .then(response => {
            if (isAuthErrorStatus(response.status)) {
                throw new Error('AUTH_ERROR');
            }
            if (!response.ok) throw new Error('Erro ao deletar tarefa');
            tasks = tasks.filter(t => String(t.id) !== String(taskId));
            updateTasksDisplay();
            updateStats();
        })
        .catch(error => {
            console.error('Erro ao deletar tarefa:', error);
            if (error.message === 'AUTH_ERROR') {
                handleAuthFailure();
                return;
            }
            alert('Erro ao deletar tarefa. Verifique usuário/senha e tente novamente.');
        });
    }
}

async function editTask(taskId) {
    const task = tasks.find(t => String(t.id) === String(taskId));
    if (!task) return;
    
    const username = localStorage.getItem('tasklistUsername');
    const password = localStorage.getItem('tasklistPassword');
    
    if (!username || !password) {
        alert('Você precisa estar autenticado!');
        return;
    }
    
    const edited = await showEditDialog('Editar tarefa', [
        {
            key: 'title',
            label: 'Título',
            type: 'text',
            value: task.title || '',
            placeholder: 'Título da tarefa'
        },
        {
            key: 'description',
            label: 'Descrição',
            type: 'text',
            value: task.description || '',
            placeholder: 'Descrição da tarefa'
        },
        {
            key: 'priority',
            label: 'Prioridade',
            type: 'select',
            value: task.priority || 'medium',
            options: [
                { value: 'low', label: '🟢 Baixa' },
                { value: 'medium', label: '🟡 Média' },
                { value: 'high', label: '🔴 Alta' }
            ]
        }
    ]);

    if (!edited) {
        return;
    }

    const newTitle = (edited.title || '').trim();
    if (!newTitle) {
        alert('O título não pode ficar vazio.');
        return;
    }

    if (newTitle.length < 3) {
        alert('O título da tarefa deve ter pelo menos 3 caracteres.');
        return;
    }

    const payload = {
        title: newTitle,
        description: (edited.description || '').trim(),
        priority: edited.priority || 'medium',
        completed: task.completed
    };

    fetch(`${API_URL}/tasks/${taskId}/`, {
        method: 'PUT',
        headers: getAuthHeaders(username, password),
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (isAuthErrorStatus(response.status)) {
            throw new Error('AUTH_ERROR');
        }
        if (!response.ok) throw new Error('Erro ao atualizar tarefa');
        return response.json();
    })
    .then(updatedTask => {
        Object.assign(task, updatedTask);
        updateTasksDisplay();
        updateStats();
    })
    .catch(error => {
        console.error('Erro ao editar tarefa:', error);
        if (error.message === 'AUTH_ERROR') {
            handleAuthFailure();
            return;
        }
        alert('Erro ao editar tarefa. Tente novamente.');
    });
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

// Em modo API, não cria tarefas demo automaticamente.