from pymongo.mongo_client import MongoClient
from bson import ObjectId

class DatabaseHelper:
    def __init__(self, app=None):
        self.client = None
        if app is not None:
            self.init_app(app)
        print(app.config.get('MONGO_URI'))
    def init_app(self, app):
        mongo_uri = app.config.get('MONGO_URI')
        if mongo_uri:
            self.client = MongoClient(mongo_uri,connectTimeoutMS=30000, socketTimeoutMS=None, connect=False, maxPoolsize=1)
        else:
            raise ValueError("No MongoDB URI provided in the app configuration.")

    def get_db(self, db_name=None):
        if self.client:
            return self.client[db_name] if db_name else self.client
        else:
            raise ValueError("No MongoDB client available.")

    def close_connection(self):
        if self.client:
            self.client.close()

class UserModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_user(self, user_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.find_one({"_id": ObjectId(user_id)})

    def get_role_by_access_token(self, access_token):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        # return _id and role of user
        return collection.find_one({"access_token": access_token}, {"_id": 1, "role": 1})

class AdminModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_users(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        for user in collection.find():
            print(user)
        return collection.find()

    def add_user(self, user):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.insert_one(user)

    def update_user(self, user_id, user):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.update_one({"_id": ObjectId(user_id)}, {"$set": user})

    def delete_user(self, user_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.delete_one({"_id": ObjectId(user_id)})

class EventModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_events(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['events']
        return collection.find()

class FacultyModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_faculties(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['faculties']
        return collection.find()

class PostModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_posts_by_faculty(self, faculty_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find({"faculty": ObjectId(faculty_id)})

    def get_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find_one({"_id": ObjectId(post_id)})

    def add_post(self, post):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.insert_one(post)

    def update_post(self, post_id, post):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.update_one({"_id": ObjectId(post_id)}, {"$set": post})

    def delete_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.delete_one({"_id": ObjectId(post_id)})

class CommentModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_comments_by_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.find({"post": ObjectId(post_id)})

    def get_comment(self, comment_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.find_one({"_id": ObjectId(comment_id)})

    def add_comment(self, comment):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.insert_one(comment)

    def update_comment(self, comment_id, comment):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.update_one({"_id": ObjectId(comment_id)}, {"$set": comment})

    def delete_comment(self, comment_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.delete_one({"_id": ObjectId(comment_id)})

    def count_comment(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.count_documents({"post": ObjectId(post_id)})

    def count_comments_for_event(self,db, event_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong event dựa trên event_id
        posts = db['comp1640']['posts'].find({"event": ObjectId(event_id)})

        # Khởi tạo biến tổng số lượng comments
        total_comments = 0

        # Duyệt qua từng bài post và tính tổng số lượng comments
        for post in posts:
            total_comments += post.get("comments", 0)

        return total_comments

    def count_comments_for_faculty(self,db, faculty_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong faculty dựa trên faculty_id
        posts = db['comp1640']['posts'].find({"faculty": ObjectId(faculty_id)})

        # Khởi tạo biến tổng số lượng comments
        total_comments = 0

        # Duyệt qua từng bài post và tính tổng số lượng comments
        for post in posts:
            total_comments += post.get("comments", 0)

        return total_comments

    def count_comments_for_user(self,db, user_id):
        # truy vấn tất cả comments của user dựa trên user_id
        db=self.db_helper.get_db()
        comments = db['comp1640']['comments'].count_documents({"user": ObjectId(user_id)})
        return comments

    def count_comments_for_post(self,db, post_id):
        # truy vấn tất cả comments của post dựa trên post_id
        db=self.db_helper.get_db()
        comments = db['comp1640']['comments'].count_documents({"post": ObjectId(post_id)})
        return comments

class LikeModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_likes_by_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.find({"post": ObjectId(post_id)})

    def add_like(self, like):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.insert_one(like)

    def update_like(self, like_id, like):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.update_one({"_id": ObjectId(like_id)}, {"$set": like})

    def delete_like(self, like_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.delete_one({"_id": ObjectId(like_id)})

    def count_likes_for_event(self,db, event_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong event dựa trên event_id
        posts = db['comp1640']['posts'].find({"event": ObjectId(event_id)})

        # Khởi tạo biến tổng số lượng likes
        total_likes = 0

        # Duyệt qua từng bài post và tính tổng số lượng likes
        for post in posts:
            total_likes += post.get("likes", 0)

        return total_likes

    def count_likes_for_faculty(self,db, faculty_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong faculty dựa trên faculty_id
        posts = db['comp1640']['posts'].find({"faculty": ObjectId(faculty_id)})

        # Khởi tạo biến tổng số lượng likes
        total_likes = 0

        # Duyệt qua từng bài post và tính tổng số lượng likes
        for post in posts:
            total_likes += post.get("likes", 0)

        return total_likes

    def count_likes_for_user(self,db, user_id):
        # truy vấn tất cả likes của user dựa trên user_id
        db=self.db_helper.get_db()
        likes = db['comp1640']['likes'].count_documents({"user": ObjectId(user_id)})
        return likes

    def count_likes_for_post(self,db, post_id):
        # truy vấn tất cả likes của post dựa trên post_id
        db=self.db_helper.get_db()
        likes = db['comp1640']['likes'].count_documents({"post": ObjectId(post_id)})
        return likes

