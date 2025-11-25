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
    添加100示例题（选择题/填空/编程）以便快速使用。
    逻辑简单可读。
    """
    samples = []

    # 基础选择题模板
    choice_templates = [
        ("Python 中用于输出的函数是？", ["print()", "input()", "len()", "open()"], "A"),
        ("下列哪个关键字用于定义函数？", ["func", "def", "function", "lambda"], "B"),
        ("用于获取列表长度的函数是？", ["size()", "length()", "len()", "count()"], "C"),
        ("下列哪个不是Python的数据类型？", ["int", "str", "char", "float"], "C"),
        ("Python中表示真值的布尔值是什么？", ["True", "true", "TRUE", "1"], "A"),
        ("下列哪个用于导入模块？", ["include", "import", "using", "require"], "B"),
        ("Python中注释使用的符号是？", ["//", "#", "/*", "--"], "B"),
        ("下列哪个是可变数据类型？", ["tuple", "str", "list", "int"], "C"),
        ("用于读取用户输入的函数是？", ["read()", "input()", "get()", "scan()"], "B"),
        ("下列哪个用于创建空列表？", ["[]", "{}", "()", "None"], "A"),
    ]
    
    # 填空题模板
    fill_templates = [
        ("在 Python 中，表示整数类型的内置函数是 __。", "int"),
        ("用于将字符串转换为小写的方法是 __。", "lower"),
        ("列表追加元素的方法是 __。", "append"),
        ("获得列表长度使用 __。", "len"),
        ("Python中用于条件判断的关键字是 __。", "if"),
        ("用于循环遍历序列的关键字是 __。", "for"),
        ("定义类的关键字是 __。", "class"),
        ("异常处理中捕获所有异常的关键字是 __。", "except"),
        ("用于打开文件的内置函数是 __。", "open"),
        ("从函数中返回值的语句是 __。", "return"),
    ]
    
    # 编程题模板
    code_templates = [
        ("编写函数 fact(n) 返回 n 的阶乘。", 
         "def fact(n):\n    if n <= 1:\n        return 1\n    r = 1\n    for i in range(2, n+1):\n        r *= i\n    return r",
         "inputs = [0,1,5,7]\noutputs = [1,1,120,5040]\nfor i,v in enumerate(inputs):\n    got = fact(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')"),
        
        ("编写函数 is_prime(n) 判断 n 是否为质数。", 
         "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0:\n            return False\n    return True",
         "inputs = [1,2,3,4,5,17,25]\noutputs = [False,True,True,False,True,True,False]\nfor i,v in enumerate(inputs):\n    got = is_prime(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')"),
        
        ("编写函数 fibonacci(n) 返回第n个斐波那契数。", 
         "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    a, b = 0, 1\n    for _ in range(2, n+1):\n        a, b = b, a+b\n    return b",
         "inputs = [0,1,5,10]\noutputs = [0,1,5,55]\nfor i,v in enumerate(inputs):\n    got = fibonacci(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')"),
        
        ("编写函数 reverse_string(s) 返回字符串的逆序。", 
         "def reverse_string(s):\n    return s[::-1]",
         "inputs = ['','a','hello','python']\noutputs = ['','a','olleh','nohtyp']\nfor i,v in enumerate(inputs):\n    got = reverse_string(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')"),
        
        ("编写函数 count_vowels(s) 统计字符串中元音字母的数量。", 
         "def count_vowels(s):\n    vowels = 'aeiouAEIOU'\n    count = 0\n    for char in s:\n        if char in vowels:\n            count += 1\n    return count",
         "inputs = ['','hello','Python','AEIOU']\noutputs = [0,2,1,5]\nfor i,v in enumerate(inputs):\n    got = count_vowels(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')"),
    ]

    # 生成100道题目
    for i in range(100):
        if i < 60:  # 60% 选择题
            template = choice_templates[i % len(choice_templates)]
            title = f"{i+1}. {template[0]}"
            opts = template[1]
            samples.append(Question(
                qtype='choice',
                title=title,
                option_a=opts[0],
                option_b=opts[1],
                option_c=opts[2],
                option_d=opts[3],
                answer=template[2],
                difficulty=(i % 3) + 1  # 难度1-3
            ))
            
        elif i < 90:  # 30% 填空题
            template = fill_templates[(i-60) % len(fill_templates)]
            title = f"{i+1}. {template[0]}"
            samples.append(Question(
                qtype='fill',
                title=title,
                answer=template[1],
                difficulty=(i % 3) + 1
            ))
            
        else:  # 10% 编程题
            template = code_templates[(i-90) % len(code_templates)]
            title = f"{i+1}. {template[0]}"
            samples.append(Question(
                qtype='code',
                title=title,
                answer=template[1],
                judge_template=template[2],
                difficulty=3  # 编程题难度较高
            ))

    # 逐一添加并提交
    for q in samples:
        existing = Question.query.filter_by(title=q.title).first()
        if not existing:  # 避免重复添加
            db.session.add(q)
    db.session.commit()
    return len(samples)
