from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=".")
CORS(app)  # Включение CORS для всех маршрутов

# Логирование всех запросов
@app.before_request
def log_requests():
    print(f"Incoming request: {request.method} {request.path}")

# Маршрут для отдачи статических файлов
@app.route("/<path:path>", methods=["GET"])
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory(".", path)
    return jsonify({"error": "File not found"}), 404


@app.route('/user', methods=['GET'])
def get_user():
    # Здесь можно подключить авторизацию или взять данные из базы
    user_data = {"username": "John Doe"}  # Заменить на реальное получение данных
    return jsonify(user_data)

@app.route('/inventory', methods=['GET'])
def get_inventory():
    # Пример данных инвентаря для пользователя
    # В реальном приложении данные будут браться из базы
    user_inventory = {
        "Мячи": 8,
        "Ракетки": 1,
        "Скакалки": 4
    }
    return jsonify(user_inventory)

@app.route('/request-extra-inventory', methods=['POST'])
def request_extra_inventory():
    data = request.json
    if not data or 'item' not in data or 'quantity' not in data:
        return jsonify({"error": "Invalid request"}), 400

    item = data['item']
    quantity = data['quantity']

    if quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    # Обработка запроса дополнительного инвентаря (например, логирование)
    print(f"User requested {quantity} of {item}")

    # Ответ пользователю
    return jsonify({"message": f"Запрос на {quantity} {item}(ов) успешно отправлен."}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
