// Переменная для переключения режимов (Вход / Регистрация)
let isLoginMode = true;

// 1. Функция для визуального переключения формы
function toggleMode() {
    isLoginMode = !isLoginMode;
    const title = document.getElementById('form-title');
    const btn = document.getElementById('auth-btn');
    const link = document.getElementById('toggle-link');

    if (isLoginMode) {
        title.innerText = 'Вход в аккаунт';
        btn.innerText = 'Войти';
        link.innerText = 'Нет аккаунта? Зарегистрироваться';
    } else {
        title.innerText = 'Регистрация';
        btn.innerText = 'Создать аккаунт';
        link.innerText = 'Уже есть аккаунт? Войти';
    }
}

// 2. Основная функция общения с базой данных (через сервер)
async function handleAuth() {
    const userField = document.getElementById('username');
    const passField = document.getElementById('password');
    
    const username = userField.value.trim();
    const password = passField.value.trim();

    // Простая проверка на пустые поля
    if (!username || !password) {
        alert("Пожалуйста, заполните все поля!");
        return;
    }

    // Определяем, на какой адрес отправлять данные (на наш Flask сервер)
    const endpoint = isLoginMode ? '/login' : '/register';
    const url = 'http://127.0.0.1:5000' + endpoint;

    try {
        // Отправляем запрос на сервер
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Если сервер ответил "ОК"
            alert(data.message);
            
            // Сохраняем имя только для того, чтобы сайт знал, как нас называть
            localStorage.setItem('currentUser', username);
            
            // Переходим на главную
            window.location.href = 'index.html';
        } else {
            // Если сервер вернул ошибку (например, неверный пароль)
            alert("Ошибка: " + data.message);
        }

    } catch (error) {
        // Если сервер не запущен или произошла ошибка сети
        console.error("Ошибка соединения:", error);
        alert("Не удалось связаться с сервером базы данных. Убедитесь, что Python-скрипт запущен!");
    }
}

