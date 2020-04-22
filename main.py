from flask import Flask, render_template, redirect, make_response, request, session, jsonify, url_for
from data import db_session
import os
# from data.login_form import LoginForm
from data import User, product, comm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import abort, Api

# from flask_restful import abort, Api
# import data.resourse as res
# import data.user_res as ur

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


def hash(name):
    res = ''
    for sym in name:
        res += str(ord(sym))
    return res


class LoginForm(FlaskForm):
    # username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class ProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    submit = SubmitField('Применить')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User.User).get(user_id)


@app.route('/')
@app.route('/greeting')
def greeting():
    return render_template('Greeting.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User.User).filter(User.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/success")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message='Пароли не совпадают')
        session = db_session.create_session()
        if session.query(User.User).filter(User.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Пользователь уже зарегистрирован')
        user = User.User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/success')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/success', methods=['GET', 'POST'])
def success():
    session = db_session.create_session()
    if request.method == 'POST':
        needed = request.form['look']
        prod = session.query(product.Product).filter(product.Product.name == needed)
        if needed:
            return render_template('main.html', prod=prod, title='Товары по вашему запросу:')
        else:
            pass
    prod = session.query(product.Product).all()
    return render_template('main.html', prod=prod, title='Все товары:')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ProductForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        prod = product.Product()
        prod.name = form.title.data
        prod.about = form.content.data
        prod.hash = hash(prod.name)
        file = request.files['file']
        filename = file.filename
        prod.filename = filename
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        prod.url = url_for('static', filename=f'{filename}')
        current_user.products.append(prod)
        session.merge(current_user)
        session.commit()
        return redirect('/success')
    return render_template('add.html', form=form)


@app.route('/products', methods=['GET', 'POST'])
def products():
    session = db_session.create_session()
    prod = session.query(product.Product).filter(product.Product.user == current_user)
    return render_template('products.html', prod=prod)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    pass




@app.route('/item/<title>/<int:user>', methods=['GET', 'POST'])
@login_required
def item(title, user):
    session = db_session.create_session()
    if request.method == 'POST':
        prod = session.query(product.Product).filter(product.Product.hash == title).first()
        if user == 1 and not(request.form['com']):
            return redirect(f'/product_delete/{prod.name}')
        else:
            comment = comm.Comm()
            comment.text = request.form['com']
            comment.product_id = prod.id
            prod.comment.append(comment)
            comment.user_ = current_user.name
            session.merge(current_user)
            session.commit()
    prod = session.query(product.Product).filter(product.Product.hash == title).first()
    return render_template('item.html', prod=prod, user=prod.user, check=user)


@app.route('/product_delete/<name>')
@login_required
def product_delete(name):
    session = db_session.create_session()
    prod = session.query(product.Product).filter(product.Product.name == name,
                                                 product.Product.user == current_user).first()
    if prod:
        session.delete(prod)
        os.remove(f'static/{prod.filename}')
        session.commit()
    else:
        abort(404)
    return redirect('/success')


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    # for user in session.query(User.User).all():
    #     print(user)
    # print('------------------------------------------------')
    # for user in session.query(product.Product).all():
    #     print(user)
    app.run(port=8080, host='127.0.0.1')
