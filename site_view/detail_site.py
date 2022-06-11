from flask import Blueprint, request
from site_control.detail_control import DetailControl
from site_control.profile_control import ProfileHandler

detail_page = Blueprint('detail', __name__)


@detail_page.route("/detail/<post_id>")
def detail(post_id):
    return DetailControl.detail_render(post_id)

@detail_page.route('/comment', methods=['POST'])
def save_comment():
    """
    클라이언트로부터 댓글 내용, 작성 시간, 포스트 아이디를 받아서 디비에 저장
    :return: 댓글 저장
    """
    comment_receive = request.form['comment_give']
    date_receive = request.form["date_give"]
    id_receive = request.form["id_give"]
    return DetailControl.save_comment(comment_receive, date_receive, id_receive)

@detail_page.route('/comment/delete', methods=['POST'])
def delete_comment():
    """
    댓글 식별용 인덱스를 받아서 해당되는 댓글을 DB에서 삭제
    :return: 댓글 삭제
    """
    comment_idx_receive = request.form['comment_idx_give']
    return DetailControl.delete_comment(comment_idx_receive)

@detail_page.route('/like_update', methods=['POST'])
def like_update():
    comment_id_receive = request.form["comment_id_give"]
    action_receive = request.form["action_give"]
    return DetailControl.like_update(comment_id_receive, action_receive)

@detail_page.route('/bookmark', methods=['POST'])
def bookmark():
    post_id_receive = request.form["post_id_give"]
    action_receive = request.form["action_give"]
    return DetailControl.bookmark(post_id_receive, action_receive)

@detail_page.route('/comments_get', methods=['GET'])
def comments_get():
    user_id_receive = request.args.get("user_id_give")
    post_id_receive = request.args.get("post_id_give")
    sorting_status_receive = request.args.get("sorting_status_give")
    return DetailControl.comments_get(user_id_receive, post_id_receive, sorting_status_receive)

@detail_page.route('/bookmarked', methods=['GET'])
def bookmarked():
    post_id_receive = request.args.get("post_id_give")
    return DetailControl.bookmarked(post_id_receive)

@detail_page.route('/posts_get', methods=['GET'])
def posts_get():
    user_id_receive = request.args.get("user_id_give")
    return ProfileHandler.posts_get(user_id_receive)