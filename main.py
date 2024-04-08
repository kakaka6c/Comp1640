from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import time
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
    FacultyModel
)
from bson import ObjectId
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://manhdc01:12345@cluster0.z2zlgel.mongodb.net/"
db_helper = DatabaseHelper(app)
MAIN_URL="https://comp1640.pythonanywhere.com/"
# create route for login and return user info


def token_to_uid(authorization_header):
    user_id = None
    token = None
    role="guest"
    if authorization_header and authorization_header.startswith("Bearer "):
        # Tách chuỗi token từ header 'Authorization'

        token = authorization_header.split(" ")[1]
        data = UserModel(db_helper).get_role_by_access_token(token)
        user_id = data.get("_id")
        role = data.get("role")

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
    if not authorization_header:
        return jsonify({"message": "You are not allowed to view posts"}), 403
    else:
        user_id, role = token_to_uid(authorization_header)
        print(user_id, role)
        if role != "admin":
            return jsonify({"message": "You are not allowed to view posts"}), 403
        else:
            posts = PostModel(db_helper).get_all_posts()
            json_data = []
            for post in posts:
                try:
                    user_id_post = str(post["user"])
                    # print(user_id)
                    user_info = UserModel(db_helper).get_user(user_id_post)
                    post_data = {
                        "_id": str(post["_id"]),
                        "user": {
                            "_id": str(user_info["_id"]),
                            "name": user_info.get("name", ""),
                            "email": user_info.get("email", ""),
                        },
                        "is_liked": LikeModel(db_helper).is_liked(user_id, str(post["_id"])),
                        "caption": post.get("caption", ""),
                        "description": post.get("description", ""),
                        "image": post.get("image", ""),
                        "file": post.get("file", ""),
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "comments_list": get_comments_by_post(str(post["_id"])),
                        "is_anonymous": post.get("is_anonymous", False),
                        "created_at": post.get("created_at", ""),
                    }
                    json_data.append(post_data)
                except Exception as e:
                    print(e)
            return jsonify(json_data)
            
# create route get all post
@app.route("/posts/faculty/<faculty_id>", methods=["POST"])
def get_posts_by_faculty(faculty_id):
    posts = PostModel(db_helper).get_posts_by_faculty(faculty_id)

    json_data = []
    for post in posts:
        user_id = post["user"]  # Lấy user_id từ bài viết

        # Truy vấn thông tin người dùng từ user_id
        user_info = UserModel(db_helper).get_user(user_id)

        # Tạo một JSON object mới chứa thông tin của bài viết và người dùng
        post_data = {
            "_id": str(post["_id"]),
            "user": {
                "_id": str(user_info["_id"]),
                "name": user_info.get("name", ""),
                "email": user_info.get("email", ""),
            },
            "caption": post["caption"],
            "url": post["url"],
            "likes": post["likes"],
            "comments": post["comments"],
            "is_anonymous": post["is_anonymous"],
            "created_at": post["created_at"],
        }
        json_data.append(post_data)

    return jsonify(json_data)

# create route add post
@app.route("/add_post", methods=["POST"])
def add_post():
    authorization_header = request.headers.get("Authorization")
    user_id, role = token_to_uid(authorization_header)
    if role != "student":
        return jsonify({"message": "You are not allowed to add post"}), 403
    else:
        try:
            if "caption" not in request.form or "description" not in request.form or "event" not in request.form:
                return jsonify({"message": "Missing required fields (caption, description, event)"}), 400
            
            # Nhận dữ liệu post từ form
            post_data = request.form.to_dict()
            # Nếu có hình ảnh được gửi kèm
            if 'image' in request.files :
                try:
                    image_file = request.files['image']
                    # Lưu hình ảnh vào thư mục hoặc lưu trữ bất kỳ cơ sở dữ liệu nào bạn muốn
                    
                    # Sau đó, lưu đường dẫn hoặc thông tin cần thiết vào post_data
                    post_data['image'] = save_image(image_file)
                except Exception as e:
                    print(e)
                
            # Nếu có tệp tin được gửi kèm
            if 'file' in request.files:
                try:
                    file = request.files['file']
                    # Lưu tệp tin vào thư mục hoặc lưu trữ bất kỳ cơ sở dữ liệu nào bạn muốn
                    
                    # Sau đó, lưu đường dẫn hoặc thông tin cần thiết vào post_data
                    post_data['file'] = save_file(file)
                except Exception as e:
                    print(e)
            

            # Thêm thông tin về người dùng và thời gian tạo
            post_data["user"] = ObjectId(user_id)
            post_data["created_at"] = datetime.now()
            post_data["faculty"] = UserModel(db_helper).get_user(user_id)["faculty"]
            if post_data["is_anonymous"].lower() == "true":
                post_data["is_anonymous"] = True
            else:
                post_data["is_anonymous"] = False
            result = PostModel(db_helper).add_post(post_data)
            # Trả về kết quả
            if result.inserted_id:
                return jsonify({"message": "Post added successfully"}), 201
            else:
                return jsonify({"message": "Failed to add post"}), 400
        except Exception as e:
            return jsonify({"message": "Failed to add post"}), 400

def save_image(image_file):
    if image_file:
        # Tạo thư mục nếu nó chưa tồn tại
        if not os.path.exists('assets/images'):
            os.makedirs('assets/images')
        
        # Tạo timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Lấy phần mở rộng của ảnh
        image_extension = os.path.splitext(image_file.filename)[1]
        
        # Đặt tên cho ảnh
        filename = f"Image_{timestamp}{image_extension}"
        
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
        
        # Đặt tên cho tệp tin
        filename = f"File_{timestamp}{file_extension}"
        
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
    # Lấy dữ liệu từ request
    comment = request.json

    # Kiểm tra các trường bắt buộc
    if not all(key in comment for key in ["comment", "post", "user"]):
        return jsonify({"message": "Missing required fields"}), 400

    # Chuyển đổi chuỗi ObjectId sang ObjectId
    try:
        comment["post"] = ObjectId(comment["post"])
        comment["user"] = ObjectId(comment["user"])
    except Exception as e:
        return jsonify({"message": "Invalid ObjectId format"}), 400

    # Thêm trường created_at nếu không được cung cấp
    if "created_at" not in comment:
        comment["created_at"] = datetime.now()

    # Thêm comment vào collection
    result = CommentModel(db_helper).add_comment(comment)

    # Kiểm tra kết quả và trả về thông báo tương ứng
    if result.inserted_id:
        # đổi số lượng comment +=1
        post = PostModel(db_helper).get_post(comment["post"])
        PostModel(db_helper).update_post(
            comment["post"], {"comments": post["comments"] + 1}
        )
        return (
            jsonify(
                {
                    "message": "Comment added successfully",
                    "comment_id": str(result.inserted_id),
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "Failed to add comment"}), 500

# create route delete comment
@app.route("/delete_comment/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    comment = CommentModel(db_helper).get_comment(comment_id)
    post = PostModel(db_helper).get(comment["post"])
    result = CommentModel(db_helper).delete_comment(comment_id)
    if result:
        PostModel(db_helper).update_post(
            comment["post"], {"comments": post["comments"] - 1}
        )
        return jsonify({"message": "Comment deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete comment"}), 500

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

@app.route("/add_like", methods=["POST"])
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
            
            result = LikeModel(db_helper).add_like(like)
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
        
        # Xóa like từ bảng
        result = LikeModel(db_helper).remove_like(like)
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
            "created_at": str(comment["created_at"]),
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
                        "is_liked": LikeModel(db_helper).is_liked(user_id, str(post["_id"])),
                        "caption": post.get("caption", ""),
                        "description": post.get("description", ""),
                        "image": post.get("image", ""),
                        "file": post.get("file", ""),
                        "likes": post.get("likes", 0),
                        "comments": post.get("comments", 0),
                        "comments_list": get_comments_by_post(str(post["_id"])),
                        "is_anonymous": post.get("is_anonymous", False),
                        "created_at": post.get("created_at", ""),
                    }
                    json_data["posts"].append(post_data)  # Thêm bài viết vào danh sách
                except Exception as e:
                    print(e)
                    
            return jsonify(json_data)




if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)
    