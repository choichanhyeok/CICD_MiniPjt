from flask import render_template, request, Blueprint
from site_control.join_control import JoinAdmin
import hashlib

join_page = Blueprint('join', __name__)


@join_page.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@join_page.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    return JoinAdmin.sign_in(username_receive, pw_hash)


@join_page.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    return JoinAdmin.sign_up(username_receive, password_hash)


@join_page.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    return JoinAdmin.check_dup(username_receive)