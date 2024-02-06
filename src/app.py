from flask import Flask, render_template
import os
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()
html_title = os.getenv("html_title")
html_changelog = os.getenv("html_changelog")

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'output/uploads'
app.config['DOWNLOAD_FOLDER'] = 'output/downloads'
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/translate')
def index():
    return render_template('index.html', html_title=html_title, html_changelog=html_changelog)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
