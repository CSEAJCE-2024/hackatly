from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import *#form creation
from wtforms.validators import *
from flask_bcrypt import Bcrypt
from datetime import datetime, date
import requests, json

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


@app.route('/save', methods = ['POST'])
def save():
    request_json = request.get_json()
    print(request_json)
    lat = request_json['lat']
    long = request_json['long']
    return jsonify({
        "lat": lat,
        "long": long
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)