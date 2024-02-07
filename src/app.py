import os
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

import log_util
import trans

logger = log_util.get_logger(__name__)
load_dotenv()
HTML_TITLE = os.getenv("HTML_TITLE")
HTML_CHANGELOG = os.getenv("HTML_CHANGELOG")

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'output/uploads'
app.config['DOWNLOAD_FOLDER'] = 'output/downloads'
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
        f"{request_id} translate_text: user_id {user_id}, enable_gpt4 {enable_gpt4}, target_languages {target_languages}, text {text}")

    translations = trans.process_row(
        1,
        # 元组中第四个元素是要翻译的文本
        ('', '', '', text),
        target_languages,
        report_progress,
        enable_gpt4=enable_gpt4
    )

    logger.info(f"{request_id} translate_text end")

    result = ""
    for i in range(len(target_languages)):
        result += "\n\n" + target_languages[i] + ": " + translations[i + 4]

    return jsonify({"success": result})


if __name__ == '__main__':
    logger.info("App start")
    app.run(host='0.0.0.0', port=5001, debug=True)
