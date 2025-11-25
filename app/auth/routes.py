# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from ..models import User
from .. import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

auth_bp = Blueprint('auth', __name__, url_prefix='')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=1, max=80)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('登录')

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data.strip()).first()
        if u and u.check_password(form.password.data.strip()):
            session['user_id'] = u.id
            flash('登录成功', 'success')
            # 根据是否管理员跳转
            if u.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.index'))
