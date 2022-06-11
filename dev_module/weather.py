from flask import jsonify, Blueprint
import requests
import json

OPENWEATHER_API_KEY = "87e3a3b8ff90e9ceb2e9297d20722b2d"

weather_api = Blueprint('weather_api', __name__)


@weather_api.route("/weather")
def weather_get():
    # Google geolocation API로부터 lat 과 lng 데이터 가져오기
    g_url = f'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyDpRifMguxQNS9mb9g0wgF-4OnZPTikIfM'

    google_location_result = requests.post(g_url)
    google_data = google_location_result.text
    google_json_data = json.loads(google_data)

    lat = google_json_data['location']['lat']
    lng = google_json_data['location']['lng']

    # Openweathermap API로부터 화면에 넣어줄 데이터 가져오기
    w_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric'

    weather_result = requests.get(w_url)
    weather_data = weather_result.text
    weather_json_data = json.loads(weather_data)

    # weather_json_data 에서 화면에 보여줄 데이터만 가져오기
    location = weather_json_data['name']
    weather = weather_json_data['weather'][0]['main']
    temp = weather_json_data['main']['temp']

    # 받아온 데이터 datas list에 넣기
    show_datas = [location, weather, temp]

    return jsonify({'show_datas': show_datas})