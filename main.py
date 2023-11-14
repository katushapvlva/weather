import requests
from geopy.geocoders import Nominatim
import sqlite3
import argparse

# Функция для получения информации о погоде по названию города
def get_weather_by_city(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=your_api_key"
    response = requests.get(url)
    weather_data = response.json()
    # Отобразить информацию о погоде, например:
    print("Текущее время:", weather_data["dt"])
    print("Название города:", city)
    print("Погодные условия:", weather_data["weather"][0]["description"])
    print("Текущая температура:", weather_data["main"]["temp"], "градусов по цельсию")
    # и т.д.

# Функция для определения текущего местоположения и получения информации о погоде
def get_weather_by_location():
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode("your_ip_address")
    latitude = location.latitude
    longitude = location.longitude
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=your_api_key"
    response = requests.get(url)
    weather_data = response.json()
    # Отобразить информацию о погоде
    # ...

# Функция для сохранения результатов запросов в базу данных
def save_to_database(data):
    connection = sqlite3.connect("weather.db")
    cursor = connection.cursor()
    # Создать таблицу, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS weather_requests
                      (timestamp DATETIME, city TEXT, weather_condition TEXT, temperature FLOAT)''')
    # Вставить данные в таблицу
    cursor.execute("INSERT INTO weather_requests VALUES (?, ?, ?, ?)", data)
    connection.commit()
    connection.close()

# Функция для вывода последних результатов запросов из базы данных
def print_history(n):
    connection = sqlite3.connect("weather.db")
    cursor = connection.cursor()
    # Выбрать последние n результатов запросов
    cursor.execute(f"SELECT * FROM weather_requests ORDER BY timestamp DESC LIMIT {n}")
    results = cursor.fetchall()
    for result in results:
        print(result)
    connection.close()

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