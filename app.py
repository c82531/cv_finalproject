import urllib

from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename
from deepface import DeepFace

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DB_PATH = 'cvdb'  # Directory containing potential matches
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/find')
def find():
    return render_template('find.html')
@app.route('/verify')
def verify():
    return render_template('verify.html')
@app.route('/analyze')
def analyze():
    return render_template('analyze.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/cvdb/<path:encoded_filename>')
def cvdb(encoded_filename):
    filename = urllib.parse.unquote(encoded_filename)
    return send_from_directory(DB_PATH, filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    mode = request.form.get('mode')
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    uploaded_image_url = f'/uploads/{filename}'

    if mode == 'find':
        try:
            dfs = DeepFace.find(img_path=file_path, db_path=DB_PATH, enforce_detection=False)
            similar_images = []
            for df in dfs:
                similar_images.extend(df['identity'].tolist())
            top_similar_images = similar_images[:3]
            similar_images_urls = [f"/cvdb/{img[len(DB_PATH) + 1:]}" for img in top_similar_images]
            return jsonify({'uploaded_image': uploaded_image_url, 'similar_images': similar_images_urls})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif mode == 'verify':
        if 'second_image' not in request.files:
            return jsonify({'error': 'Second image not provided for verification'}), 400

        second_file = request.files['second_image']
        if second_file.filename == '':
            return jsonify({'error': 'No selected second file'}), 400

        second_filename = secure_filename(second_file.filename)
        second_file_path = os.path.join(app.config['UPLOAD_FOLDER'], second_filename)
        second_file.save(second_file_path)

        second_uploaded_image_url = f'/uploads/{second_filename}'

        try:
            result = DeepFace.verify(img1_path=file_path, img2_path=second_file_path, enforce_detection=False)
            verification_result = result['verified']
            return jsonify({
                'uploaded_image': uploaded_image_url,
                'second_uploaded_image': second_uploaded_image_url,
                'verification_result': verification_result
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif mode == 'analyze':
        print(file_path)
        try:
            analysis_result = DeepFace.analyze(img_path=file_path, actions=["age", "gender", "emotion", "race"], enforce_detection=False)
            # Extract only the desired fields
            simplified_result = {
                'age': analysis_result[0]['age'],
                'gender': analysis_result[0]['dominant_gender'],
                'emotion': analysis_result[0]['dominant_emotion'],
                'race': analysis_result[0]['dominant_race']
            }
            return jsonify({'uploaded_image': uploaded_image_url, 'analysis_result': simplified_result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid mode'}), 400


if __name__ == '__main__':
    app.run(debug=True)
