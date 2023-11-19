import requests
from geopy.geocoders import Nominatim
import sqlite3
import argparse
from datetime import datetime

API_KEY = "149e2a0058107922f6aff6ee2e05113d"

# Функция для получения информации о погоде по названию города
def get_weather_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Проверяем наличие ошибок при запросе
        weather_data = response.json()

        print_weather_info(city, weather_data)
        save_to_database((datetime.now(), city, weather_data["weather"][0]["description"], weather_data["main"]["temp"]))
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}")

# Функция для вывода информации о погоде
def print_weather_info(location, weather_data):
    print("Текущее время:", datetime.fromtimestamp(weather_data["dt"]).strftime('%Y-%m-%d %H:%M:%S'))
    print("Название города:", location)
    print("Погодные условия:", weather_data["weather"][0]["description"])
    print("Текущая температура:", weather_data["main"]["temp"], "градусов по Цельсию")
    print("Ощущается как:", weather_data["main"]["feels_like"], "градусов по Цельсию")
    print("Скорость ветра:", weather_data["wind"]["speed"], "м/c")
    # Добавим информацию о других параметрах погоды при необходимости
    # ...

# Функция для получения информации о погоде по текущему местоположению
def get_weather_by_location():
    try:
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode("me")

        if location:
            latitude, longitude = location.latitude, location.longitude
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # Проверяем наличие ошибок при запросе
            weather_data = response.json()

            print_weather_info(location.address, weather_data)
            save_to_database((datetime.now(), location.address, weather_data["weather"][0]["description"], weather_data["main"]["temp"]))
        else:
            print("Не удалось определить текущее местоположение")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}")

# Функция для сохранения результатов запросов в базу данных
def save_to_database(data):
    try:
        connection = sqlite3.connect("weather.db")
        cursor = connection.cursor()

        # Создаем таблицу, если она не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS weather_requests
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          timestamp DATETIME, 
                          city TEXT, 
                          weather_condition TEXT, 
                          temperature FLOAT)''')

        # Вставляем данные в таблицу
        cursor.execute("INSERT INTO weather_requests (timestamp, city, weather_condition, temperature) VALUES (?, ?, ?, ?)", data)
        connection.commit()
        connection.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с базой данных:", error)

# Функция для вывода последних результатов запросов из базы данных
def print_history(n):
    try:
        connection = sqlite3.connect("weather.db")
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM weather_requests ORDER BY timestamp DESC LIMIT {n}")
        results = cursor.fetchall()
        connection.close()

        if results:
            print("Последние", n, "результатов запросов:")
            for result in results:
                print("Время запроса:", result[0])
                print("Место:", result[1])
                print("Погодные условия:", result[2])
                print("Температура:", result[3])
                print("="*20)
        else:
            print("История запросов пуста.")
    except sqlite3.Error as error:
        print("Ошибка при работе с базой данных:", error)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", help="get weather by city")
    parser.add_argument("--location", action="store_true", help="get weather by current location")
    parser.add_argument("--history", type=int, help="print history of requests")
    args = parser.parse_args()

    if args.city:
        get_weather_by_city(args.city)
    elif args.location:
        get_weather_by_location()
    elif args.history:
        print_history(args.history)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()