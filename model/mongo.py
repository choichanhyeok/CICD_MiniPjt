from pymongo import MongoClient
from CONFIG.account import API_KEY

client = MongoClient(API_KEY)
db = client.Haromony
news = client.news_data.news_data

class DBAdmin():
    @staticmethod
    def get_mongo_connector():
        '''
        API_KEY를 통해 접근하는 클라우드 MONGODB에 client.Harmony 컬렉션에 대한 컨넥터를 반환해준다.
        :return db: API_KEY를 통해 접근하는 클라우드 MONGODB에 client.Harmony 컬렉션에 대한 컨넥터
        '''
        return db

class UserAdmin():
    @staticmethod
    def users_find_one(column, target):   # main_control, join_control에서 사용
        return db.users.find_one({column: target})

    @staticmethod
    def is_customer_check(user_id, pw_hash):  # join_control: checkdup()에 사용
        return db.users.find_one({'user_id': user_id, 'password': pw_hash})

    @staticmethod
    def user_signup_db(doc): # join_control에 사용
        db.users.insert_one(doc)

    @staticmethod
    def users_update_one(payload_id, new_doc):
        return db.users.update_one({'user_id': payload_id}, {'$set': new_doc})


class DetailContents():
    @staticmethod
    def find_post(post_id):   # detail_control에서 사용
        return news.find_one({'post_id': int(post_id)}, {'_id': False})

    @staticmethod
    def count_all_comments():   # detail_control에서 사용
        return db.comments.estimated_document_count()

    @staticmethod
    def count_comments(post_id):   # detail_control에서 사용
        return db.comments.count_documents({'post_id': post_id})

    @staticmethod
    def plus_comment_id():   # detail_control에서 사용
        return db.comments.find_one(sort=[("idx", -1)])['idx'] + 1

    @staticmethod
    def insert_comment(doc):   # detail_control에서 사용
        return db.comments.insert_one(doc)

    @staticmethod
    def delete_comment(comment_idx):   # detail_control에서 사용
        return db.comments.delete_one({'idx': int(comment_idx)})

    @staticmethod
    def insert_action(doc):   # detail_control에서 사용
        return db.action.insert_one(doc)

    @staticmethod
    def delete_action(doc):   # detail_control에서 사용
        return db.action.delete_one(doc)

    @staticmethod
    def count_like(comment_id):   # detail_control에서 사용
        return db.action.count_documents({"like_comment_id": comment_id})

    @staticmethod
    def find_comments(column, target):   # detail_control에서 사용
        return db.comments.find({column: target})

    @staticmethod
    def like_by_me(column, target, user_id):   # detail_control에서 사용
        return db.action.find_one({column: target, "user_id": user_id})

    @staticmethod
    def find_bookmark_post(user_id):   # detail_control에서 사용
        return db.action.find({"user_id": user_id}, {"_id": False, "bookmark_post_id": True})


class Posts():
    @staticmethod
    def add_view_data(doc):           # detail_control에서 사용
        news_db = client.news_data    # 뉴스 db에 조회수 1 더하기
        news_db.news_data.update_one({"post_id": int(doc['post_id'])}, {'$set': {'view':(Posts.count_view(int(doc['post_id']))+1)}})
        db.visit_log.insert_one(doc)  # visit_log에 방문 기록 작성
        return True

    @staticmethod
    def count_view(post_id):
        news_db = client.news_data
        view = news_db.news_data.find_one({'post_id': post_id})['view']
        return view


class AboutComment:  # detail_control에서 사용
    @staticmethod
    def comment_find(key, value):
        return db.comments.find_one({key: value})