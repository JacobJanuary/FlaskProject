import requests
import sqlite3
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = "38b444cb-ef6b-4312-8f3f-63e6ad61571c"

if not API_KEY:
    raise ValueError("Необходимо установить переменную окружения COINMARKETCAP_API_KEY")

conn = None

try:
    conn = sqlite3.connect('cryptocurrencies.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coins_volume_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id INTEGER,
            datetime TEXT,
            volume REAL,
            price REAL,
            marketcap REAL,
            FOREIGN KEY (coin_id) REFERENCES cryptocurrencies(id)
        )
    ''')
    conn.commit()

    cursor.execute("SELECT id FROM cryptocurrencies")
    coin_ids = cursor.fetchall()

    # Разделяем coin_ids на группы по 100
    chunk_size = 100
    for i in range(0, len(coin_ids), chunk_size):
        chunk = coin_ids[i:i + chunk_size]
        chunk_ids_str = ','.join(str(id_tuple[0]) for id_tuple in chunk)  # Преобразуем список id в строку для запроса

        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'id': chunk_ids_str
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': API_KEY,
        }

        try:
            response = requests.get(url, params=parameters, headers=headers)
            response.raise_for_status()
            data = response.json()['data']

            current_datetime = datetime.now().isoformat()

            for coin_id_str, coin_data in data.items():
                try:
                    coin_id = int(coin_id_str)
                    quote = coin_data['quote']['USD']

                    volume = quote.get('volume_24h')
                    price = quote.get('price')
                    marketcap = quote.get('market_cap')

                    cursor.execute('''
                        INSERT INTO coins_volume_stats (coin_id, datetime, volume, price, marketcap)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (coin_id, current_datetime, volume, price, marketcap))
                    conn.commit()
                    print(f"Данные для coin_id {coin_id} успешно добавлены.")
                except (KeyError, TypeError) as e:
                    print(f"Ошибка обработки данных для coin_id {coin_id_str}: {e}")

            time.sleep(1)  # Задержка после каждого запроса

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            if response.status_code == 429:
                print("Слишком много запросов! Ждем 60 секунд...")
                time.sleep(60)
                continue
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    print("Сбор данных завершен.")

except sqlite3.Error as e:
    print(f"Ошибка базы данных: {e}")
finally:
    if conn:
        conn.close()