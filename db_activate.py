import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = "38b444cb-ef6b-4312-8f3f-63e6ad61571c"

if not API_KEY:
    raise ValueError("Необходимо установить переменную окружения COINMARKETCAP_API_KEY")

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': API_KEY,
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Проверка на ошибки HTTP (например, 400, 401, 500)
    data = response.json()['data']

    # Подключение к базе данных (создаст файл, если его нет)
    conn = sqlite3.connect('cryptocurrencies.db')
    cursor = conn.cursor()

    # Создание таблицы, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id INTEGER PRIMARY KEY,
            rank INTEGER,
            name TEXT,
            symbol TEXT
        )
    ''')
    conn.commit()

    # Очистка таблицы перед добавлением новых данных (опционально, если нужно полное обновление)
    cursor.execute("DELETE FROM cryptocurrencies")
    conn.commit()

    # Вставка данных в базу данных
    for currency in data:
        if currency['is_active'] == 1:
            cursor.execute('''
                INSERT INTO cryptocurrencies (id, rank, name, symbol)
                VALUES (?, ?, ?, ?)
            ''', (currency['id'], currency.get('rank'), currency['name'], currency['symbol'])) # .get() для обработки отсутствия ключа 'rank'
    conn.commit()

    print("Данные успешно сохранены в базу данных cryptocurrencies.db")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при запросе к API: {e}")
except sqlite3.Error as e:
    print(f"Ошибка базы данных: {e}")
except KeyError as e:
    print(f"Ошибка в структуре данных API (отсутствует ключ {e}): возможно, структура ответа API изменилась")
finally:
    if conn:
        conn.close()