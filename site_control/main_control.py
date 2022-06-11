from flask import render_template, request
from CONFIG.account import SECRET_KEY
from model.mongo import UserAdmin
import jwt


def home_render():
    '''
    token 유무를 파악해 게시글 접근 권한 인가를 위한 상태(status), 유저 정보(user_info)등을 index.html에 삽입해 랜더링 하는 함수
    :return: jwt 정보가 있을시, 상태(True)와 해당 토큰에 담겨있는 user_info를 담아 inex.html에 삽입해 랜더링. jwt 정보가 없을 시 실패 메시지라 상태(False)를 담어 랜더링
    '''
    msg = request.args.get("msg")
    token_receive = request.cookies.get('mytoken')  # 클라이언트로부터 mytoekn에 담겨 온 토큰 정보 받아주기 #
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = UserAdmin.users_find_one("user_id", payload["id"])
        status = True
        return render_template('index.html', status=status, user_info=user_info)
    except :
        status = False
        return render_template('index.html', status=status, msg=msg)