import os
import uuid

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

import trans

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

    # 这里对应了trans代码中的process_row函数的定义：text需要是一个元组，其中第四个元素是要翻译的文本
    transrow = ('', '', '', text)

    def report_progress(lang):
        socketio.emit('translation_progress', {'user_id': user_id, 'progress': lang})

    translations = trans.process_row(1, transrow, target_languages, report_progress,
                                     enable_gpt4=enable_gpt4)  # 使用您提供的翻译函数

    print(f" text {text} target_languages {target_languages} user_id {user_id} enable_gpt4 {enable_gpt4}")

    result = ""
    for i in range(len(target_languages)):
        result += "\n\n" + target_languages[i] + ": " + translations[i + 4]
        # result.append({"language": languages[i], "translation": translations[i+4]})

    # print (jsonify(result))

    return jsonify({"success": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
