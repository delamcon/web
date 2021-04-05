from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


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
    password = db.Column(db.String(100), nullable=True)
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

# вводит в бд данные о новом пользователе


def main():
    global first_reg
    db.create_all()
    
    @app.route('/')
    @app.route('/main_page')
    def main_page():
        return render_template('main_page.html')

    @app.route('/authorization')
    def authorization():
        return render_template('auth.html')

    @app.route('/registration', methods=['POST', 'GET'])
    def registration():
        if request.method == 'GET':
            return render_template('reg.html')
        elif request.method == 'POST':
            new_user = Users(name=request.form['name'],
                            surname=request.form['surname'],
                            patronic=request.form['patronic'],
                            phone=request.form['phone'],
                            email=request.form['email'],
                            password=generate_password_hash(request.form['password']))
            
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                return "ОШИБКА"
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        email = db.Column(db.String(30), index=True, unique=True, nullable=True)
        password = db.Column(db.String(100), nullable=True)
        name = db.Column(db.String(30), nullable=True)
        surname = db.Column(db.String(30), nullable=True)
        patronic = db.Column(db.String(30), nullable=True)
        phone = db.Column(db.String(15), nullable=True)
        bonuses = db.Column(db.Float, nullable=True)


    app.run()


if __name__ == '__main__':
    main()