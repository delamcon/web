from flask import Flask, render_template, request, redirect, make_response, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
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

class Items(db.Model):  # таблица со всеми товарами
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=True)   # название товара
    description = db.Column(db.Text, nullable=True)  # описание
    photo_url = db.Column(db.Text, nullable=True)  # ссылка на фотографию
    count = db.Column(db.Integer, nullable=True)  # количество товара на складе
    price = db.Column(db.Float, nullable=True)   # стоимость 1 единицы товара


class Users(db.Model):  # таблица пользователей
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), index=True, unique=True, nullable=True)  # почта
    password = db.Column(db.String(150), nullable=True)   # пароль(хэшируется)
    name = db.Column(db.String(30), nullable=True)  # имя пользователя
    surname = db.Column(db.String(30), nullable=True)   # фамилия
    patronic = db.Column(db.String(30), nullable=True)  # отчество
    phone = db.Column(db.String(15), nullable=True)  # номер телефона
    bonuses = db.Column(db.Float, nullable=True)   # бонусный счет
    address = db.Column(db.String(200), nullable=True)  # адрес доставки(?)


class Orders(db.Model):  # таблица заказов
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # номер заказа
    id_of_user = db.Column(db.Integer,  db.ForeignKey("users.id"))  # id заказчика из таблицы пользователей
    address = db.Column(db.String(200), nullable=True)  # адрес доставки
    email = db.Column(db.String(30), index=True, nullable=True)  # почта пользователя
    track_num = db.Column(db.String(30), nullable=True)  # трек номер
    comment_of_user = db.Column(db.String(200), nullable=True)  # комментарий заказчика
    comment_of_sender = db.Column(db.String(200), nullable=True)  # комментарий отправителя
    status = db.Column(db.String(30), nullable=True)  # статус заказа
    created_date = db.Column(db.DateTime,
                default=datetime.datetime.now)   # дата создания
    item = db.Column(db.String(300), index=True, nullable=True)   # товары



def main():
    db.create_all()  # создание базы данных
    
    @app.route('/item/<id>', methods=['POST', 'GET'])  # страница отдельного товара
    def item(id):
        if request.method == 'GET':
            item = Items.query.filter(Items.id == id).all()[0]
            return render_template('item.html', item=item, css_file='cart.css')
        elif request.method == 'POST':
            try:
                if session['id']:  # получаем данные о нужном товаре
                    try:

                        if session['basket'] != '':
                            ses = session['basket'].split(';')
                            ses.append(f'{str(id)},{request.form["product_amount"]}')
                            session['basket'] = ';'.join(ses)
                        else:
                            session['basket'] = f'{str(id)},{request.form["product_amount"]}'
                        print(session)
                    except Exception:
                        session['basket'] = f'{str(id)},{request.form["product_amount"]}'
                return redirect('/catalog')
            except Exception:
                return redirect('/authorization')

    @app.route('/')
    @app.route('/main_page')  # главная страница магазина
    def main_page():
        try:
            if session['basket']:
                pass
        except Exception:
            session['basket'] = ""
        return render_template('main_page.html', title='Главная', css_file='main_page.css', class_main='container')

    @app.route('/authorization', methods=['POST', 'GET'])  # страница авторизации
    def authorization():
        if request.method == 'GET':
            return render_template('auth.html', title='Авторизация', css_file='signin.css', class_main='form-signin')
        elif request.method == 'POST':
            # получение хэшированного ввденого пароля
            hashed_password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            try:
                # получаем данные пользователя, чтобы закинуть в куки
                user_data = Users.query.filter(Users.email == request.form['email'], 
                        Users.password == hashed_password).all()
                id = user_data[0].id
                name = user_data[0].name
                session['id'] = id
                session['name'] = name
                return redirect('/')  # возвращаем на главную страницу после авторизации

            except Exception as e:  # если пользователь не зарегистрирован - редирект на страницу регистрации
                print(traceback.format_exc())
                return redirect('/registration')

    @app.route('/registration', methods=['POST', 'GET'])  # страница регистрации
    def registration():
        if request.method == 'GET':
            return render_template('reg.html', title='Регистрация', css_file='signup.css', class_main='form-signup')
        elif request.method == 'POST':
            # хэшируем введеный пароль
            hashed_password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            new_user = Users(name=request.form['name'],  # добавляем информацию о новом пользовтале в бд
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
                return redirect('/')  # после регистрации - возврат на главную страницу

            except Exception as e:
                print(traceback.format_exc())
                return "ОШИБКА"
    
    @app.route('/clear')  # очищение куки, возвращает на главную страницу
    def cookie():
        for key in list(session.keys()):
            del session[key]
        return redirect('/')

    @app.route('/catalog')  # страница каталога товаров
    def catalog():
        items = Items.query.all()  # получаем информацию о всех товарах из бд
        return render_template('catalog.html', title='Каталог', css_file='catalog.css', class_main='container',
                               items=items)

    @app.route('/personal_info')  # личный кабинет, если пользователь не зарегистрирован - вернет на главную страницу
    def personal_info():
        info_user = Users.query.filter(Users.id == int(session['id'])).all()[0]
        info_orders = Orders.query.filter(Orders.id_of_user == int(session['id'])).all()
        print(len(info_orders))
        return render_template('personal_info.html', title='Личный кабинет', css_file='personal_info.css',
            class_main='container', user=info_user, orders=info_orders, 
            Users=Users, Items=Items)

    @app.route('/admin85367', methods=['POST', 'GET'])  # админка
    def admin():
        if request.method == 'GET':
            return render_template('admin.html', css_file='signin.css', title='Админка туту')
        elif request.method == 'POST':
            password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
            if password == ADMIN_PASSWORD and request.form['login'] == ADMIN_LOGIN:  # сверяем пароль и логин
                # они записаны в сам код, если введены неверны - снова вернет на страницу авторизации админки
                session['admin'] = '4891nimda'
                return redirect('/admin85367/panel')  # если данные введены верно - возврат на панель администратора
            else:
                return redirect('/admin85367')  # если нет - снова страница авторизации админки

    @app.route('/admin85367/panel', methods=['POST', 'GET'])  # админская панель - главная страница
    def panel():
        if request.method == 'GET':
            if 'admin' in session.keys() and session['admin'] == '4891nimda':  # проверка авторизации(на всякий)
                return render_template('panel.html', title='Панель', 
                                        css_file='panel.css', orders=Orders.query.all(), Items=Items)
            else:
                return redirect('/admin85367')
        elif request.method == "POST":
            order = Orders.query.filter(Orders.id == request.form["id"]).first()
            order.track_num = request.form['track_num']
            db.session.commit()
            return redirect('/admin85367/panel')

    @app.route('/admin85367/panel/add_item', methods=['POST', 'GET'])  # добавление нового товара в каталог
    def add_item():
        if request.method == 'GET':
            if 'admin' in session.keys() and session['admin'] == '4891nimda':  # проверка авторизации
                return render_template('add_item.html', css_file='add_item.css', title='Добавить товар')
            else:
                return redirect('/admin85367')
        elif request.method == 'POST':  # добавление товара в бд при отправки формы
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
                return redirect('/admin85367/panel')  # после отправки формы - редирект на панель основную

            except Exception as e:
                print(traceback.format_exc())
                return "ОШИБКА"

    @app.route('/cart', methods=['POST', 'GET'])  # корзина пользователя
    def cart():
        if request.method == 'GET':
            if session['id']:
                info_user = Users.query.filter(Users.id == int(session['id'])).all()[0]
                # order = Orders.query.filter(Orders.id_of_user == int(session['id']) and 
                #                             Orders.item == session['basket']).all()[0]
                return render_template('cart.html', title='Корзина', css_file='cart.css',
                                    class_main='container', Items=Items, Users=Users)
            else:
                return redirect('/authorization')
        elif request.method == "POST":
            print(request.form)
            if 'submit' in request.form:
                user_data = Users.query.filter(Users.id == session['id']).all()[0]
                new_order = Orders(item=session['basket'],
                                id_of_user=session['id'],
                                address=request.form['address'],
                                email=user_data.email,
                                created_date=datetime.datetime.now(),
                                comment_of_user=request.form['comment'])
                try:
                    db.session.add(new_order)
                    db.session.commit()
                    session['basket'] = ''
                    return redirect('/')
                except Exception as e:
                    print(traceback.format_exc())
                    return "ОШИБКА"
            elif 'id' in request.form:
                ses = session['basket'].split(';')
                print(request.form['id'])
                del ses[ses.index(request.form['id'])]
                session['basket'] = ';'.join(ses)
                return redirect('/cart')

    @app.route('/admin85367/panel/delete_item', methods=['POST', 'GET'])
    def delete_item():
        if request.method == 'GET':
            if 'admin' in session.keys() and session['admin'] == '4891nimda':
                info_items = Items.query.all()
                return render_template('delete_item.html', css_file='delete_item.css', title='Удаление товаров',
                                       info_items=info_items)
            else:
                return redirect('/admin85367')
        elif request.method == 'POST':
            print(request.form['id'])
            db.session.delete(Items.query.filter(Items.id == int(request.form['id'])).all()[0])
            db.session.commit()
            return redirect('/admin85367/panel/delete_item')

    @app.route('/bonus_system')  # страничка информации о бонусной системе (которая не работает ехеххехе)
    def bonus_system():
        return render_template('bonuses.html', css_file='bonuses.css', title='Бонусная система')

    @app.route('/info_changing', methods=['POST', 'GET'])
    def info_changing():
        if request.method == 'GET':
            user_data = Users.query.filter(Users.id == session['id']).all()[0]
            return render_template('info_changing.html', css_file='info_changing.css', title='Изменение данных',
                                   user=user_data)
        elif request.method == 'POST':
            user = (update(Users).
                    where(Users.id == session['id']).
                    values(name=request.form['name'],
                           surname=request.form['surname'],
                           patronic=request.form['patronic'],
                           phone=request.form['phone'],
                           email=request.form['email'],
                           address=request.form['address']))
            try:
                db.session.add(user)
                db.session.commit()
                return redirect('/personal_info')
            except Exception as e:
                    print(traceback.format_exc())
                    return "ОШИБКА"


    app.run()


if __name__ == '__main__':
    main()