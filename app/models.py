# app/models.py
from . import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password_plain: str):
        self.password_hash = generate_password_hash(password_plain)

    def check_password(self, password_plain: str) -> bool:
        return check_password_hash(self.password_hash, password_plain)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    qtype = db.Column(db.String(20), nullable=False)  # 'choice','fill','code'
    title = db.Column(db.String(2000), nullable=False)
    option_a = db.Column(db.String(1000))
    option_b = db.Column(db.String(1000))
    option_c = db.Column(db.String(1000))
    option_d = db.Column(db.String(1000))
    answer = db.Column(db.Text)  # 存放参考答案或填空答案或代码样例
    difficulty = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    judge_template = db.Column(db.Text)  # 对于 code 题的判题模板（可选）

class ExamRecord(db.Model):
    __tablename__ = 'exam_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    score = db.Column(db.Float)
    total = db.Column(db.Float)
    duration_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    details = db.Column(db.Text)  # JSON 格式或字符串化结果

# 辅助：创建内置用户与示例题
def create_builtin_users():
    u = User.query.filter_by(username='x').first()
    if not u:
        u = User(username='x', is_admin=True)
        u.set_password('1')
        db.session.add(u)
        db.session.commit()
    # 如果题库为空则插入一些样例题
    if Question.query.count() == 0:
        insert_sample_questions()

def insert_sample_questions():
    """
    添加若干示例题（选择题/填空/编程）以便快速使用。
    写得比较冗长以增加行数，但逻辑简单可读。
    """
    samples = []

    samples.append(Question(
        qtype='choice',
        title='Python 中用于输出的函数是？',
        option_a='print()',
        option_b='input()',
        option_c='len()',
        option_d='open()',
        answer='A',
        difficulty=1
    ))

    samples.append(Question(
        qtype='choice',
        title='下列哪个关键字用于定义函数？',
        option_a='func',
        option_b='def',
        option_c='function',
        option_d='lambda',
        answer='B',
        difficulty=1
    ))

    samples.append(Question(
        qtype='fill',
        title='在 Python 中，表示整数类型的内置函数是 __ 。（填写函数名，不含括号）',
        answer='int',
        difficulty=2
    ))

    samples.append(Question(
        qtype='code',
        title='编写函数 fact(n) 返回 n 的阶乘。',
        answer='def fact(n):\\n    # 返回 n 的阶乘\\n    if n <= 1:\\n        return 1\\n    r = 1\\n    for i in range(2, n+1):\\n        r *= i\\n    return r',
        judge_template="# 以下为判题模板\\ninputs = [0,1,5,7]\\noutputs = [1,1,120,5040]\\nfor i,v in enumerate(inputs):\\n    got = fact(v)\\n    if got != outputs[i]:\\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')",
        difficulty=3
    ))

    # 逐一添加并提交
    for q in samples:
        db.session.add(q)
    db.session.commit()
