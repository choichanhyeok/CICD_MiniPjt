from datetime import datetime, timedelta
from CONFIG.account import SECRET_KEY
from model.mongo import UserAdmin
from flask import jsonify
import jwt


class JoinAdmin():
    @staticmethod
    def sign_in(user_id, pw_hash):
        is_customer = UserAdmin.is_customer_check(user_id, pw_hash)

        if is_customer is not None:
            payload = {
                'id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'result': 'success', 'token': token})
        # 찾지 못하면
        else:
            return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    @staticmethod
    def sign_up(user_id, user_pw):
        doc = {
            "user_id": user_id,  # 아이디
            "password": user_pw,  # 비밀번호
            "nick_name": user_id,  # 닉네임 기본값은 아이디
            "profile_pic": "",  # 프로필 사진 파일 이름
            "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
            "profile_info": ""  # 프로필 한 마디
        }
        UserAdmin.user_signup_db(doc)
        return jsonify({'result': 'success'})

    @staticmethod
    def check_dup(user_id):
        exists = bool(UserAdmin.users_find_one("user_id", user_id))
        return jsonify({'result': 'success', 'exists': exists})