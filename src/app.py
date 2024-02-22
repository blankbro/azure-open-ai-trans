import os
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

import log_util
import trans

logger = log_util.get_logger(__name__)
load_dotenv()
HTML_TITLE = os.getenv("HTML_TITLE")
HTML_CHANGELOG = os.getenv("HTML_CHANGELOG")
SERVER_PORT = os.getenv("SERVER_PORT")
UPLOAD_FOLDER = 'output/uploads'
DOWNLOAD_FOLDER = 'output/downloads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/translate')
def index():
    return render_template('index.html', HTML_TITLE=HTML_TITLE, HTML_CHANGELOG=HTML_CHANGELOG)


@socketio.on('translate_text')
@app.route('/translate/text', methods=['POST'])
def translate_text():
    text = request.form['text']
    target_languages = jsonify(eval(request.form.getlist('languages')[0])).json
    user_id = request.form['user_id']
    enable_gpt4 = request.form['enable_gpt4']

    def report_progress(lang):
        socketio.emit('translation_progress', {'user_id': user_id, 'progress': lang})

    request_id = str(uuid.uuid4())
    logger.info(
        f"{request_id} /translate/text: user_id {user_id}, enable_gpt4 {enable_gpt4}, target_languages {target_languages}, text {text}")

    translations = trans.process_row(
        row_number=1,
        # 元组中第四个元素是要翻译的文本
        row_data=('', '', '', text),
        target_languages=target_languages,
        progress_callback=report_progress,
        enable_gpt4=enable_gpt4
    )

    logger.info(f"{request_id} translate_text end")

    result = ""
    for i in range(len(target_languages)):
        result += "\n\n" + target_languages[i] + ": " + translations[i + 4]

    return jsonify({"success": result})


@app.route('/translate/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file:
        return jsonify({"error": "File upload failed"}), 400

    # 保存文件
    filename = secure_filename(file.filename)
    request_id = uuid.uuid4()
    file_save_name = str(request_id) + '_' + filename
    upload_filepath = os.path.join(UPLOAD_FOLDER, file_save_name)
    download_filepath = os.path.join(DOWNLOAD_FOLDER, file_save_name)
    file.save(upload_filepath)

    # 获取请求参数
    target_languages = jsonify(eval(request.form.getlist('languages')[0])).json
    user_id = request.form['user_id']
    enable_gpt4 = request.form['enable_gpt4']

    logger.info(
        f"{request_id} /translate/upload: user_id {user_id}, enable_gpt4 {enable_gpt4}, target_languages {target_languages}, filename {filename}")

    def report_progress(lang):
        socketio.emit('file_progress', {'user_id': user_id, 'progress': lang})

    session['upload_filepath'] = upload_filepath
    session['download_filepath'] = download_filepath
    session['download_filename'] = file_save_name

    # 开始翻译
    trans.process_excel(
        upload_filepath,
        download_filepath,
        target_languages=target_languages,
        progress_callback=report_progress,
        enable_gpt4=enable_gpt4
    )

    return jsonify({"success": "Translation Success!", "filename": filename}), 200


@app.route('/translate/download/<filename>', methods=['GET'])
def download_file(filename):
    if 'download_filepath' not in session or 'download_filename' not in session:
        return jsonify({"error": "No file selected"}), 400

    download_filepath = session['download_filepath']
    download_filename = session['download_filename']
    return send_file(download_filepath, download_name=download_filename, as_attachment=True)


if __name__ == '__main__':
    logger.info("App start")
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
