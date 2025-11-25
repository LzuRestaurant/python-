# app/admin/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
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
        
        # 延迟导入，避免循环导入
        from ..models import User
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

class CreateStudentForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=1, max=80)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('创建学生账号')

# 添加日志查看表单
class LogFilterForm(FlaskForm):
    level = SelectField('日志级别', choices=[
        ('', '全部'), ('INFO', '信息'), ('WARNING', '警告'), ('ERROR', '错误'), ('DEBUG', '调试')
    ])
    module = StringField('模块名称')
    user_id = IntegerField('用户ID')
    count = IntegerField('显示数量', default=100)
    submit = SubmitField('筛选')

# 添加备份管理表单
class BackupForm(FlaskForm):
    description = StringField('备份描述')
    submit = SubmitField('创建备份')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # 延迟导入，避免循环导入
    from ..models import Question, User
    qcount = Question.query.count()
    users = User.query.limit(20).all()
    return render_template('admin/dashboard.html', qcount=qcount, users=users)

@admin_bp.route('/questions')
@admin_required
def questions():
    from ..models import Question
    qs = Question.query.order_by(Question.id.desc()).all()
    return render_template('admin/q_list.html', qs=qs)

@admin_bp.route('/question/add', methods=['GET', 'POST'])
@admin_required
def question_add():
    from ..models import Question
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
    from ..models import Question
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
    from ..models import Question
    q = Question.query.get_or_404(qid)
    db.session.delete(q)
    db.session.commit()
    flash('已删除题目', 'info')
    return redirect(url_for('admin.questions'))

@admin_bp.route('/import_csv', methods=['GET', 'POST'])
@admin_required
def import_csv():
    from ..models import Question
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
    from ..models import ExamRecord
    recs = ExamRecord.query.order_by(ExamRecord.created_at.desc()).limit(200).all()
    return render_template('admin/records.html', recs=recs)

@admin_bp.route('/create_student', methods=['GET', 'POST'])
@admin_required
def create_student():
    from ..models import User
    form = CreateStudentForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('用户名已存在，请选择其他用户名', 'danger')
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

# 添加日志查看路由
@admin_bp.route('/logs')
@admin_required
def view_logs():
    from ..services.logging_service import logging_service
    form = LogFilterForm()
    
    # 获取筛选参数
    level = request.args.get('level', '')
    module = request.args.get('module', '')
    user_id = request.args.get('user_id', type=int)
    count = request.args.get('count', 100, type=int)
    
    # 获取日志
    logs = logging_service.get_recent_logs(count=count)
    
    # 应用筛选
    if level:
        logs = [log for log in logs if log.level == level]
    if module:
        logs = [log for log in logs if module.lower() in log.module.lower()]
    if user_id:
        logs = [log for log in logs if log.user_id == user_id]
    
    # 获取统计信息
    stats = logging_service.get_statistics()
    
    return render_template('admin/logs.html', 
                         logs=logs, 
                         form=form, 
                         stats=stats,
                         current_level=level,
                         current_module=module,
                         current_user_id=user_id,
                         current_count=count)

# 添加备份管理路由
@admin_bp.route('/backups', methods=['GET', 'POST'])
@admin_required
def manage_backups():
    from ..services.backup_service import backup_service
    from ..services.logging_service import logging_service
    
    form = BackupForm()
    
    if form.validate_on_submit():
        # 创建新备份
        description = form.description.data or ""
        backup_info = backup_service.create_backup(description)
        
        if backup_info['success']:
            flash(f'备份创建成功: {backup_info["filename"]}', 'success')
            # 记录日志
            uid = session.get('user_id')
            logging_service.info("创建数据库备份", user_id=uid, module="backup", 
                               details={'filename': backup_info['filename']})
        else:
            flash(f'备份创建失败: {backup_info.get("error", "未知错误")}', 'danger')
        
        return redirect(url_for('admin.manage_backups'))
    
    # 获取备份列表和统计信息
    backups = backup_service.list_backups()
    stats = backup_service.get_backup_stats()
    
    return render_template('admin/backups.html', 
                         backups=backups, 
                         form=form, 
                         stats=stats,
                         backup_service=backup_service)

# 添加备份恢复路由
@admin_bp.route('/backup/restore/<filename>', methods=['POST'])
@admin_required
def restore_backup(filename):
    from ..services.backup_service import backup_service
    from ..services.logging_service import logging_service
    
    result = backup_service.restore_backup(filename)
    
    if result['success']:
        flash(f'数据库恢复成功: {result["message"]}', 'success')
        # 记录日志
        uid = session.get('user_id')
        logging_service.info("恢复数据库备份", user_id=uid, module="backup", 
                           details={'filename': filename, 'previous': result.get('previous_backup')})
    else:
        flash(f'数据库恢复失败: {result["message"]}', 'danger')
    
    return redirect(url_for('admin.manage_backups'))

# 添加备份删除路由
@admin_bp.route('/backup/delete/<filename>', methods=['POST'])
@admin_required
def delete_backup(filename):
    from ..services.backup_service import backup_service
    from ..services.logging_service import logging_service
    
    result = backup_service.delete_backup(filename)
    
    if result['success']:
        flash(f'备份删除成功: {result["message"]}', 'info')
        # 记录日志
        uid = session.get('user_id')
        logging_service.info("删除数据库备份", user_id=uid, module="backup", 
                           details={'filename': filename})
    else:
        flash(f'备份删除失败: {result["message"]}', 'danger')
    
    return redirect(url_for('admin.manage_backups'))