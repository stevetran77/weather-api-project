import requests

api_key = "your_api_key"
api_url = f"https://api.weatherstack.com/current?access_key={api_key}&query=Viet Nam" 

# # Fetching data from API
def fetch_data() :
    print('Fetching weather data from Weather Stack API....')
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        print('API response received successfully') 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'An error occured: {e}')
        raise

fetch_data()

# Take data reference from API
def mock_fetch_data():
    return {'request': {'type': 'City', 'query': 'Viet An, Vietnam', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'Viet An', 'country': 'Vietnam', 'region': '', 'lat': '15.617', 'lon': '108.217', 'timezone_id': 'Asia/Ho_Chi_Minh', 'localtime': '2025-08-12 22:05', 'localtime_epoch': 1755036300, 'utc_offset': '7.0'}, 'current': {'observation_time': '03:05 PM', 'temperature': 27, 'weather_code': 353, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png'], 'weather_descriptions': ['Light rain shower'], 'astro': {'sunrise': '05:30 AM', 'sunset': '06:11 PM', 'moonrise': '08:23 PM', 'moonset': '07:59 AM', 'moon_phase': 'Waning Gibbous', 'moon_illumination': 91}, 'air_quality': {'co': '444', 'no2': '8.14', 'o3': '273', 'so2': '8.325', 'pm2_5': '48.285', 'pm10': '49.025', 'us-epa-index': '3', 'gb-defra-index': '3'}, 'wind_speed': 9, 'wind_degree': 151, 'wind_dir': 'SSE', 'pressure': 1008, 'precip': 0.9, 'humidity': 87, 'cloudcover': 75, 'feelslike': 30, 'uv_index': 0, 'visibility': 10, 'is_day': 'no'}}
