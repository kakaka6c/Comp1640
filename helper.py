from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb+srv://manhdc01:12345@cluster0.z2zlgel.mongodb.net/')
db = client['comp1640']


# db.create_collection("posts", validator={
#     "$jsonSchema": {
#         "bsonType": "object",
#         "required": ["user", "caption"],
#         "properties": {
#             "post": {"bsonType": "objectId"},
#             "user": {"bsonType": "objectId"},
#             "event": {"bsonType": "objectId"},
#             "faculty": {"bsonType": "objectId"},
#             "caption": {"bsonType": "string"},
#             "url": {"bsonType": "string"},
#             "likes": {"bsonType": "int", "minimum": 0},
#             "comments": {"bsonType": "int", "minimum": 0},
#             "is_anonymous": {"bsonType": "bool"},
#             "created_at": {"bsonType": "date"}
#         }
#     }
# })

# Tạo bảng Comments với ràng buộc
# db.create_collection("comments", validator={
#     "$jsonSchema": {
#         "bsonType": "object",
#         "required": ["post", "user", "comment","created_at"],
#         "properties": {
#             "comment": {"bsonType": "string"},
#             "post": {"bsonType": "objectId"},
#             "user": {"bsonType": "objectId"},
#             "created_at": {"bsonType": "date"}
#         }
#     }
# })

# create collection likes
# db.create_collection("likes", validator={
#     "$jsonSchema": {
#         "bsonType": "object",
#         "required": ["post", "user"],
#         "properties": {
#             "post": {"bsonType": "objectId"},
#             "user": {"bsonType": "objectId"},
#             "created_at": {"bsonType": "date"}
#         }
#     }
# })
