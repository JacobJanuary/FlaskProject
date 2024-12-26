from flask import Flask, render_template
import sqlite3
import requests
import os
from openai import OpenAI
from datetime import datetime, timedelta

app = Flask(__name__)

def format_volume(volume):
    if volume is not None:
        return f"{volume / 1000000:.2f} млн"
    return "N/A"

def format_price(price):
    if price is not None:
        return f"{price:.2f}"
    return "N/A"

#XAI_API_KEY = "xai-AEbygKMNvz46KLqCszO6UEp3RDpc0DyWmwLpwOnNlM18BWF0rUwuHGPVSUykOxAyRuGKoT48IzCOSvvm" # Получаем ключ из переменной окружения
#GROK_API_URL = "https://api.x.ai/v1"

def get_grok_analytics(name, symbol):
    if not XAI_API_KEY:
        print("Ошибка: Не установлен XAI_API_KEY")
        return {"error": "API ключ не установлен"}

    try:

        client = OpenAI(
            api_key="xai-AEbygKMNvz46KLqCszO6UEp3RDpc0DyWmwLpwOnNlM18BWF0rUwuHGPVSUykOxAyRuGKoT48IzCOSvvm",
            base_url="https://api.x.ai/v1",
        )

        completion = client.chat.completions.create(
            model="grok-2-1212",
            messages=[
                {"role": "system",
                 "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
                {"role": "user", "content": "дай подробную информацию о проекте {name} ({symbol}). Что он делает, когда создан, кто в команде, какие перспективы, развитие, социальная активность. Заходили ли в проект умные деньги, какие твои прогнозы по курсу токена на 2025 год"},
            ],
        )

        response = completion.choices[0].message.content # Устанавливаем таймаут
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API Grok: {e}")

    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return {"error": "Непредвиденная ошибка"}

# ... (остальной код app.py)
@app.route("/")
def index():
    try:
        conn = sqlite3.connect('cryptocurrencies.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, symbol, rank FROM cryptocurrencies")
        cryptos = cursor.fetchall()

        crypto_data_to_display = []
        time_difference_global = None

        for coin_id, coin_name, coin_symbol, current_rank in cryptos:
            cursor.execute('''
                SELECT datetime, volume, price
                FROM coins_volume_stats
                WHERE coin_id = ?
                ORDER BY datetime DESC
                LIMIT 6
            ''', (coin_id,))
            volume_data = cursor.fetchall()

            if len(volume_data) >= 2:
                periods_of_growth = 0
                time_of_growth = timedelta(0)
                total_volume_increase_percentage = 0

                for i in range(1, len(volume_data)):
                    prev_volume, prev_datetime = volume_data[i][1], volume_data[i][0]
                    curr_volume, curr_datetime = volume_data[i-1][1], volume_data[i-1][0]

                    if prev_volume is not None and curr_volume is not None:
                        try:
                            if curr_volume > prev_volume:
                                periods_of_growth += 1
                                time_diff = datetime.fromisoformat(curr_datetime) - datetime.fromisoformat(prev_datetime)
                                time_of_growth += time_diff

                                increase_percentage = ((curr_volume - prev_volume) / prev_volume) * 100
                                total_volume_increase_percentage += increase_percentage
                            else:
                                break
                        except (ValueError, TypeError, ZeroDivisionError):
                            print(f"Ошибка при обработке данных для {coin_name} ({coin_symbol})")
                            break
                    else:
                        break

                if periods_of_growth > 0:
                  average_volume_increase_percentage = total_volume_increase_percentage / periods_of_growth
                else:
                  average_volume_increase_percentage = 0

                if time_difference_global is None and len(volume_data) >= 2:
                    try:
                        time_difference_global = datetime.fromisoformat(volume_data[0][0]) - datetime.fromisoformat(volume_data[1][0])
                    except (ValueError, IndexError):
                        print(f"Некорректный формат даты или недостаточно данных для {coin_name} ({coin_symbol})")
                        time_difference_global = timedelta(0)

                latest_volume, latest_price = volume_data[0][1], volume_data[0][2]
                if len(volume_data) > 1:
                    previous_volume, previous_price = volume_data[1][1], volume_data[1][2]
                else:
                    previous_volume, previous_price = None, None

                if all(v is not None for v in (previous_volume, latest_volume, latest_price)):
                    try:
                        volume_increase = ((latest_volume - previous_volume) / previous_volume) * 100
                        price_change = ((latest_price - previous_price) / previous_price) * 100

                        if volume_increase >= 20 and abs(price_change) <= 10:
                            crypto_data_to_display.append({
                                "name": coin_name,
                                "symbol": coin_symbol,
                                "rank": current_rank,
                                "current_volume": format_volume(latest_volume),
                                "volume_increase": volume_increase,
                                "current_price": format_price(latest_price),
                                "price_change": price_change,
                                "periods_of_growth": min(periods_of_growth, 5),
                                "time_of_growth": time_of_growth,
                                "average_volume_increase_percentage": average_volume_increase_percentage
                            })
                    except ZeroDivisionError:
                        print(f"Деление на ноль при расчете для {coin_name} ({coin_symbol})")
                    except (TypeError, ValueError) as e:
                        print(f"Ошибка типа данных: {e} для {coin_name} ({coin_symbol})")
                else:
                    print(f"Недостаточно данных для {coin_name} ({coin_symbol})")
            else:
                print(f"Недостаточно данных о объемах для {coin_name} ({coin_symbol})")

        return render_template("index.html", crypto_data=crypto_data_to_display, time_difference=time_difference_global)

    except sqlite3.Error as e:
        return f"Ошибка базы данных: {e}"
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)