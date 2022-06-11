from flask import Blueprint, jsonify
from dev_module import news_getter
from site_control import main_control


main_page = Blueprint('main', __name__)


@main_page.route('/')
def home():
    '''
        로그인 유무(토큰 유무)에 따른 분기 처리, 로그인시 유저 정보와 게시글 접근 권한(status==True)가 index.html과 함께 랜더링되며
        그렇지 않을 시, 접근 권한(status==Fale)인 상태만 랜더링된다.
    :return: 로그인 유무에 따른 게시글 접근 권한(status)와 유저 정보(user_info) 실패 메시지(msg)등이 index에 담겨 리턴된다.
    '''
    return main_control.home_render()


@main_page.route("/news", methods=["GET"])
def news_get():
    '''
    dev_module의 news_getter.get_news()를 통해 받아온 뉴스 정보를 /news로 요청을 보낸 클라이언트에게 리턴하는 함수
    :return news_list: post_id, title, summary, image_url, news_url, explain, write_time, view 정보가 담긴 리스트
    '''
    news_list = news_getter.get_news() # 뉴스 정보 받아오는 함수
    return jsonify({'news_list': news_list})
