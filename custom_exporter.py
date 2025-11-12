from prometheus_client import start_http_server, Gauge, Counter
import requests
import time
import random

# --- Настройки ---
API_KEY = "9d681cfb761e61870a806921bac779e2"
CITIES = ["Astana", "Almaty", "Shymkent"]  # ⚙️ теперь несколько городов
URL_TEMPLATE = "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

# --- Метрики Prometheus с лейблом city ---
temperature = Gauge('weather_temperature_celsius', 'Current temperature in Celsius', ['city'])
feels_like = Gauge('weather_feels_like_celsius', 'Feels like temperature in Celsius', ['city'])
humidity = Gauge('weather_humidity_percent', 'Humidity in percentage', ['city'])
pressure = Gauge('weather_pressure_hpa', 'Atmospheric pressure in hPa', ['city'])
wind_speed = Gauge('weather_wind_speed_mps', 'Wind speed in meters per second', ['city'])
cloudiness = Gauge('weather_cloudiness_percent', 'Cloudiness in percent', ['city'])
visibility = Gauge('weather_visibility_meters', 'Visibility in meters', ['city'])
sunrise = Gauge('weather_sunrise_timestamp', 'Sunrise time (UNIX)', ['city'])
sunset = Gauge('weather_sunset_timestamp', 'Sunset time (UNIX)', ['city'])
update_time = Gauge('weather_last_update_seconds', 'Last update timestamp', ['city'])
comfort_index = Gauge('weather_comfort_index', 'Synthetic comfort index combining temperature and humidity', ['city'])
temperature_variation = Gauge('weather_temp_variation_last_hour', 'Simulated temperature variation last hour', ['city'])
api_latency = Gauge('weather_api_latency_seconds', 'OpenWeather API response latency in seconds', ['city'])
api_errors = Counter('weather_api_errors_total', 'Number of API request errors', ['city'])

# --- Основная функция ---
def collect_weather():
    for city in CITIES:
        start = time.time()
        try:
            url = URL_TEMPLATE.format(city=city, key=API_KEY)
            resp = requests.get(url, timeout=10)
            latency = time.time() - start
            api_latency.labels(city=city).set(latency)

            data = resp.json()

            if resp.status_code != 200 or "main" not in data:
                api_errors.labels(city=city).inc()
                print(f"⚠️ Invalid response for {city}: {data}")
                continue

            main = data["main"]
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            sys = data.get("sys", {})

            # --- Обновление метрик ---
            temperature.labels(city=city).set(main.get("temp", 0))
            feels_like.labels(city=city).set(main.get("feels_like", 0))
            humidity.labels(city=city).set(main.get("humidity", 0))
            pressure.labels(city=city).set(main.get("pressure", 0))
            wind_speed.labels(city=city).set(wind.get("speed", 0))
            cloudiness.labels(city=city).set(clouds.get("all", 0))
            visibility.labels(city=city).set(data.get("visibility", 0))
            sunrise.labels(city=city).set(sys.get("sunrise", 0))
            sunset.labels(city=city).set(sys.get("sunset", 0))
            update_time.labels(city=city).set(time.time())

            # --- Кастомные расчёты ---
            comfort_index.labels(city=city).set(round((main.get("temp", 0) + (100 - main.get("humidity", 0)) / 5), 2))
            temperature_variation.labels(city=city).set(random.uniform(-1.5, 1.5))

            print(f"✅ Updated {city}: {main.get('temp', '?')}°C, humidity {main.get('humidity', '?')}%, latency {round(latency, 2)}s")

        except Exception as e:
            api_errors.labels(city=city).inc()
            print(f"❌ Error fetching data for {city}: {e}")


# --- Запуск ---
if __name__ == "__main__":
    print("🚀 Starting Custom OpenWeather Exporter with city labels on port 8000...")
    start_http_server(8000)
    while True:
        collect_weather()
        time.sleep(20)
