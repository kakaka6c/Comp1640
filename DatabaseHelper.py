from pymongo import MongoClient
from bson import ObjectId

class DatabaseHelper:
    def __init__(self, app=None):
        self.client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        mongo_uri = app.config.get('MONGO_URI')
        if mongo_uri:
            self.client = MongoClient(mongo_uri)
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
    
class AdminModel:
    def __init__(self, db_helper):
        self.db_helper = db_helper

    def get_users(self):
        db = self.db_helper.get_db()
        collection = db['comp1640']['users']
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