import requests
import geocoder
import sqlite3
from datetime import datetime, timezone, timedelta

API_KEY = "149e2a0058107922f6aff6ee2e05113d"

def get_weather_by_city(city: str):
    """
    Получение информации о погоде по названию города.

    Аргумент:
    city - название города.
    """

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        response.raise_for_status()  # Проверяем наличие ошибок при запросе
        weather_data = response.json()

        print_weather_info(city, weather_data)
        save_to_database((datetime.now(), city, weather_data["weather"][0]["description"], weather_data["main"]["temp"], weather_data["main"]["feels_like"], weather_data["wind"]["speed"]))
    except requests.exceptions.HTTPError:
        print(f"Город не найден, попробуйте снова!")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}, попробуйте снова!")

def print_weather_info(location: str, weather_data: dict):
    """
    Вывод информации о погоде.

    Аргументы:
    location - местоположение;
    weather_data - данные о погоде.
    """

    # Получаем UTC временную метку из данных о погоде
    utc_timestamp = weather_data["dt"]
    
    # Получаем смещение временной зоны в формате ±HHMM
    offset = weather_data["timezone"]

    tz = timezone(timedelta(seconds=offset))
    result_time = datetime.fromtimestamp(utc_timestamp, tz)

    # Форматируем время в нужный формат с смещением временной зоны
    formatted_time = result_time

    print("Текущее время:", formatted_time)
    print("Название города:", location)
    print("Погодные условия:", weather_data["weather"][0]["description"])
    print("Текущая температура:", weather_data["main"]["temp"], "градусов по Цельсию")
    print("Ощущается как:", weather_data["main"]["feels_like"], "градусов по Цельсию")
    print("Скорость ветра:", weather_data["wind"]["speed"], "м/c")

def get_weather_by_location():
    """
    Получение информации о погоде по текущему местоположению.
    """

    try:
        location = geocoder.ip("me")

        if location:
            latitude, longitude = location.latlng
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
            response = requests.get(url)
            response.raise_for_status()  # Проверяем наличие ошибок при запросе
            weather_data = response.json()
           
            print_weather_info(location.address, weather_data)
            save_to_database((datetime.now(), location.address, weather_data["weather"][0]["description"], weather_data["main"]["temp"], weather_data["main"]["feels_like"], weather_data["wind"]["speed"]))
        else:
            print("Не удалось определить текущее местоположение")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}, попробуйте снова!")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}, попробуйте снова!")

def save_to_database(data: tuple):
    """
    Сохранение результатов запросов в базу данных.

    Аргумент:
    data - данные для сохранения.
    """

    try:
        connection = sqlite3.connect("weather.db")
        cursor = connection.cursor()

        # Создаем таблицу, если она не существует
        cursor.execute('''CREATE TABLE IF NOT EXISTS weather_requests
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          timestamp DATETIME, 
                          city TEXT, 
                          weather_condition TEXT, 
                          temperature FLOAT,
                          feeling FLOAT,
                          speed FLOAT)''')

        # Форматируем время перед вставкой в базу данных
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Вставляем данные в таблицу
        cursor.execute("INSERT INTO weather_requests (timestamp, city, weather_condition, temperature, feeling, speed) VALUES (?, ?, ?, ?, ?, ?)", (formatted_time,) + data[1:])
        connection.commit()
        connection.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с базой данных, попробуйте снова!")

def print_history(n: str):
    """
    Вывод истории запросов о погоде из базы данных.

    Аргумент:
    n - количество последних запросов (str).
    """

    try:
        n = int(n)
        if n < 0:
            print("Введите значение n > 0")
        else:
            connection = sqlite3.connect("weather.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM weather_requests ORDER BY timestamp DESC LIMIT {n}")
            results = cursor.fetchall()
            connection.close()

            print("Последние", n, "запросов:")
            print("=" * 20)
            for result in results:
                print("Время запроса:", result[1])
                print("Название города:", result[2])
                print("Погодные условия:", result[3])
                print("Температура:", result[4], "градусов по Цельсию")
                print("Ощущение:", result[5], "градусов по Цельсию")
                print("Скорость ветра:", result[6], "м/c")
                print("=" * 20)
            
    except ValueError:
        print("Введите целое число для 'history'.")
    except sqlite3.OperationalError:
        print("История запросов пуста.")
    except sqlite3.Error as error:
        print("Ошибка при работе с базой данных, попробуйте снова!")

def main():
    """
    Обработка команд пользователя и вызов соответствующих функций.

    Функция выводит список доступных команд и предлагает пользователю ввести одну из них.
    Пользователь может выбрать одну из следующих команд:
        - 'city': получить информацию о погоде по названию города;
        - 'location': получить информацию о погоде по текущему местоположению;
        - 'history': получить историю запросов о погоде;
        - 'exit': завершить выполнение программы.

    После ввода одной из команд программа запускает соответствующую функцию.
    """
    
    commands = {
        'city': 'погода по названию города',
        'location': 'погода по текущему местоположению',
        'history': 'история запросов',
        'exit': 'выход'
    }

    while True:
        print("\nДоступные команды:")
        for cmd, desc in commands.items():
            print(f"'{cmd}' - {desc}")

        user_input = input("\nВыберите одну из команд и введите её: ").strip()

        if user_input == 'exit':
            print("Завершение программы.")
            break
        elif user_input == 'city':
            city = input("Введите название города: ").strip()
            print()
            get_weather_by_city(city)
        elif user_input == 'location':
            print()
            get_weather_by_location()
        elif user_input == 'history':
            n = input("Введите количество последних запросов: ").strip()
            print()
            print_history(n)
        else:
            print("Неизвестная команда. Пожалуйста, выберите из предложенного списка.")

if __name__ == "__main__":
    main()