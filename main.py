from flask import Flask, request, session, redirect, render_template

app = Flask(__name__)

# === MODELS ===========


# === ROUTES ===========

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)