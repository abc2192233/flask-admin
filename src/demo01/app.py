import os
import os.path as op
import time
from multiprocessing import Process

import flask_login as login
from flask import Flask, redirect
from flask_admin import expose
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import form, fields, validators
from flask_admin import helpers, expose
import flask_login as login
from flask import url_for, redirect, request
import os.path as op
import flask_admin as admin
from flask_admin import form as form1
from flask_admin import helpers, expose
from flask_admin.contrib import sqla

import flask_admin as admin
from src.demo01.views.views import AlertStrategyView, VolFileView, LightStrategyView
from src.monitor.check import check_data

# Create Flask application
app = Flask(__name__, static_folder='files')

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

db = SQLAlchemy(app)


# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class AlertStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    speed_lower = db.Column(db.Unicode(64))
    speed_upper = db.Column(db.Unicode(64))

    vol_name = db.Column(db.Unicode(128))
    light_name = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


class VolFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


class LightStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    period = db.Column(db.Unicode(64))
    light_on = db.Column(db.Unicode(64))

    def __unicode__(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            app.config['process'] = Process(target=check_data)
            if not app.config['process'].is_alive():
                app.config['process'].start()
            return redirect(url_for('.index'))
        # link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        # self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        if app.config['process'].is_alive():
            app.config['process'].terminate()
        return redirect(url_for('.index'))


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Flask views
@app.route('/')
def index():
    return redirect('/admin')
    # return render_template('index.html')


# Initialize flask-login
init_login()

# Create admin
# admin = admin.Admin(app, 'Example: Auth', index_view=MyAdminIndexView(), base_template='my_master.html', template_mode='bootstrap4')
admin = admin.Admin(app, '配置平台', index_view=MyAdminIndexView(), base_template='my_master.html',
                    template_mode='bootstrap4')

# Add view
admin.add_view(AlertStrategyView(AlertStrategy, db.session))
admin.add_view(VolFileView(VolFile, db.session))
admin.add_view(LightStrategyView(LightStrategy, db.session))


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()
    # passwords are hashed, to use plaintext passwords instead:
    # test_user = User(login="test", password="test")
    test_user = User(login="test", password=generate_password_hash("test"))
    db.session.add(test_user)

    for i in [1, 2, 3]:
        alertstrategy = AlertStrategy()
        alertstrategy.name = "策略 " + str(i)
        alertstrategy.speed_lower = str(i * 10)
        alertstrategy.speed_upper = str(i * 10 + 10)
        alertstrategy.vol_name = "vol_example_" + str(i) + ".mp3"
        alertstrategy.light_name = "light_example_" + str(i) + ".txt"

        db.session.add(alertstrategy)

        volfile = VolFile()
        volfile.name = "vol_example_ " + str(i)
        volfile.path = "file/vol_example_2023_02_05" + str(i) + ".mp3"

        db.session.add(volfile)

        lightstrategy = LightStrategy()
        lightstrategy.name = "策略 " + str(i)
        lightstrategy.period = str(i * 20) + "s"
        lightstrategy.light_on = str(i * 10) + "s"

        db.session.add(lightstrategy)

    db.session.commit()
    return


if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        with app.app_context():
            build_sample_db()

    app.config['process'] = Process(target=check_data)
    app.run(processes=1)
