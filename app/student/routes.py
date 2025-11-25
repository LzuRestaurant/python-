# app/student/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from ..models import Question, ExamRecord, User
from .. import db
from ..utils import grade_choice, grade_fill, safe_exec
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
import datetime

student_bp = Blueprint('student', __name__, url_prefix='/student')

class CodeSubmitForm(FlaskForm):
    code = TextAreaField('代码', validators=[DataRequired(), Length(max=20000)])
    submit = SubmitField('提交')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

@student_bp.route('/dashboard')
@login_required
def dashboard():
    uid = session.get('user_id')
    records = ExamRecord.query.filter_by(user_id=uid).order_by(ExamRecord.created_at.desc()).limit(10).all()
    qcount = Question.query.count()
    return render_template('student/dashboard.html', records=records, qcount=qcount)

@student_bp.route('/practice', methods=['GET'])
@login_required
def practice():
    # 简单返回 5 道题作为练习
    qs = Question.query.limit(5).all()
    return render_template('student/practice.html', qs=qs)

@student_bp.route('/exam', methods=['GET', 'POST'])
@login_required
def exam():
    if request.method == 'GET':
        session['exam_start'] = datetime.datetime.utcnow().isoformat()
        # 随机选择5道题
        all_questions = Question.query.all()
        if len(all_questions) > 5:
            import random
            qs = random.sample(all_questions, 5)
        else:
            qs = all_questions
        return render_template('student/exam.html', qs=qs)
    
    # POST 提交试卷
    uid = session.get('user_id')
    # 获取提交的5道题
    all_questions = Question.query.all()
    if len(all_questions) > 5:
        import random
        qs = random.sample(all_questions, 5)
    else:
        qs = all_questions
    
    total = 0.0
    score = 0.0
    details = []
    for q in qs:
        total += 1.0
        if q.qtype == 'choice':
            ans = request.form.get(f'answer_{q.id}', '')
            sc = grade_choice(q.answer or '', ans)
            score += sc
            details.append({'qid': q.id, 'type': 'choice', 'score': sc, 'got': ans})
        elif q.qtype == 'fill':
            ans = request.form.get(f'answer_{q.id}', '')
            sc = grade_fill(q.answer or '', ans)
            score += sc
            details.append({'qid': q.id, 'type': 'fill', 'score': sc, 'got': ans})
        elif q.qtype == 'code':
            code = request.form.get(f'code_{q.id}', '')
            ok, msg = safe_exec(code or '', q.judge_template or '')
            sc = 1.0 if ok else 0.0
            score += sc
            details.append({'qid': q.id, 'type': 'code', 'score': sc, 'msg': msg})
        else:
            details.append({'qid': q.id, 'type': 'unknown', 'score': 0.0})
    try:
        start_iso = session.get('exam_start')
        start_dt = datetime.datetime.fromisoformat(start_iso) if start_iso else datetime.datetime.utcnow()
    except Exception:
        start_dt = datetime.datetime.utcnow()
    duration = (datetime.datetime.utcnow() - start_dt).seconds
    rec = ExamRecord(user_id=uid, score=score, total=total, duration_seconds=duration, details=str(details))
    db.session.add(rec)
    db.session.commit()
    flash(f'考试提交完成，得分 {score}/{total}', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/code_run/<int:qid>', methods=['GET', 'POST'])
@login_required
def code_run(qid):
    q = Question.query.get_or_404(qid)
    form = CodeSubmitForm()
    result = None
    if form.validate_on_submit():
        code = form.code.data
        ok, msg = safe_exec(code, q.judge_template or '')
        result = {'ok': ok, 'msg': msg}
    return render_template('student/code_run.html', q=q, form=form, result=result)
