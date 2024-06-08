# flask_app.py
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Flask and Streamlit Integration</title>
          </head>
          <body>
            <h1>Flask and Streamlit Integration</h1>
            <iframe src="http://localhost:8501" width="700" height="800"></iframe>
          </body>
        </html>
    ''')

if __name__ == "__main__":
    app.run(port=5000)
