from site_view import main_site, join_site, detail_site, profile_site
from flask_wtf.csrf import CSRFProtect
from flask import Flask
from dev_module import weather


application = Flask(__name__)
CSRFProtect(application)
application.config["SECRET_KEY"] = 'chlcksgur12'

#사이트 Routing#
application.register_blueprint(main_site.main_page)          # index.html에 관련된 blueprint
application.register_blueprint(join_site.join_page)          # login.html에 관련된 blueprint
application.register_blueprint(detail_site.detail_page)      # detail.html에 관련된 blueprint
application.register_blueprint(profile_site.profile_page)    # profile.html에 관련된 blueprint

#외부 API(weather)
application.register_blueprint(weather.weather_api)  # 화면에 날씨/위치 정보 표시해주는 것과 관련된 blueprint

if __name__ == '__main__':
    application.run('0.0.0.0', port=5000, debug=True)
