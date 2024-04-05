from datetime import datetime
from flask import Flask, request, jsonify
from DatabaseHelper import AdminModel, UserModel, PostModel, CommentModel, LikeModel, DatabaseHelper
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://manhdc01:12345@cluster0.z2zlgel.mongodb.net/'
db_helper = DatabaseHelper(app)

# create route for login and return user info

def token_to_uid(authorization_header):
    user_id = None
    token = None
    if authorization_header and authorization_header.startswith('Bearer '):
        # Tách chuỗi token từ header 'Authorization'
        token = authorization_header.split(' ')[1]
        user_id,role = UserModel(db_helper).get_role_by_access_token(token)
        return user_id,role
    else:
        return user_id,role



@app.route('/users', methods=['GET'])
def get_users():
    # authorization_header = request.headers.get('Authorization')
    # user_id,role = token_to_uid(authorization_header)

    users = AdminModel(db_helper).get_users()
    print(users)
    json_data = [ { "_id": str(user['_id']), "name": user['name'], "email": user['email'],"role": user['role']} for user in users]
    return jsonify(json_data)

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    # print(user_id)
    user = UserModel(db_helper).get_user(user_id)
    # print(user)
    if user:
        # Trả về thông tin cần thiết trong định dạng JSON
        user_data = {
            'name': user['name'],
            'phone': user['phone'],
            'email': user['email'],
            'dateOfBirth': str(user['dateOfBirth']),
            'gender': user['gender'],
            'faculty': user['faculty'],
            'role': user['role']
        }
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/add_user', methods=['POST'])
def add_user():
    user = request.json
    result = AdminModel(db_helper).add_user(user)
    if result:
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"message": "Failed to add user"}), 400

@app.route('/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = request.json
    result = AdminModel(db_helper).update_user(str(user_id), user)
    if result:
        return jsonify({"message": "User updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update user"}), 400

@app.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = AdminModel(db_helper).delete_user(str(user_id))
    if result:
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete user"}), 400

# create route get all post 
@app.route('/posts', methods=['POST'])
def get_posts():
    faculty_id = request.json.get('faculty_id')
    posts = PostModel(db_helper).get_posts_by_faculty(faculty_id)
    
    json_data = []
    for post in posts:
        user_id = post['user']  # Lấy user_id từ bài viết
        
        # Truy vấn thông tin người dùng từ user_id
        user_info = UserModel(db_helper).get_user(user_id)
        
        # Tạo một JSON object mới chứa thông tin của bài viết và người dùng
        post_data = {
            "_id": str(post['_id']),
            "user": {
                "_id": str(user_info['_id']),
                "name": user_info.get('name', ''),
                "email": user_info.get('email', '')
            },
            "caption": post['caption'],
            "url": post['url'],
            "likes": post['likes'],
            "comments": post['comments'],
            "is_anonymous": post['is_anonymous'],
            "created_at": post['created_at']
        }
        json_data.append(post_data)

    return jsonify(json_data)

# create route add post
@app.route('/add_post', methods=['POST'])
def add_post():
    post = request.json
    
    # Kiểm tra các trường bắt buộc
    if not all(key in post for key in ['caption', 'user', 'faculty']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Chuyển đổi chuỗi ObjectId sang ObjectId
    try:
        post['user'] = ObjectId(post['user'])
        post['faculty'] = ObjectId(post['faculty'])
    except Exception as e:
        return jsonify({'message': 'Invalid ObjectId format'}), 400
    
    # Thêm trường created_at nếu không được cung cấp
    if 'created_at' not in post:
        post['created_at'] = datetime.now()
    
    # Thêm post vào collection
    result = PostModel(db_helper).add_post(post)
    
    # Kiểm tra kết quả và trả về thông báo tương ứng
    if result.inserted_id:
        return jsonify({'message': 'Post added successfully', 'post_id': str(result.inserted_id)}), 200
    else:
        return jsonify({'message': 'Failed to add post'}), 500

# create route get post by id
@app.route('/comments/<post_id>', methods=['GET'])
def get_comments(post_id):
    comments = CommentModel(db_helper).get_comments_by_post(post_id)
    json_data = []
    for comment in comments:
        user_id = comment['user']
        user_info = UserModel(db_helper).get_user(user_id)
        comment_data = {
            "post_id": str(comment['_id']),
            "user": {
                "user_id": str(user_info['_id']),
                "name": user_info.get('name', ''),
                "email": user_info.get('email', '')
            },
            "comment": comment['comment'],
            "created_at": comment['created_at']
        }
        json_data.append(comment_data)
    return jsonify(json_data)

# create route add comment
@app.route('/add_comment', methods=['POST'])
def add_comment():
    # Lấy dữ liệu từ request
    comment = request.json
    
    # Kiểm tra các trường bắt buộc
    if not all(key in comment for key in ['comment', 'post', 'user']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Chuyển đổi chuỗi ObjectId sang ObjectId
    try:
        comment['post'] = ObjectId(comment['post'])
        comment['user'] = ObjectId(comment['user'])
    except Exception as e:
        return jsonify({'message': 'Invalid ObjectId format'}), 400
    
    # Thêm trường created_at nếu không được cung cấp
    if 'created_at' not in comment:
        comment['created_at'] = datetime.now()
    
    # Thêm comment vào collection
    result = CommentModel(db_helper).add_comment(comment)
    
    # Kiểm tra kết quả và trả về thông báo tương ứng
    if result.inserted_id:
        # đổi số lượng comment +=1
        post = PostModel(db_helper).get_post(comment['post'])
        PostModel(db_helper).update_post(comment['post'], {'comments': post['comments'] + 1})
        return jsonify({'message': 'Comment added successfully', 'comment_id': str(result.inserted_id)}), 200
    else:
        return jsonify({'message': 'Failed to add comment'}), 500

# create route delete comment
@app.route('/delete_comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment=CommentModel(db_helper).get_comment(comment_id)
    post = PostModel(db_helper).get(comment['post'])
    result = CommentModel(db_helper).delete_comment(comment_id)
    if result:
        PostModel(db_helper).update_post(comment['post'], {'comments': post['comments'] - 1})
        return jsonify({"message": "Comment deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete comment"}), 500
    
# create route count comments by post
@app.route('/count_comments/<post_id>', methods=['GET'])
def count_comments(post_id):
    count = CommentModel(db_helper).count_comment(post_id)
    return jsonify({'count': count})

# create route count comments by event
@app.route('/count_comments/event/<event_id>', methods=['GET'])
def count_comments_for_event(event_id):
    count = CommentModel(db_helper).count_comments_for_event(event_id)
    return jsonify({'count': count})

# create route count comments by faculty
@app.route('/count_comments/faculty/<faculty_id>', methods=['GET'])
def count_comments_for_faculty(faculty_id):
    count = CommentModel(db_helper).count_comments_for_faculty(faculty_id)
    return jsonify({'count': count})

# create route count comments by user
@app.route('/count_comments/user/<user_id>', methods=['GET'])
def count_comments_for_user(user_id):
    count = CommentModel(db_helper).count_comments_for_user(user_id)
    return jsonify({'count': count})

@app.route('/add_like', methods=['POST'])
def add_like():
    like = request.json
    result = LikeModel(db_helper).add_like(like)
    # count likes now
    count = LikeModel(db_helper).count_like(like['post'])
    # update likes count
    PostModel(db_helper).update_post(like['post'], {'likes': count})
    # return message and current like count
    if result:
        return jsonify({"message": "Like added successfully", "likes": count}), 200
    else:
        return jsonify({"message": "Failed to add like"}), 500

@app.route('/remove_like', methods=['POST'])
def remove_like():
    like = request.json
    result = LikeModel(db_helper).delete_like(like)
    # count likes now
    count = LikeModel(db_helper).count_likes_for_post(like['post'])
    # update likes count
    PostModel(db_helper).update_post(like['post'], {'likes': count})
    # return message and current like count
    if result:
        return jsonify({"message": "Like removed successfully", "likes": count}), 200
    else:
        return jsonify({"message": "Failed to remove like"}), 500

@app.route('/count_likes/<post_id>', methods=['GET'])
def count_likes(post_id):
    count = LikeModel(db_helper).count_likes_for_post(post_id)
    return jsonify({'count': count})

@app.route('/count_likes/event/<event_id>', methods=['GET'])
def count_likes_for_event(event_id):
    count = LikeModel(db_helper).count_likes_for_event(event_id)
    return jsonify({'count': count})

@app.route('/count_likes/faculty/<faculty_id>', methods=['GET'])
def count_likes_for_faculty(faculty_id):
    count = LikeModel(db_helper).count_likes_for_faculty(faculty_id)
    return jsonify({'count': count})

@app.route('/count_likes/user/<user_id>', methods=['GET'])
def count_likes_for_user(user_id):
    count = LikeModel(db_helper).count_likes_for_user(user_id)
    return jsonify({'count': count})


if __name__ == '__main__':
    app.run(debug=True,port=5000,host='0.0.0.0')