# app.py
# Main Flask application for the DownMark service.

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, DownMark app!"

if __name__ == '__main__':
    app.run(debug=True)
