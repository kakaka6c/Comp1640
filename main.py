from flask import Flask, request, jsonify
from DatabaseHelper import *

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://manhdc01:12345@cluster0.z2zlgel.mongodb.net/'
db_helper = DatabaseHelper(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = AdminModel(db_helper).get_users()

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


if __name__ == '__main__':
    app.run(debug=True,port=5000,host='0.0.0.0')