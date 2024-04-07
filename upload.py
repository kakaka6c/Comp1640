from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CLIENT_ID = '1868ce014cffd54'

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['image']

        headers = {'Authorization': f'Client-ID {CLIENT_ID}'}
        files = {'image': (file.filename, file.read())}

        response = requests.post('https://api.imgur.com/3/image', headers=headers, files=files)
        data = response.json()

        if 'data' in data and 'link' in data['data']:
            return jsonify({'imageUrl': data['data']['link']}), 200
        else:
            return jsonify({'error': 'Upload failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# create route show img from imgur url
@app.route('/show_image', methods=['GET'])
def show_image():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'No url provided'}), 400

        response = requests.get(url)
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
    print("hihihihihihi")
