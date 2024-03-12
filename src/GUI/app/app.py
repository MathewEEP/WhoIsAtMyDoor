from flask import Flask
from flask import send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return "Index page."

@app.route('/upload/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.static_folder, filename)
