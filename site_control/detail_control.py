from flask import render_template, request, jsonify, redirect, url_for
from datetime import datetime
from CONFIG.account import SECRET_KEY
from model.mongo import UserAdmin, DetailContents, Posts, AboutComment
from operator import itemgetter
import jwt
from dev_module.xss_protect import xss_protect


class DetailControl():
    @staticmethod
    def detail_render(post_id):
        post = DetailContents.find_post(post_id)
        count_comments = DetailContents.count_comments(post_id)
        token_receive = request.cookies.get('mytoken')  # 클라이언트로부터 mytoekn에 담겨 온 토큰 정보 받아주기
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = UserAdmin.users_find_one("user_id", payload["id"])
            status = True

            #포스트 접속 기록 db 저장: 포스트_id, 유저_id, 접속 시간
            doc = {
                "post_id": post_id,
                "user_id": payload["id"],
                "use_time": datetime.now()
            }
            Posts.add_view_data(doc)
            return render_template('detail.html', post=post, status=status, user_info=user_info, count_comments=count_comments)
        except :
            status = False
            return redirect(url_for("main.home", msg="로그인을 해주세요!"))

    @staticmethod
    def save_comment(comment_receive, date_receive, id_receive):
        """ -hj
        댓글 저장
        :param comment_receive: 클라이언트에서 작성한 댓글 내용
        :param date_receive: 댓글 작성 시간
        :param id_receive: 댓글을 달려고 하는 post의 id
        :return: DB에 댓글 저장
        """
        # 토큰으로 유저 정보 가져오기
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = UserAdmin.users_find_one("user_id", payload["id"])

        # DB에 comment 저장 시 comment 식별용 아이디로 사용될 index 구성
        if DetailContents.count_all_comments == 0:
            max_value = 1
        else:
            max_value = DetailContents.plus_comment_id()

        doc = {
            "comment": xss_protect.stop_code_filter(comment_receive),
            "user_id": user_info['user_id'],
            "nick_name": user_info['nick_name'],
            "date": date_receive,
            "profile_pic_real": user_info['profile_pic_real'],
            "post_id": id_receive,
            "idx": max_value
        }

        DetailContents.insert_comment(doc)
        return jsonify({'msg': '의견이 정상적으로 등록되었습니다.'})

    @staticmethod
    def delete_comment(comment_idx_receive):
        """ -hj
        댓글 삭제
        :param comment_idx_receive: 댓글을 작성할 때마다 댓글에 부여되는 댓글 식별용 인덱스
        :return: DB에서 댓글 삭제
        """
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = UserAdmin.users_find_one("user_id", payload["id"])  # 유저 회원 정보 데이터 불러오기

        comment = AboutComment.comment_find('idx', int(comment_idx_receive))  # 코멘트 인덱스로 댓글 데이터 불러오기

        # 코멘트를 작성한 유저 아이디와 현재 로그인 되어있는 아이디 비교해서 일치할 때만 댓글 삭제 가능
        if comment['user_id'] == user_info['user_id']:
            DetailContents.delete_comment(comment_idx_receive)
            return jsonify({'msg': '의견이 삭제 되었습니다.', 'success': "성공"})

    @staticmethod
    def like_update(comment_id_receive, action_receive):
        """ -yj
        좋아요
        :param comment_id_receive: 좋아요 눌린 댓글 ID
        :param action_receive: 좋아요 취소 구분을 위함
        :return: 성공 여부, 좋아요 수
        """
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = payload["id"]
            doc = {
                "like_comment_id": comment_id_receive,
                "user_id": user_info
            }
            if action_receive == "like":
                DetailContents.insert_action(doc)
            else:
                DetailContents.delete_action(doc)
            count = DetailContents.count_like(comment_id_receive)
            return jsonify({"result": "success", "count": count})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))

    @staticmethod
    def bookmark(post_id_receive, action_receive):
        """ -yj
        북마크
        :param post_id_receive: 북마크 눌린 기사 ID
        :param action_receive: 북마크 취소 구분을 위함
        :return: 성공 여부
        """
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = payload["id"]
            doc = {
                "bookmark_post_id": post_id_receive,
                "user_id": user_info
            }
            if action_receive == "bookmark":
                DetailContents.insert_action(doc)
            else:
                DetailContents.delete_action(doc)
            return jsonify({"result": "success"})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))

    @staticmethod
    def comments_get(user_id_receive, post_id_receive, sorting_status_receive):
        """ -yj
        DB의 comments 컬렉션에서 댓글 정보 리스트를 최근 시간 순으로 가져오기
        :param user_id_receive: profile 페이지의 해당 사용자 ID
        :param post_id_receive: 현재 사용자가 위치한 기사 ID
        :param sorting_status_receive: 정렬 구분
        :return: 성공 여부, 댓글 리스트
        """
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = payload["id"]

            # user_id가 없으면(detail 페이지의 경우) post_id와 매칭되는 댓글 전체 가져오기
            if user_id_receive == "":
                comments = list(DetailContents.find_comments("post_id", post_id_receive).sort("date", -1).limit(20))
            else:
                comments = list(DetailContents.find_comments("user_id", user_id_receive).sort("date", -1).limit(20))

            for comment in comments:
                comment["_id"] = str(comment["_id"])
                # 좋아요 수, 여부 확인
                comment["count_like"] = DetailContents.count_like(comment["_id"])
                comment["like_by_me"] = bool(DetailContents.like_by_me("like_comment_id", comment["_id"], user_info))
                # 내가 쓴 댓글인지 확인
                comment["mine"] = (comment['user_id'] == user_info)

            # 정렬
            if sorting_status_receive == "new":
                comments = sorted(comments, key=itemgetter('date'), reverse=True)
            elif sorting_status_receive == "old":
                comments = sorted(comments, key=itemgetter('date'))
            elif sorting_status_receive == "like":
                comments = sorted(comments, key=itemgetter('count_like', 'date'), reverse=True)

            return jsonify({"result": "success", "comments": comments})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))

    @staticmethod
    def bookmarked(post_id_receive):
        """ -yj
        북마크 여부 확인
        :param post_id_receive: 현재 사용자가 위치한 기사 ID
        :return: 성공 여부, 북마크 여부
        """
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = payload["id"]
            bookmark_by_me = bool(DetailContents.like_by_me("bookmark_post_id", post_id_receive, user_info))
            return jsonify({"result": "success", "bookmark_by_me": bookmark_by_me})
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("home"))