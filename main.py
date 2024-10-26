from flask import Flask, request, session, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://" + os.path.join(basedir, 'school.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# === MODELS ===========
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    role = db.Column(db.Integer(), default=False, nullable=False)

    def __repr__(self):
        return  f'<User {self.username}>'

# === ROUTES ===========

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/courses')
def courses():
    return render_template('courses.html')


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/services')
def services():
    return render_template('services.html')


if __name__ == '__main__':
    app.run(debug=True)