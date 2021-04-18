from flask import Flask, render_template, request, redirect, make_response, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import traceback
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PERimport hashlibMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
db = SQLAlchemy(app)

ADMIN_PASSWORD = '6470c92fb4087b7cdb017342bf68c7cdd21a84317dd10aa5d8faa1e7b2800c54'
ADMIN_LOGIN = 'admin1984'

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.Text, nullable=True)
    count = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=True)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), index=True, unique=True, nullable=True)
    password = db.Column(db.String(150), nullable=True)
    name = db.Column(db.String(30), nullable=True)
    surname = db.Column(db.String(30), nullable=True)
    patronic = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    bonuses = db.Column(db.Float, nullable=True)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_of_user = db.Column(db.Integer,  db.ForeignKey("users.id"))
    address = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(30), index=True, unique=True, nullable=True)
    track_num = db.Column(db.String(30), nullable=True)
    comment_of_user = db.Column(db.String(200), nullable=True)
    comment_of_sender = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), nullable=True)
    created_date = db.Column(db.DateTime,
                default=datetime.datetime.now)
    item = db.Column(db.String(300), index=True, unique=True, nullable=True)

# вводит в бд данные о новом пользователе


def main():
    db.create_all()
    
    @app.route('/item')
    def item():
        return render_template('item.html')

    @app.route('/')
    @app.route('/main_page')
    def main_page():
        return render_template('main_page.html', title='Главная', css_file='main_page.css', class_main='container')

    @app.route('/authorization', methods=['POST', 'GET'])
    def authorization():
        if request.method == 'GET':
            return render_template('auth.html', title='Авторизация', css_file='signin.css', class_main='form-signin')
        elif request.method == 'POST':
            hashed_password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            try:
                # получаем данные пользователя, чтобы закинуть в куки
                user_data = Users.query.filter(Users.email == request.form['email'], 
                        Users.password == hashed_password).all()
                id = user_data[0].id
                name = user_data[0].name
                session['id'] = id
                session['name'] = name
                return redirect('/')

            except Exception as e:
                print(traceback.format_exc())
                return redirect('/registration')

    @app.route('/registration', methods=['POST', 'GET'])
    def registration():
        if request.method == 'GET':
            return render_template('reg.html', title='Регистрация', css_file='signup.css', class_main='form-signup')
        elif request.method == 'POST':
            hashed_password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            new_user = Users(name=request.form['name'],
                            surname=request.form['surname'],
                            patronic=request.form['patronic'],
                            phone=request.form['phone'],
                            email=request.form['email'],
                            password=hashed_password)

            try:
                db.session.add(new_user)
                db.session.commit()

                # получаем данные пользователя, чтобы закинуть в куки
                user_data = Users.query.filter(Users.email == request.form['email'], 
                                        Users.password == hashed_password).all()[0]
                id = user_data.id
                name = user_data.name
                session['id'] = id
                session['name'] = name
                return redirect('/')

            except Exception as e:
                print(traceback.format_exc())
                return "ОШИБКА"
    
    @app.route('/clear')
    def cookie():
        for key in list(session.keys()):
            del session[key]
        return redirect('/')

    @app.route('/catalog')
    def catalog():
        return render_template('catalog.html', title='Каталог', css_file='catalog.css', class_main='container')

    @app.route('/personal_info')
    def personal_info():
        info_user = Users.query.filter(Users.id == int(session['id'])).all()[0]
        info_orders = Orders.query.filter(Orders.id_of_user == int(session['id'])).all()
        return render_template('personal_info.html', title='Каталог', css_file='personal_info.css',
            class_main='container', user=info_user, orders=info_orders)

    @app.route('/admin85367', methods=['POST', 'GET'])
    def admin():
        if request.method == 'GET':
            return render_template('admin.html', css_file='signin.css', title='Админка туту')
        elif request.method == 'POST':
            password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            if password == ADMIN_PASSWORD and request.form['login'] == ADMIN_LOGIN:
                session['admin'] = '4891nimda'
                return redirect('/admin85367/panel')
            else:
                return redirect('/admin85367')

    @app.route('/admin85367/panel', methods=['POST', 'GET'])
    def panel():
        if request.method == 'GET':
            if 'admin' in session.keys() and session['admin'] == '4891nimda':
                return render_template('panel.html', title='Панель')
            else:
                return redirect('/admin85367')

    @app.route('/admin85367/panel/add_item', methods=['POST', 'GET'])
    def add_item():
        if request.method == 'GET':
            if 'admin' in session.keys() and session['admin'] == '4891nimda':
                return render_template('add_item.html', css_file='add_item.css', title='Добавить товар')
            else:
                return redirect('/admin85367')
        elif request.method == 'POST':
            try:
                photo = request.files['photo_url']
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                new_item = Items(name=request.form['name'],
                                 description=request.form['description'],
                                 price=int(request.form['price']),
                                 count=int(request.form['count']),
                                 photo_url=photo_path)
                db.session.add(new_item)
                db.session.commit()
                return 'asd'

            except Exception as e:
                print(traceback.format_exc())
                return "ОШИБКА"


    app.run()


if __name__ == '__main__':
    main()