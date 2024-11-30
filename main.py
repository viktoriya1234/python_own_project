from flask import Flask, request, session, redirect, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

SESSION_USER_ID = 'user_id'
SESSION_USER_NAME = 'user_name'

app = Flask(__name__)

# --- DB ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'school.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'B5CJYf33ktROup5IMMzXi9APYN4LIVETFmHHK2unpQc'

db = SQLAlchemy(app)


# === MODELS ======================================================================================
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Integer(), nullable=False, default=0)

    def __repr__(self):
        return f'<User: {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class News(db.Model):
    __tablename__ = 'News'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.Date(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)


class Subject(db.Model):
    __tablename__ = 'Subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    icon = db.Column(db.String(255), nullable=False)
    deleted = db.Column(db.Boolean, default=False)


# створюємо базу даних з таблицями
# with app.app_context():
#     db.create_all()


# === ROUTES ======================================================================================

@app.route('/')
def index():
    latest_news = News.query.order_by(News.created_on.desc()).limit(2).all()

    for item in latest_news:
        if len(item.text) > 200:
            item.text = item.text[:200] + ' ...'

    return render_template('index.html',latest_news=latest_news)


@app.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    news_items = News.query.paginate(page=page, per_page=6)

    for item in news_items.items:
        if len(item.text) > 200:
            item.text = item.text[:200] + ' ...'

    return render_template('news.html',
                           news_items=news_items,
                           user_id=session.get(SESSION_USER_ID))


@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news_item = News.query.filter_by(id=news_id).first()

    if news_item:
        news_item.text = news_item.text.replace("\n", "<br>")
        return render_template('news_detail.html',
                           news_item=news_item)

    abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# --- Admin -------------------------------------

@app.route('/logout')
def logout():
    session.pop(SESSION_USER_ID, None)
    session.pop(SESSION_USER_NAME, None)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            message = 'Введіть коректний Email!'
            return render_template('login.html', message=message)
        else:
            if not user.check_password(password):
                message = "Введіть коректний пароль!"
                return render_template('login.html', message=message)

            session[SESSION_USER_ID] = user.id
            session[SESSION_USER_NAME] = user.username
            return redirect('/')

    return render_template('login.html', message='')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if SESSION_USER_ID not in session:
        redirect('/login')

    if request.method == 'POST':
        id = int(request.form['id'])
        name = request.form['name']
        text = request.form['text']
        image = request.form['image']

        if id:
            row = News.query.filter_by(id=id).first()
            row.name = name
            row.text = text
            row.image = image
        else:
            row = News(name=name, text=text, image=image)

        db.session.add(row)
        db.session.commit()

        redirect('/')

    return render_template('add_news.html',
                           message='Додати новину',
                           id=0, name='', text='', image='')


@app.route('/edit_news/<int:news_id>')
def edit_news(news_id):
    if SESSION_USER_ID not in session:
        redirect('/login')

    news_item = News.query.filter_by(id=news_id).first()

    if news_item:
        return render_template('add_news.html',
                               message='Редагувати новину',
                               id=news_item.id,
                               name=news_item.name,
                               text=news_item.text,
                               image=news_item.image)

    abort(404)


if __name__ == '__main__':
    app.run(debug=True)
