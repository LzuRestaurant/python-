# app/admin/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from ..models import Question, ExamRecord, User
from .. import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        uid = session.get('user_id')
        if not uid:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        u = User.query.get(uid)
        if not u or not u.is_admin:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return wrapper

class QuestionForm(FlaskForm):
    qtype = SelectField('题型', choices=[('choice','选择题'),('fill','填空题'),('code','编程题')], validators=[DataRequired()])
    title = TextAreaField('题目', validators=[DataRequired(), Length(max=2000)])
    option_a = StringField('选项 A')
    option_b = StringField('选项 B')
    option_c = StringField('选项 C')
    option_d = StringField('选项 D')
    answer = TextAreaField('参考答案')
    difficulty = IntegerField('难度', default=1)
    judge_template = TextAreaField('判题模板')
    submit = SubmitField('保存')

# 添加创建学生账号的表单
class CreateStudentForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=1, max=80)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('创建学生账号')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    qcount = Question.query.count()
    users = User.query.limit(20).all()
    return render_template('admin/dashboard.html', qcount=qcount, users=users)

# 添加创建学生账号的路由
@admin_bp.route('/create_student', methods=['GET', 'POST'])
@admin_required
def create_student():
    form = CreateStudentForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('用户名已存在', 'danger')
            return render_template('admin/create_student.html', form=form)
        
        # 创建新学生账号
        new_student = User(
            username=form.username.data,
            is_admin=False
        )
        new_student.set_password(form.password.data)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash(f'学生账号 "{form.username.data}" 创建成功', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_student.html', form=form)

# 其他路由保持不变...
@admin_bp.route('/questions')
@admin_required
def questions():
    qs = Question.query.order_by(Question.id.desc()).all()
    return render_template('admin/q_list.html', qs=qs)

@admin_bp.route('/question/add', methods=['GET', 'POST'])
@admin_required
def question_add():
    form = QuestionForm()
    if form.validate_on_submit():
        q = Question(
            qtype=form.qtype.data,
            title=form.title.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            answer=form.answer.data,
            difficulty=form.difficulty.data or 1,
            judge_template=form.judge_template.data
        )
        db.session.add(q)
        db.session.commit()
        flash('题目已添加', 'success')
        return redirect(url_for('admin.questions'))
    return render_template('admin/q_edit.html', form=form, mode='add')

@admin_bp.route('/question/edit/<int:qid>', methods=['GET', 'POST'])
@admin_required
def question_edit(qid):
    q = Question.query.get_or_404(qid)
    form = QuestionForm(obj=q)
    if form.validate_on_submit():
        q.qtype = form.qtype.data
        q.title = form.title.data
        q.option_a = form.option_a.data
        q.option_b = form.option_b.data
        q.option_c = form.option_c.data
        q.option_d = form.option_d.data
        q.answer = form.answer.data
        q.difficulty = form.difficulty.data or 1
        q.judge_template = form.judge_template.data
        db.session.commit()
        flash('题目已更新', 'success')
        return redirect(url_for('admin.questions'))
    return render_template('admin/q_edit.html', form=form, mode='edit', q=q)

@admin_bp.route('/question/delete/<int:qid>', methods=['POST'])
@admin_required
def question_delete(qid):
    q = Question.query.get_or_404(qid)
    db.session.delete(q)
    db.session.commit()
    flash('已删除题目', 'info')
    return redirect(url_for('admin.questions'))

@admin_bp.route('/import_csv', methods=['GET', 'POST'])
@admin_required
def import_csv():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash('未选择文件', 'warning')
            return redirect(url_for('admin.import_csv'))
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            q = Question(
                qtype=row.get('qtype','choice'),
                title=row.get('title',''),
                option_a=row.get('option_a'),
                option_b=row.get('option_b'),
                option_c=row.get('option_c'),
                option_d=row.get('option_d'),
                answer=row.get('answer'),
                difficulty=int(row.get('difficulty') or 1),
                judge_template=row.get('judge_template')
            )
            db.session.add(q)
            count += 1
        db.session.commit()
        flash(f'已导入 {count} 道题', 'success')
        return redirect(url_for('admin.questions'))
    return render_template('admin/import_csv.html')

@admin_bp.route('/records')
@admin_required
def records():
    recs = ExamRecord.query.order_by(ExamRecord.created_at.desc()).limit(200).all()
    return render_template('admin/records.html', recs=recs)