from flask import request, Blueprint
from site_control.profile_control import ProfileHandler

SECRET_KEY = 'test'

profile_page = Blueprint('profile', __name__)


# 각 사용자의 프로필과 글을 모아볼 수 있는 공간
@profile_page.route('/profile/<userid>')
def profile(userid):
    ''' -CCH-
    분기에 따른 profile 랜더링 정보를 리턴해주는 api, (로그인 유저 접근시 profile_page, 그 밖의 경우 index.html 랜더링)
    :param userid: index로 부터 넘어오는 원하는 프로필 페이지의 사용자 id
    :return profile.html or index.html: 사용자 토큰 유무(로그인 인가 파악)에 따라 페이지 리턴
    '''
    token_receive = request.cookies.get('mytoken') # 사용자의 토큰 정보를 받아,
    return ProfileHandler.profile_render(token_receive, userid) # api 요청시, 사용자의 id를 보고 분기처리


# 사용자의 프로필 이미지 바꿀 수 있는 기능
@profile_page.route('/update_profile', methods=['POST'])
def save_img():
    '''
    클라이언트가 /update_profile 경로로 POST 요청을 하면 profile 정보 변경 성공 여부를 리턴하는 함수, (실패시 index.html 랜더링)
    :return {result:bool, msg:String} or redirect('/'): 업데이트 성공 여부혹은, jwt 검사 실패시 index.html 페이지로 redirect
    '''
    token_receive = request.cookies.get('mytoken')
    return ProfileHandler.change_img(token_receive)


# 프로필 페이지에서 사용자가 북마크한 기사만 모아보기
@profile_page.route('/profile/<userid>')
def show_bookmark(userid):
    return ProfileHandler.posts_get(userid)
