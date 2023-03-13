from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Flask and Flask-SQLAlchemy initialization here

app = Flask(__name__)
db = SQLAlchemy(app)
print(type(db.session))
