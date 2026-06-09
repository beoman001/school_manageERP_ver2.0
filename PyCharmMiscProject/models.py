from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    password = db.Column(db.String(200))

    role = db.Column(db.String(20))

    roll_no = db.Column(db.String(20))

    class_name = db.Column(db.String(20))