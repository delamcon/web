from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    photo_url = db.Column(db.Text)
    count = db.Column(db.Integer)
    price = db.Column(db.Float)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30))
    email = db.Column(db.String(30))
    password = db.Column(db.String(30))
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    patronic = db.Column(db.String(30))
    phone = db.Column(db.Integer(15))
    bonuses = db.Column(db.Float)


def main():
    db.create_all()
    app.run()


if __name__ == '__main__':
    main()