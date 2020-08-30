from flask import Flask, request, send_file, jsonify
import hashlib
import os

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World'


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Request should contain at least one file'}), 400
    file = request.files['file']
    file_content = file.read()
    hash_object = hashlib.md5(file_content)
    folder_name = hash_object.hexdigest()[:2]

    if not os.path.exists(f'store/{folder_name}'):
        os.mkdir(f"store/{folder_name}")

    file.seek(0, 0)  # ставим курсор в начало файла перед сохранением
    file.save(f"store/{folder_name}/{hash_object.hexdigest()}")
    file.close()

    return jsonify({'hash': hash_object.hexdigest()})


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()

    if not data or not data.get('hash'):
        return jsonify({'error': 'Hash is required'}), 400

    folder_name = data['hash'][:2]

    if not os.path.exists(f'store/{folder_name}/{data["hash"]}'):
        return jsonify({'error': 'No such file in directory'}), 404

    return send_file(f'store/{folder_name}/{data["hash"]}')


@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()

    if not data or not data.get('hash'):
        return jsonify({'error': 'Hash is required'}), 400

    folder_name = data['hash'][:2]

    if not os.path.exists(f'store/{folder_name}/{data["hash"]}'):
        return jsonify({'error': 'No such file in directory'}), 404

    os.remove(f'store/{folder_name}/{data["hash"]}')

    if not os.listdir(f'store/{folder_name}'):
        os.rmdir(f'store/{folder_name}')

    return jsonify({'status': 'OK'})


if __name__ == "__main__":
    app.run()
