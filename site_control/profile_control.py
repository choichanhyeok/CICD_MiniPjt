from flask import render_template, request, jsonify, redirect, url_for
from model.mongo import UserAdmin
from werkzeug.utils import secure_filename
from model.mongo import DetailContents
from dev_module.xss_protect import xss_protect
import jwt

SECRET_KEY = 'test'


class ProfileHandler:
    '''
        profile site구성을 위해 필요한 페이지 랜더링, 이미지 변경, 북마크 게시글 조회등의 기능을 갖고있는 클래스
    '''
    @staticmethod
    def profile_render(token, userid):
        ''' -CCH-
        api 요청을 보낸 토큰과 요청받은 profile 페이지의 유저 id를 비교해, 수정 권한 인가를 위한 status값과 랜더링을 위한 user_info를 랜더링할 페이지에 실어 리턴하는 함수
        :param token: 사용자 회원 정보를 파악하기 위해 받은 token 정보
        :param userid: 프로필 페이지의 수정 권한 인가를 위해, token(실 사용자)안의 id와 비교하기 위한 요청받은 프로필 page의 id
        :return profile.html(user_info, status) or index.html: 토큰 정보를 보고 권한이 있는 접근자인지 정보와 사용자 정보 리턴 or jwt 토큰 검증 실패자 index.html로
        ##이슈 존재 ##
        '''
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            status = (userid == payload["id"])                         # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
            user_info = UserAdmin.users_find_one('user_id', userid)    # 해당 user의 id 정보를 토대로 유저 정보를 가져옴 (model.mongo로부터)
            return render_template('profile.html', user_info=user_info, status=status)
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError): # jwt 토큰이 만료, 비인가 사용자면 index 페이지로 redirect
            return redirect(url_for("/"))

    @staticmethod
    def change_img(token):
        ''' -CCH-
        프로필 페이지에서 발생한 요청을 보고 form에 딸려온 토큰, 이름, 프로필 설명, 사진 정보등을 db에 업로드하는 함수
        :param token: 요청을 보낸 클라이언트의 토큰 정보
        :return profile.html(result, msg) || index.html: 성공 여부에 따른 분기 처리 (profile에서의 업데이트 성공여부 or 토큰 검사 실패시 index.html 페이지로)
        '''
        try:# 사진 업로드 기능
            # 토큰 정보를 보고 수정할 프로필 정보 추출
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            username = payload["id"]
            name_receive = request.form["name_give"]
            about_receive = request.form["about_give"]
            # 추출한 프로필 정보를 토대로 doc 생성
            new_doc = {
                "nick_name": xss_protect.stop_code_filter(name_receive),   #xss 공격 방어를 위해, 커스터마이징한 필터링 적용
                "profile_info": xss_protect.stop_code_filter(about_receive)
            }
            # 클라이언트로부터 전달받은 파일 정보를 토대로 프로필 사진 이름, 매핑을 위한 경로값 doc에 추가 
            if 'file_give' in request.files:
                file = request.files["file_give"]                   # request.files로 받은 클라이언트가 보낸 file객체
                filename = secure_filename(file.filename)           # 파일 이름
                extension = filename.split(".")[-1]                 # 파일 확장자명
                file_path = f"profile_pics/{username}.{extension}"  # 파일 완전 경로
                file.save("./static/" + file_path)                  # 파일을 ./static에 사진명으로 분류된 경로에 저장
                new_doc["profile_pic"] = filename                   # db에 삽입할 new_doc에 finame 기록
                new_doc["profile_pic_real"] = file_path             # db에 삽입할 new_doc에 file_path 기록
            else:  # 전달받은 파일이 없을 때
                filename = 'profile_placeholder.png'                # 기본 파일이름 설정 (프로필 없음 사진)
                file_path = 'profile_pics/profile_placeholder.png'  # 기본 파일 경로 설정
                new_doc["profile_pic"] = filename                   # db에 삽입할 new_doc에 기본 파일명 기록
                new_doc["profile_pic_real"] = file_path             # db에 삽입한 new_doc에 기본 경로명 기록

            UserAdmin.users_update_one(payload['id'], new_doc)      # mode.mongo의 user_update_one을 통해 해당 id의 프로필 정보 앞서 기록한 doc으로 변경
            return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError): # 사진 업로드 실패시 home으로,
            return redirect(url_for("home"))

    @staticmethod
    def posts_get(user_id_receive):
        """ -yj
        DB의 news_data 컬렉션에서 북마크한 기사 리스트를 최근 시간 순으로 가져오기
        :param user_id_receive: 로그인한 사용자 ID
        :return: 성공 여부, 기사 리스트
        """
        try:
            # 해당 사용자가 북마크한 기사 ID 필드 가져오기
            bookmark_post_ids = list(DetailContents.find_bookmark_post(user_id_receive).sort("date", -1).limit(20))
            bookmarked_posts = []
            for r in bookmark_post_ids:
                if r:  # 해당 컬렉션에 다른 필드도 함께 있어서 기사 ID가 있는 경우에만 기사를 찾아 넣도록 처리
                    bookmarked_posts.append(DetailContents.find_post(r["bookmark_post_id"]))
            return jsonify({"result": "success", "posts": bookmarked_posts})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))

