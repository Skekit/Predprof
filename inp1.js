// Получение имени пользователя через GET-запрос
async function fetchUsername() {
    try {
        // Отправляем GET-запрос на бэкенд
        const response = await fetch('http://127.0.0.1:8000/user');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Обрабатываем JSON-ответ
        const data = await response.json();
        const usernameElement = document.getElementById('username');

        // Обновляем имя пользователя в интерфейсе
        if (data.username) {
            usernameElement.innerHTML = `<a href="#">${data.username}</a>`;
        } else {
            usernameElement.innerHTML = `<a href="#">Гость</a>`;
        }
    } catch (error) {
        console.error('Ошибка при получении имени пользователя:', error);
    }
}

// Обработка запроса инвентаря
function setupInventoryRequest() {
    const requestButton = document.getElementById('request-button');
    requestButton.addEventListener('click', () => {
        const inventory = document.getElementById('inventory-select').value;
        const quantity = document.getElementById('quantity-input').value;
        alert(`Вы запросили ${quantity} ${inventory}(ов)`);
    });
}

// Инициализация функций
document.addEventListener('DOMContentLoaded', () => {
    fetchUsername(); // Загружаем имя пользователя при загрузке страницы
    setupInventoryRequest(); // Настраиваем обработку запроса инвентаря
});
// Получение инвентаря пользователя через GET-запрос
async function fetchUserInventory() {
    try {
        // Отправляем GET-запрос на маршрут /inventory
        const response = await fetch('http://127.0.0.1:8000/inventory');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Обрабатываем JSON-ответ
        const inventoryData = await response.json();

        // Отображаем инвентарь в таблице
        const inventoryTable = document.getElementById('inventory-table');
        inventoryTable.innerHTML = ''; // Очищаем таблицу перед добавлением новых данных

        for (const [itemName, quantity] of Object.entries(inventoryData)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${itemName}</td>
                <td>${quantity}</td>
            `;
            inventoryTable.appendChild(row);
        }
    } catch (error) {
        console.error('Ошибка при получении инвентаря:', error);
    }
}

// Инициализация функций
document.addEventListener('DOMContentLoaded', () => {
    fetchUsername(); // Загружаем имя пользователя
    fetchUserInventory(); // Загружаем инвентарь пользователя
    setupInventoryRequest(); // Настраиваем обработку запроса инвентаря
});
