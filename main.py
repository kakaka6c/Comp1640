from datetime import datetime
import random
from flask import Flask, request, jsonify
import os
import time
import utils
import threading
# os.environ["TZ"] = "Asia/Bangkok"
# time.tzset()
from DatabaseHelper import (
    AdminModel,
    UserModel,
    PostModel,
    CommentModel,
    LikeModel,
    DatabaseHelper,
    EventModel,
    FacultyModel,
    CoordinatorModel,
    CommentPendingModel
)
from bson import ObjectId
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://user:pass@cluster0.z2zlgel.mongodb.net/"
db_helper = DatabaseHelper(app)
MAIN_URL="https://comp1640.pythonanywhere.com/"
# create route for login and return user info


def token_to_uid(authorization_header):
    user_id = ""
    token = None
    role="guest"
    if authorization_header and authorization_header.startswith("Bearer "):
        # Tách chuỗi token từ header 'Authorization'
        try:
            token = authorization_header.split(" ")[1]
            data = UserModel(db_helper).get_role_by_access_token(token)
            user_id = data.get("_id")
            role = data.get("role")
        except Exception as e:
            print(e)
        return str(user_id), role
    else:
        return str(user_id), role

@app.route("/users", methods=["GET"])
def get_users():
    # authorization_header = request.headers.get('Authorization')
    # user_id,role = token_to_uid(authorization_header)

    users = AdminModel(db_helper).get_users()
    json_data = [
        {
            "_id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
        for user in users
    ]
    return jsonify(json_data)

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    # print(user_id)
    user = UserModel(db_helper).get_user(user_id)
    # print(user)
    if user:
        # Trả về thông tin cần thiết trong định dạng JSON
        user_data = {
            "name": user["name"],
            "email": user["email"],
            "faculty": user["faculty"],
            "role": user["role"],
        }
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/add_user", methods=["POST"])
def add_user():
    user = request.json
    result = AdminModel(db_helper).add_user(user)
    if result:
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"message": "Failed to add user"}), 400

@app.route("/update_user/<user_id>", methods=["PUT"])
def update_user(user_id):
    user = request.json
    result = AdminModel(db_helper).update_user(str(user_id), user)
    if result:
        return jsonify({"message": "User updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update user"}), 400

@app.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    result = AdminModel(db_helper).delete_user(str(user_id))
    if result:
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete user"}), 400

@app.route("/all_posts", methods=["GET"])
def get_all_posts():
    authorization_header = request.headers.get("Authorization")
    role=""
    if not authorization_header:
        role="guests"
    if role == "guests":
        pass
    else:
        user_id, role = token_to_uid(authorization_header)
    # print(user_id, role)
    if role != "admin" and role != "marketing manager" and role != "marketing coordinator" and role != "guests":
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        posts = PostModel(db_helper).get_all_posts()
        json_data = []
        for post in posts:
            try:
                user_id_post = str(post["user"])
                # print(user_id)
                if role == "guests":
                    is_like=False
                else:
                    is_like =LikeModel(db_helper).is_liked(user_id +"_"+str(post["_id"]))
                # print(is_like)
                user_info = UserModel(db_helper).get_user(user_id_post)
                event_name=EventModel(db_helper).get_event(post["event"])["event_name"]
                event_id=post["event"]
                post_data = {
                    "_id": str(post["_id"]),
                    "user": {
                        "_id": str(user_info["_id"]),
                        "name": user_info.get("name", ""),
                        "email": user_info.get("email", ""),
                    },
                    "event_name": event_name,
                    "event_id": str(event_id),
                    "is_liked": is_like,
                    "image": post.get("image", ""),
                    "file": post.get("file", ""),
                    "likes": post.get("likes", 0),
                    "comments": post.get("comments", 0),
                    "comments_list": get_comments_by_post(str(post["_id"])),
                    "is_anonymous": post.get("is_anonymous", False),
                    "created_at": calculate_time_difference(post.get("created_at", "")),
                }
                json_data.append(post_data)

            except Exception as e:
                print(e)
        return jsonify(json_data)

# create route get all post
@app.route("/get_posts", methods=["GET"])
def get_posts():
    # Lấy thông tin về người dùng từ token và show posts theo faculty
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        user_id, role = token_to_uid(authorization_header)
        if role != "student" and role != "marketing coordinator":
            return jsonify({"message": "You are not allowed to view posts"}), 403
        else:
            try:
                faculty = FacultyModel(db_helper).get_faculty_by_user(user_id)
                posts = PostModel(db_helper).get_posts_by_faculty(faculty,"published")
                json_data = []
                for post in posts:
                    user_id_post = str(post["user"])
                    user_info = UserModel(db_helper).get_user(user_id_post)
                    event_name=EventModel(db_helper).get_event(post["event"])["event_name"]
                    event_id=post["event"]
                    post_data = {
                        "_id": str(post["_id"]),
                        "user": {
                            "_id": str(user_info["_id"]),
                            "name": user_info.get("name", ""),
                            "email": user_info.get("email", ""),
                        },
                        "is_liked": LikeModel(db_helper).is_liked(user_id +"_"+str(post["_id"])),
                        "event_name": event_name,
                        "event_id": str(event_id),
                        "image": post.get("image", ""),
                        "file": post.get("file", ""),
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "comments_list": get_comments_by_post(str(post["_id"])),
                        "is_anonymous": post.get("is_anonymous", False),
                        "created_at": calculate_time_difference(post.get("created_at", "")),
                    }
                    json_data.append(post_data)
                return jsonify(json_data)
            except Exception as e:
                return jsonify({"message": "Failed to get posts"}), 500

@app.route("/get_posts/guests", methods=["GET"])
def get_guests():
    try:
        posts = PostModel(db_helper).get_all_posts()
        json_data = []
        for post in posts:
            user_id_post = str(post["user"])
            user_info = UserModel(db_helper).get_user(user_id_post)
            event_name=EventModel(db_helper).get_event(post["event"])["event_name"]
            event_id=post["event"]
            post_data = {
                "_id": str(post["_id"]),
                "user": {
                    "_id": str(user_info["_id"]),
                    "name": user_info.get("name", ""),
                    "email": user_info.get("email", ""),
                },
                "event_name": event_name,
                "event_id": str(event_id),
                "image": post.get("image", ""),
                "file": post.get("file", ""),
                "likes": post.get("likes", 0),
                "comments": post.get("comments", 0),
                "comments_list": get_comments_by_post(str(post["_id"])),
                "is_anonymous": post.get("is_anonymous", False),
                "created_at": calculate_time_difference(post.get("created_at", "")),
            }
            json_data.append(post_data)
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"message": "Failed to get posts"}), 500

@app.route("/get_my_posts/<status>", methods=["GET"])
def get_my_posts(status):
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        try:
            posts = PostModel(db_helper).get_posts_by_user(user_id,status)
            json_data = []
            for post in posts:
                user_id_post = str(post["user"])
                user_info = UserModel(db_helper).get_user(user_id_post)
                event_name=EventModel(db_helper).get_event(post["event"])["event_name"]
                event_id=post["event"]
                post_data = {
                    "_id": str(post["_id"]),
                    "user": {
                        "_id": str(user_info["_id"]),
                        "name": user_info.get("name", ""),
                        "email": user_info.get("email", ""),
                    },
                    "event_name": event_name,
                    "event_id": str(event_id),
                    "image": post.get("image", ""),
                    "file": post.get("file", ""),
                    "comments": post.get("comments", 0),
                    "comments_list": get_comment_pending_by_post(str(post["_id"])),
                    "is_anonymous": post.get("is_anonymous", False),
                    "created_at": calculate_time_difference(post.get("created_at", "")),
                }
                json_data.append(post_data)
            return jsonify(json_data)
        except Exception as e:
            return jsonify({"message": "Failed to get posts"}), 500

# create route add post
@app.route("/add_post", methods=["POST"])
def add_post():
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to add post"}), 403
    else:
        try:
            if "event" not in request.form:
                return jsonify({"message": "Missing required fields (event)"}), 400

            # Nhận dữ liệu post từ form
            post_data = request.form.to_dict()

            # Nếu có hình ảnh được gửi kèm
            if 'images' in request.files:
                image_files = request.files.getlist('images')
                # print(image_files)
                images=""
                for image_file in image_files:
                    try:
                        # Lưu hình ảnh vào thư mục hoặc lưu trữ bất kỳ cơ sở dữ liệu nào bạn muốn
                        # Sau đó, lưu đường dẫn hoặc thông tin cần thiết vào images list
                        images+=save_image(image_file)+","
                    except Exception as e:
                        print(e)
                # print(images)
                post_data['image'] = images[:-1]

            # Nếu có tệp tin được gửi kèm
            if 'documents' in request.files:
                file_files = request.files.getlist('documents')
                files = ""
                for file in file_files:
                    try:
                        # Lưu tệp tin vào thư mục hoặc lưu trữ bất kỳ cơ sở dữ liệu nào bạn muốn
                        # Sau đó, lưu đường dẫn hoặc thông tin cần thiết vào files list
                        files+=save_file(file)+","
                    except Exception as e:
                        print(e)
                post_data['file'] = files[:-1]

            # Thêm thông tin về người dùng và thời gian tạo
            post_data["user"] = user_id
            # Get faculty xong sau đó sẽ thêm faculty vào form
            post_data["created_at"] = datetime.now()
            post_data["faculty"] = UserModel(db_helper).get_user(user_id)["faculty"]
            if post_data["is_anonymous"].lower() == "true":
                post_data["is_anonymous"] = True
            else:
                post_data["is_anonymous"] = False
            post_data["status"] = "pending"
            # print("post_data >>>>>>",post_data)
            result = PostModel(db_helper).add_post(post_data)

            if result.inserted_id:
                user_name=UserModel(db_helper).get_user(user_id)["name"]
                threading.Thread(target=send_email, args=(user_name+" đã đăng một bài viết mới trên Greenwich Blog.Hãy vào check nhé !!!",)).start()
                return jsonify({"message": "Post successfully, wait approve from MC"}), 201
            else:
                return jsonify({"message": "Failed to add post"}), 400
        except Exception as e:
            print(e)
            return jsonify({"message": "Failed to add post"}), 400

def send_email(body):
    coordinators=CoordinatorModel(db_helper).get_coordinators()
    for coordinator in coordinators:
        utils.send_email(coordinator["email"], body)
    return True

def save_image(image_file):
    if image_file:
        # Tạo thư mục nếu nó chưa tồn tại
        if not os.path.exists('assets/images'):
            os.makedirs('assets/images')

        # Tạo timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Lấy phần mở rộng của ảnh
        image_extension = os.path.splitext(image_file.filename)[1]
        random_number = str(random.randint(100000, 999999))
        # Đặt tên cho ảnh
        filename = f"Image_{timestamp}_{random_number}{image_extension}"

        # Tạo đường dẫn đầy đủ đến ảnh
        filepath = os.path.join('assets/images', filename)

        # Lưu ảnh vào thư mục
        image_file.save(filepath)

        # Trả về đường dẫn của ảnh đã lưu
        return MAIN_URL+"images/"+filename
    else:
        return None

def save_file(file):
    if file:
        # Tạo thư mục nếu nó chưa tồn tại
        if not os.path.exists('assets/files'):
            os.makedirs('assets/files')

        # Tạo timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Lấy phần mở rộng của tệp tin
        file_extension = os.path.splitext(file.filename)[1]
        random_number = str(random.randint(100000, 999999))
        # Đặt tên cho tệp tin
        filename = f"File_{timestamp}_{random_number}{file_extension}"

        # Tạo đường dẫn đầy đủ đến tệp tin
        filepath = os.path.join('assets/files', filename)

        # Lưu tệp tin vào thư mục
        file.save(filepath)

        # Trả về đường dẫn của tệp tin đã lưu
        return MAIN_URL+"files/"+filename
    else:
        return None

# create route get post by id
@app.route("/comments/<post_id>", methods=["GET"])
def get_comments(post_id):
    comments = CommentModel(db_helper).get_comments_by_post(post_id)
    json_data = []
    for comment in comments:
        user_id = comment["user"]
        user_info = UserModel(db_helper).get_user(user_id)
        comment_data = {
            "post_id": str(comment["_id"]),
            "user": {
                "user_id": str(user_info["_id"]),
                "name": user_info.get("name", ""),
                "email": user_info.get("email", ""),
            },
            "comment": comment["comment"],
            "created_at": comment["created_at"],
        }
        json_data.append(comment_data)
    return jsonify(json_data)

# create route add comment
@app.route("/add_comment", methods=["POST"])
def add_comment():
    try:
        authorization_header = request.headers.get("Authorization")
        user_id, role = token_to_uid(authorization_header)
        if role != "student" and "coordinator" not in role:
            return jsonify({"message": "You are not allowed to add comment"}), 403
        else:
            comment = request.json

            # Kiểm tra các trường bắt buộc
            if not all(key in comment for key in ["comment", "post"]):
                return jsonify({"message": "Missing required fields"}), 400

            # Chuyển đổi chuỗi ObjectId sang ObjectId
            try:
                comment["post"] = ObjectId(comment["post"])
                comment["user"] = ObjectId(user_id)
            except Exception as e:
                return jsonify({"message": "Invalid ObjectId format"}), 400

            # Check to see if the post has existed for more than 14 days
            post = PostModel(db_helper).get_post(comment["post"])

            # Thêm trường created_at nếu không được cung cấp
            if "created_at" not in comment:
                comment["created_at"] = datetime.now()

            # Thêm comment vào collection
            result = CommentModel(db_helper).add_comment(comment)

            # Kiểm tra kết quả và trả về thông báo tương ứng
            if result.inserted_id:
                # đổi số lượng comment +=1
                post = PostModel(db_helper).get_post(comment["post"])
                try:
                    post["comments"]
                except:
                    post["comments"] = 0
                PostModel(db_helper).update_post(
                    comment["post"], {"comments": post["comments"] + 1}
                )
                count_comment=CommentModel(db_helper).count_comment(comment["post"])
                comment_list=get_comments_by_post(comment["post"])

                return (
                    jsonify(
                        {
                            "message": "Comment added successfully",
                            "comments": count_comment,
                            "comment_list": comment_list,
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"message": "Failed to add comment - top"}), 500
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to add comment - bot"}), 500

# create route delete comment
@app.route("/delete_comment/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = CommentModel(db_helper).get_comment(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to delete comment"}), 403
    else:
        if str(comment["user"]) != user_id:
            return jsonify({"message": "You are not allowed to delete this comment"}), 403
        result = CommentModel(db_helper).delete_comment(comment_id)
        if not result:
            return jsonify({"message": "Failed to delete comment"}), 500
        post = PostModel(db_helper).get_post(comment["post"])
        PostModel(db_helper).update_post(
            comment["post"], {"comments": post["comments"] - 1}
        )
        count_comment=CommentModel(db_helper).count_comment(comment["post"])
        comment_list=get_comments_by_post(comment["post"])
        return (
            jsonify(
                {
                    "message": "Comment deleted successfully",
                    "comments": count_comment,
                    "comment_list": comment_list,
                }
            ),
            200,
        )

@app.route("/update_comment/<comment_id>", methods=["PUT"])
def update_comment(comment_id):
    content = request.json.get("comment", "")
    comment = CommentModel(db_helper).get_comment(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to delete comment"}), 403
    else:
        result = CommentModel(db_helper).update_comment(comment_id, content)
        if not result:
            return jsonify({"message": "Failed to delete comment"}), 500
        count_comment=CommentModel(db_helper).count_comment(comment["post"])
        comment_list=get_comments_by_post(comment["post"])
        return (
            jsonify(
                {
                    "message": "Comment deleted successfully",
                    "comments": count_comment,
                    "comment_list": comment_list,
                }
            ),
            200,
        )
# create route count comments by post
@app.route("/count_comments/<post_id>", methods=["GET"])
def count_comments(post_id):
    count = CommentModel(db_helper).count_comment(post_id)
    return jsonify({"count": count})

# create route count comments by event
@app.route("/count_comments/event/<event_id>", methods=["GET"])
def count_comments_for_event(event_id):
    count = CommentModel(db_helper).count_comments_for_event(event_id)
    return jsonify({"count": count})

# create route count comments by faculty
@app.route("/count_comments/faculty/<faculty_id>", methods=["GET"])
def count_comments_for_faculty(faculty_id):
    count = CommentModel(db_helper).count_comments_for_faculty(faculty_id)
    return jsonify({"count": count})

# create route count comments by user
@app.route("/count_comments/user/<user_id>", methods=["GET"])
def count_comments_for_user(user_id):
    count = CommentModel(db_helper).count_comments_for_user(user_id)
    return jsonify({"count": count})

@app.route("/add_like", methods=["POST"]) # Done
def add_like():
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to like"}), 403
    else:
        try:
            like = request.json
            # create sample json
            like["user"] = ObjectId(user_id)
            like["created_at"] = datetime.now()
            like["post"] = ObjectId(like["post"])
            like["like_id"] = user_id+"_"+str(like["post"])
            # check if user liked this post before
            # if LikeModel(db_helper).is_liked(like["l +"_"+e_id"]):
            #     return jsonify({"message": "You have already liked this post"}), 400
            try:
                result = LikeModel(db_helper).add_like(like)
            except Exception as e:
                print(e)
                return jsonify({"message": "You want to spam like ?????"}), 500
            # count likes now
            count = LikeModel(db_helper).count_likes_for_post(like["post"])
            # update likes count
            PostModel(db_helper).update_post(like["post"], {"likes": count})
            # return message and current like count
            if result:
                return jsonify({"message": "Like added successfully", "likes": count}), 200
            else:
                return jsonify({"message": "Failed to add like"}), 500
        except Exception as e:
            print(e)
            return jsonify({"message": "Failed to add like"}), 500

@app.route("/remove_like", methods=["POST"])
def remove_like():
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to remove likes"}), 403
    else:
        like = request.json
        like["user"] = ObjectId(user_id)
        like["post"] = ObjectId(like["post"])
        like["like_id"] = str(like["user"])+"_"+str(like["post"])
        # check if user liked this post before
        if not LikeModel(db_helper).is_liked(like["like_id"]):
            return jsonify({"message": "You have not liked this post"}), 400
        result = LikeModel(db_helper).remove_like(like["like_id"])
        if not result:
            return jsonify({"message": "Failed to remove like"}), 500

        # Cập nhật lại số lượng likes cho bài đăng
        count = LikeModel(db_helper).count_likes_for_post(like["post"])
        PostModel(db_helper).update_post(like["post"], {"likes": count})

        return jsonify({"message": "Like removed successfully", "likes": count}), 200

@app.route("/count_likes/<post_id>", methods=["GET"])
def count_likes(post_id):
    count = LikeModel(db_helper).count_likes_for_post(post_id)
    return jsonify({"count": count})

@app.route("/count_likes/event/<event_id>", methods=["GET"])
def count_likes_for_event(event_id):
    count = LikeModel(db_helper).count_likes_for_event(event_id)
    return jsonify({"count": count})

@app.route("/count_likes/faculty/<faculty_id>", methods=["GET"])
def count_likes_for_faculty(faculty_id):
    count = LikeModel(db_helper).count_likes_for_faculty(faculty_id)
    return jsonify({"count": count})

@app.route("/count_likes/user/<user_id>", methods=["GET"])
def count_likes_for_user(user_id):
    count = LikeModel(db_helper).count_likes_for_user(user_id)
    return jsonify({"count": count})

# create route get all events
@app.route("/events", methods=["GET"])
def get_events():
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return jsonify({"message": "You are not allowed to view events"}), 403
    else:
        user_id, role = token_to_uid(authorization_header)
        if role != "student" and role != "admin":
            return jsonify({"message": "You are not allowed to view events"}), 403
        else:
            try:
                faculty= FacultyModel(db_helper).get_faculty_by_user(user_id)
                events = EventModel(db_helper).get_event_by_faculty(faculty)
                json_data = []
                for event in events:
                    event_data = {
                        "_id": str(event["_id"]),
                        "name": event.get('event_name', ''),
                        "start_at": event.get("first_closure_date", ''),
                        "end_at": event.get("final_closure_date", ''),
                        "description": event.get('event_description', '')
                    }
                    json_data.append(event_data)
                print(json_data)

                return jsonify(json_data)
            except Exception as e:
                return jsonify({"message": "Failed to get events"}), 500

def get_user_info(user_id):
    user_info = UserModel(db_helper).get_user(user_id)
    return {
        "_id": str(user_info["_id"]),
        "name": user_info.get("name", ""),
        "email": user_info.get("email", ""),
    }

def get_comments_by_post(post_id):
    comments = CommentModel(db_helper).get_comments_by_post(post_id)
    json_data = []
    for comment in comments:
        user_id = comment["user"]
        user_info = UserModel(db_helper).get_user(user_id)
        comment_data = {
            "_id": str(comment["_id"]),
            "user": {
                "_id": str(user_info["_id"]),
                "name": user_info.get("name", ""),
                "email": user_info.get("email", ""),
            },
            "comment": comment["comment"],
            "created_at": calculate_time_difference(str(comment["created_at"])),
        }
        json_data.append(comment_data)
    return json_data

def get_comment_pending_by_post(post_id):
    comments = CommentPendingModel(db_helper).get_comments_by_post(post_id)
    json_data = []
    for comment in comments:
        user_id = comment["user"]
        user_info = UserModel(db_helper).get_user(user_id)
        comment_data = {
            "_id": str(comment["_id"]),
            "user": {
                "_id": str(user_info["_id"]),
                "name": user_info.get("name", ""),
                "email": user_info.get("email", ""),
            },
            "comment": comment["comment"],
            "created_at": calculate_time_difference(str(comment["created_at"])),
        }
        json_data.append(comment_data)
    return json_data

# create route get post from event
@app.route("/posts/event/<event_id>", methods=["GET"])
def get_posts_by_event(event_id):
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        user_id, role = token_to_uid(authorization_header)
        if role != "student" and role != "admin":
            return jsonify({"message": "You are not allowed to view posts"}), 403
        else:
            # Lấy thông tin về sự kiện từ event_id

            event_info = EventModel(db_helper).get_event(event_id)
            if not event_info:
                return jsonify({"message": "Event not found"}), 404

            event_name = event_info.get("event_name", "")

            # Lấy danh sách bài viết từ sự kiện
            posts = PostModel(db_helper).get_posts_by_event(event_id)
            json_data = {
                "event_name": event_name,
                "posts": []  # Khởi tạo danh sách bài viết
            }
            for post in posts:
                try:
                    user_id_post = str(post["user"])
                    user_info = UserModel(db_helper).get_user(user_id_post)
                    post_data = {
                        "_id": str(post["_id"]),
                        "user": {
                            "_id": str(user_info["_id"]),
                            "name": user_info.get("name", ""),
                            "email": user_info.get("email", ""),
                        },
                        "is_liked": LikeModel(db_helper).is_liked(user_id +"_"+str(post["_id"])),
                        "caption": post.get("caption", ""),
                        "description": post.get("description", ""),
                        "image": post.get("image", None),
                        "file": post.get("file", None),
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "comments_list": get_comments_by_post(str(post["_id"])),
                        "is_anonymous": post.get("is_anonymous", False),
                        "created_at": calculate_time_difference(post.get("created_at", "")),
                    }
                    json_data["posts"].append(post_data)  # Thêm bài viết vào danh sách
                except Exception as e:
                    print(e)

            return jsonify(json_data)

def calculate_time_difference(timestamp_str):
    # Chuyển timestamp từ chuỗi thành đối tượng datetime
    dt_timestamp = datetime.strptime(str(timestamp_str), "%Y-%m-%d %H:%M:%S.%f")
    # Lấy thời gian hiện tại
    dt_now = datetime.now()
    # Tính toán khoảng cách thời gian giữa timestamp và thời gian hiện tại
    time_difference = dt_now - dt_timestamp
    # Chuyển đổi thời gian thành phút, giờ, ngày
    minutes = int(time_difference.total_seconds() / 60)
    hours = int(minutes / 60)
    days = int(hours / 24)
    # Xử lý kết quả
    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "A few seconds"

# ######## Cordinator ########
@app.route("/get_posts_cordinator/<userId>", methods=["GET"])
def get_posts_cordinator(userId):
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "cordinator":
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        try:
            posts = PostModel(db_helper).get_posts_by_user(userId)
            json_data = []
            for post in posts:
                user_id_post = str(post["user"])
                user_info = UserModel(db_helper).get_user(user_id_post)
                post_data = {
                    "_id": str(post["_id"]),
                    "user": {
                        "_id": str(user_info["_id"]),
                        "name": user_info.get("name", ""),
                        "email": user_info.get("email", ""),
                    },
                    "caption": post.get("caption", ""),
                    "description": post.get("description", ""),
                    "image": post.get("image", ""),
                    "file": post.get("file", ""),
                    "likes": post.get("likes", 0),
                    "comments": post.get("comments", 0),
                    "comments_list": get_comments_by_post(str(post["_id"])),
                    "is_anonymous": post.get("is_anonymous", False),
                    "created_at": calculate_time_difference(post.get("created_at", "")),
                }
                json_data.append(post_data)
            return jsonify(json_data)
        except Exception as e:
            return jsonify({"message": "Failed to get posts"}), 500

@app.route("/count_posts_cordinator/<userId>", methods=["GET"])
def count_posts_cordinator(userId):
    count = PostModel(db_helper).count_posts_by_user(userId)
    return jsonify({"count": count})

@app.route("/load_posts_cordinator", methods=["GET"])
def load_posts_cordinator():
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if "coordinator" not in role:
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        try:
            faculty=UserModel(db_helper).get_user(user_id)["faculty"]
            posts = PostModel(db_helper).get_posts_by_faculty(faculty)
            json_data = []
            for post in posts:
                if post["status"] == "published":
                    comment_list=get_comments_by_post(str(post["_id"]))
                else:
                    comment_list=get_comment_pending_by_post(str(post["_id"]))
                user_id_post = str(post["user"])
                user_info = UserModel(db_helper).get_user(user_id_post)
                event_name=EventModel(db_helper).get_event(post["event"])["event_name"]
                event_id=post["event"]

                post_data = {
                    "_id": str(post["_id"]),
                    "user": {
                        "_id": str(user_info["_id"]),
                        "name": user_info.get("name", ""),
                        "email": user_info.get("email", ""),
                    },
                    "status": post.get("status", "pending"),
                    "description": post.get("description", ""),
                    "image": post.get("image", ""),
                    "event_name": event_name,
                    "event_id": str(event_id),
                    "file": post.get("file", ""),
                    "comments_list": comment_list,
                    "is_anonymous": post.get("is_anonymous", False),
                    "created_at": calculate_time_difference(post.get("created_at", "")),
                }
                json_data.append(post_data)
            return jsonify(json_data)
        except Exception as e:
            print(e)
            return jsonify({"message": "Failed to get posts"}), 500


# add comment bởi cordinator
@app.route("/add_comment_pending", methods=["POST"])
def add_comment_pending():
    try:
        authorization_header = request.headers.get("Authorization")
        user_id, role = token_to_uid(authorization_header)
        if "coordinator" not in role and role != "student":
            return jsonify({"message": "You are not allowed to add comment"}), 403
        else:
            comment = request.json

            # Kiểm tra các trường bắt buộc
            if not all(key in comment for key in ["comment", "post"]):
                return jsonify({"message": "Missing required fields"}), 400

            # Chuyển đổi chuỗi ObjectId sang ObjectId
            try:
                comment["post"] = ObjectId(comment["post"])
                comment["user"] = ObjectId(user_id)
            except Exception as e:
                return jsonify({"message": "Invalid ObjectId format"}), 400

            # Thêm trường created_at nếu không được cung cấp
            if "created_at" not in comment:
                comment["created_at"] = datetime.now()

            # Thêm comment vào collection
            result = CommentPendingModel(db_helper).add_comment_pending(comment)

            # Kiểm tra kết quả và trả về thông báo tương ứng
            if result.inserted_id:
                comment_list=get_comment_pending_by_post(comment["post"])
                print(comment_list)
                return (
                    jsonify(
                        {
                            "message": "Comment added successfully",
                            "comment_list": comment_list,
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"message": "Failed to add comment - top"}), 500
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to add comment - bot"}), 500

def is_in_14days(date):
    date = datetime.strptime(date, "%Y-%m-%d")
    now = datetime.now()
    delta = now - date
    if delta.days <= 14:
        return True
    return False

@app.route("/approve_post", methods=["POST"])
def approve_post():
    data=request.json
    post_id=data["post_id"]
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if "coordinator" not in role:
        return jsonify({"message": "You are not allowed to approve post"}), 403

    post = PostModel(db_helper).get_post(post_id)
    author=UserModel(db_helper).get_user(str(post["user"]))
    user_mail=author["email"]
    utils.send_email(user_mail, "Bài viết của bạn đã được duyệt và đã được đăng trên trang chủ của Greenwich Blog", "Bài viết của bạn đã được duyệt!!!")
    if not post:
        return jsonify({"message": "Post not found"}), 404
    if post["status"] == "published":
        return jsonify({"message": "Post has already been approved"}), 400
    result = PostModel(db_helper).update_post(post_id, {"status": "published"})
    if not result:
        return jsonify({"message": "Failed to approve post"}), 500
    return jsonify({"message": "Post approved successfully"}), 200



if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)
    