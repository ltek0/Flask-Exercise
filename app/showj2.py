from flask import Flask, render_template
from flask_livereload import LiveReload

app = Flask(__name__)
livereload = LiveReload(app)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)