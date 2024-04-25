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
        return collection.find_one({"accessToken": access_token}, {"_id": 1, "role": 1})

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

    def get_event(self, event_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['events']
        return collection.find_one({"_id": ObjectId(event_id)})
    
    def get_event_by_faculty(self, faculty_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['events']
        return collection.find({"faculty": ObjectId(faculty_id)})
    
class FacultyModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_faculties(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['faculties']
        return collection.find()

    def get_faculty(self, faculty_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['faculties']
        return collection.find_one({"_id": ObjectId(faculty_id)})

    def get_faculty_by_user(self, user_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        user = collection.find_one({"_id": ObjectId(user_id)})
        return user.get("faculty", None)

    def count_posts_by_faculty(self, faculty_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.count_documents({"faculty": ObjectId(faculty_id)})

class PostModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_posts_by_user(self, user_id,status="published"):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find({"user": ObjectId(user_id),"status": status})

    def get_posts_by_faculty(self, faculty_id,status=None):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        if status is None:
            return collection.find({"faculty": ObjectId(faculty_id)})
        return collection.find({"faculty": ObjectId(faculty_id),"status": status})

    def get_posts_by_event(self, event_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find({"event": ObjectId(event_id),"status": "published"}, sort=[("created_at", -1)])

    def get_all_posts(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find({"status": "published"},sort=[("created_at", -1)])   

    def get_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.find_one({"_id": ObjectId(post_id)})

    def add_post(self, post):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        post["event"] = ObjectId(post["event"])
        post["faculty"] = ObjectId(post["faculty"])
        post["user"] = ObjectId(post["user"])
        return collection.insert_one(post)

    def update_post(self, post_id, post):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.update_one({"_id": ObjectId(post_id)}, {"$set": post})

    def delete_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.delete_one({"_id": ObjectId(post_id)})

    def count_posts_by_user(self, user_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        return collection.count_documents({"user": ObjectId(user_id)})

    def search_title(self, title):
        db = self.db_helper.get_db()
        collection = db['comp1640']['posts']
        # find all posts that contain the title
        return collection.find({"caption": {"$regex": title, "$options": "i"}})

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
        return collection.update_one({"_id": ObjectId(comment_id)}, {"$set": {"comment": comment}})

    def delete_comment(self, comment_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.delete_one({"_id": ObjectId(comment_id)})

    def count_comment(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments']
        return collection.count_documents({"post": ObjectId(post_id)})

    def count_comments_for_event(self, event_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong event dựa trên event_id
        posts = db['comp1640']['posts'].find({"event": ObjectId(event_id)})

        # Khởi tạo biến tổng số lượng comments
        total_comments = 0

        # Duyệt qua từng bài post và tính tổng số lượng comments
        for post in posts:
            total_comments += post.get("comments", 0)

        return total_comments

    def count_comments_for_faculty(self, faculty_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong faculty dựa trên faculty_id
        posts = db['comp1640']['posts'].find({"faculty": ObjectId(faculty_id)})

        # Khởi tạo biến tổng số lượng comments
        total_comments = 0

        # Duyệt qua từng bài post và tính tổng số lượng comments
        for post in posts:
            total_comments += post.get("comments", 0)

        return total_comments

    def count_comments_for_user(self, user_id):
        # truy vấn tất cả comments của user dựa trên user_id
        db=self.db_helper.get_db()
        comments = db['comp1640']['comments'].count_documents({"user": ObjectId(user_id)})
        return comments

    def count_comments_for_post(self, post_id):
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

    def is_liked(self, like_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.find_one({"like_id":like_id}) is not None

    def update_like(self, like_id, like):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.update_one({"_id": ObjectId(like_id)}, {"$set": like})

    def remove_like(self, like_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['likes']
        return collection.delete_one({"like_id": like_id})

    def count_likes_for_event(self, event_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong event dựa trên event_id
        posts = db['comp1640']['posts'].find({"event": ObjectId(event_id)})

        # Khởi tạo biến tổng số lượng likes
        total_likes = 0

        # Duyệt qua từng bài post và tính tổng số lượng likes
        for post in posts:
            total_likes += post.get("likes", 0)

        return total_likes

    def count_likes_for_faculty(self, faculty_id):
        db=self.db_helper.get_db()
        # Truy vấn tất cả các bài post trong faculty dựa trên faculty_id
        posts = db['comp1640']['posts'].find({"faculty": ObjectId(faculty_id)})

        # Khởi tạo biến tổng số lượng likes
        total_likes = 0

        # Duyệt qua từng bài post và tính tổng số lượng likes
        for post in posts:
            total_likes += post.get("likes", 0)

        return total_likes

    def count_likes_for_user(self, user_id):
        # truy vấn tất cả likes của user dựa trên user_id
        db=self.db_helper.get_db()
        likes = db['comp1640']['likes'].count_documents({"user": ObjectId(user_id)})
        return likes

    def count_likes_for_post(self, post_id):
        # truy vấn tất cả likes của post dựa trên post_id
        db=self.db_helper.get_db()
        likes = db['comp1640']['likes'].count_documents({"post": ObjectId(post_id)})
        return likes

class CoordinatorModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_coordinators(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.find({"role": "marketing coordinator"})

    def get_coordinator(self, coordinator_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
        return collection.find_one({"_id": ObjectId(coordinator_id)})
    
class CommentPendingModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_comments_pending(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.find()

    def get_comment_pending(self, comment_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.find_one({"_id": ObjectId(comment_id)})

    def get_comments_by_post(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.find({"post": ObjectId(post_id)})

    def add_comment_pending(self, comment):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.insert_one(comment)

    def update_comment_pending(self, comment_id, comment):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.update_one({"_id": ObjectId(comment_id)}, {"$set": comment})

    def delete_comment_pending(self, comment_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.delete_one({"_id": ObjectId(comment_id)})

    def count_comment_pending(self, post_id):
        db = self.db_helper.get_db()
        collection = db['comp1640']['comments_pending']
        return collection.count_documents({"post": ObjectId(post_id)})
    