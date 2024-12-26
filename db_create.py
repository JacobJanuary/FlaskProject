import sqlite3

try:
    conn = sqlite3.connect('cryptocurrencies.db')
    cursor = conn.cursor()

    # Создаем таблицу cryptocurrencies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            rank INTEGER
        )
    ''')

    # Создаем таблицу coins_volume_stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coins_volume_stats (
            id INTEGER PRIMARY KEY,
            coin_id INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            volume REAL,
            price REAL,
            FOREIGN KEY (coin_id) REFERENCES cryptocurrencies(id)
        )
    ''')
    conn.commit()
    print("Таблицы успешно созданы.")

except sqlite3.Error as e:
    print(f"Ошибка базы данных: {e}")

finally:
    if conn:
        conn.close()

#Заполнение таблицы cryptocurrencies тестовыми данными
try:
    conn = sqlite3.connect('cryptocurrencies.db')
    cursor = conn.cursor()
    cryptos = [
        ('Bitcoin', 'BTC', 1),
        ('Ethereum', 'ETH', 2),
        ('Litecoin', 'LTC', 10),
        ('Cardano', 'ADA', 7)
    ]
    cursor.executemany("INSERT OR IGNORE INTO cryptocurrencies (name, symbol, rank) VALUES (?, ?, ?)", cryptos)
    conn.commit()
    print("Таблица cryptocurrencies заполнена тестовыми данными")
except sqlite3.Error as e:
    print(f"Ошибка базы данных: {e}")

finally:
    if conn:
        conn.close()

#Заполнение таблицы coins_volume_stats тестовыми данными
import datetime
try:
    conn = sqlite3.connect('cryptocurrencies.db')
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    stats = [
        (1, now, 100000, 29000),
        (1, yesterday, 90000, 28000),
        (2, now, 50000, 1900),
        (2, yesterday, 40000, 1800),
        (3, now, 10000, 100),
        (3, yesterday, 9000, 90),
        (4, now, 1000000, 0.3),
        (4, yesterday, 900000, 0.25)
    ]
    cursor.executemany("INSERT INTO coins_volume_stats (coin_id, datetime, volume, price) VALUES (?, ?, ?, ?)", stats)
    conn.commit()
    print("Таблица coins_volume_stats заполнена тестовыми данными")
except sqlite3.Error as e:
    print(f"Ошибка базы данных: {e}")

finally:
    if conn:
        conn.close()