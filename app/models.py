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
    
    # 基础选择题（150道）- 确保每个选项都有4个元素
    choice_questions = [
        # Python基础语法 (1-30)
        ("Python中用于输出的函数是？", "print()", ["print()", "input()", "len()", "open()"], "A", 1),
        ("定义函数使用的关键字是？", "def", ["func", "def", "function", "define"], "B", 1),
        ("获取列表长度的函数是？", "len()", ["size()", "length()", "len()", "count()"], "C", 1),
        ("下列哪个不是Python数据类型？", "char", ["int", "str", "char", "float"], "C", 1),
        ("Python中表示真值的布尔值是？", "True", ["True", "true", "TRUE", "1"], "A", 1),
        ("导入模块使用的关键字是？", "import", ["include", "import", "using", "require"], "B", 1),
        ("Python中单行注释的符号是？", "#", ["//", "#", "/*", "--"], "B", 1),
        ("下列哪个是可变数据类型？", "list", ["tuple", "str", "list", "int"], "C", 1),
        ("读取用户输入的函数是？", "input()", ["read()", "input()", "get()", "scan()"], "B", 1),
        ("创建空列表的语法是？", "[]", ["[]", "{}", "()", "None"], "A", 1),
        ("Python中表示空值的关键字是？", "None", ["null", "None", "nil", "undefined"], "B", 1),
        ("字典的表示方式是？", "{}", ["()", "[]", "{}", "<>"], "C", 1),
        ("删除变量的关键字是？", "del", ["remove", "delete", "del", "pop"], "C", 1),
        ("求幂运算符是？", "**", ["^", "**", "//", "%%"], "B", 1),
        ("逻辑与操作的关键字是？", "and", ["and", "&&", "&", "AND"], "A", 1),
        ("逻辑或操作的关键字是？", "or", ["or", "||", "|", "OR"], "A", 1),
        ("逻辑非操作的关键字是？", "not", ["not", "!", "~", "NOT"], "A", 1),
        ("表示除法的整数部分运算符是？", "//", ["//", "/", "%", "div"], "A", 1),
        ("取模运算符是？", "%", ["%", "mod", "//", "&"], "A", 1),
        ("比较两个值是否相等的运算符是？", "==", ["=", "==", "===", "eq"], "B", 1),
        ("比较两个值是否不相等的运算符是？", "!=", ["!=", "<>", "!==", "ne"], "A", 1),
        ("成员测试运算符是？", "in", ["in", "contains", "has", "member"], "A", 1),
        ("身份测试运算符是？", "is", ["is", "==", "===", "id"], "A", 1),
        ("三元条件表达式的语法是？", "x if condition else y", 
         ["x if condition else y", "condition ? x : y", "if condition then x else y", "x when condition else y"], "A", 2),
        ("用于序列解包的操作是？", "a, b = b, a", ["a, b = b, a", "swap(a, b)", "a = b; b = a", "exchange(a, b)"], "A", 2),
        ("用于字符串格式化的f-string前缀是？", "f", ["f", "F", "format", "fmt"], "A", 2),
        ("用于定义多行字符串的语法是？", "三引号", ["单引号", "双引号", "三引号", "反引号"], "C", 1),
        ("用于退出程序的内置函数是？", "exit()", ["quit()", "exit()", "stop()", "end()"], "B", 2),
        ("获取对象类型的内置函数是？", "type()", ["type()", "typeof()", "kind()", "category()"], "A", 2),
        ("用于获取对象唯一标识的内置函数是？", "id()", ["id()", "identity()", "uid()", "hash()"], "A", 2),
        
        # 数据类型和方法 (31-60)
        ("向列表添加元素的方法是？", "append()", ["add()", "append()", "insert()", "push()"], "B", 2),
        ("获取字符串长度的方法是？", "len()", ["length()", "size()", "len()", "count()"], "C", 2),
        ("字典获取所有键的方法是？", "keys()", ["keys()", "getKeys()", "allKeys()", "keyList()"], "A", 2),
        ("检查元素是否在序列中的关键字是？", "in", ["in", "exist", "has", "contain"], "A", 2),
        ("创建集合的函数是？", "set()", ["set()", "{}", "[]", "()"], "A", 2),
        ("向集合添加元素的方法是？", "add()", ["add()", "append()", "insert()", "put()"], "A", 2),
        ("从列表中删除元素的方法是？", "remove()", ["delete()", "remove()", "pop()", "discard()"], "B", 2),
        ("列表排序的方法是？", "sort()", ["sort()", "order()", "arrange()", "sorted()"], "A", 2),
        ("返回列表排序副本的函数是？", "sorted()", ["sort()", "sorted()", "order()", "arrange()"], "B", 2),
        ("字符串转换为大写的方法是？", "upper()", ["upper()", "uppercase()", "toUpper()", "capitalize()"], "A", 2),
        ("字符串转换为小写的方法是？", "lower()", ["lower()", "lowercase()", "toLower()", "small()"], "A", 2),
        ("字符串首字母大写的方法是？", "capitalize()", ["capitalize()", "title()", "upperFirst()", "cap()"], "A", 2),
        ("字符串每个单词首字母大写的方法是？", "title()", ["title()", "capitalize()", "upperAll()", "capWords()"], "A", 2),
        ("字符串去除两端空格的方法是？", "strip()", ["strip()", "trim()", "clean()", "removeSpace()"], "A", 2),
        ("字符串查找子串位置的方法是？", "find()", ["find()", "search()", "index()", "locate()"], "A", 2),
        ("字符串替换子串的方法是？", "replace()", ["replace()", "substitute()", "change()", "swap()"], "A", 2),
        ("字符串分割的方法是？", "split()", ["split()", "divide()", "separate()", "cut()"], "A", 2),
        ("列表反转的方法是？", "reverse()", ["reverse()", "invert()", "flip()", "backwards()"], "A", 2),
        ("列表获取元素索引的方法是？", "index()", ["index()", "find()", "search()", "locate()"], "A", 2),
        ("列表统计元素出现次数的方法是？", "count()", ["count()", "total()", "sum()", "occurrences()"], "A", 2),
        ("字典获取所有值的方法是？", "values()", ["values()", "getValues()", "allValues()", "valueList()"], "A", 2),
        ("字典获取所有键值对的方法是？", "items()", ["items()", "pairs()", "entries()", "keyValues()"], "A", 2),
        ("字典检查键是否存在的方法是？", "in", ["in", "has_key()", "contains()", "exists()"], "A", 2),
        ("集合的交集操作方法是？", "intersection()", ["intersection()", "and", "common()", "shared()"], "A", 3),
        ("集合的并集操作方法是？", "union()", ["union()", "or", "combine()", "merge()"], "A", 3),
        ("集合的差集操作方法是？", "difference()", ["difference()", "subtract()", "minus()", "remove()"], "A", 3),
        ("元组与列表的主要区别是？", "元组不可变", ["元组不可变", "元组有序", "元组可哈希", "元组效率高"], "A", 2),
        ("用于深度拷贝的函数是？", "deepcopy()", ["copy()", "deepcopy()", "clone()", "duplicate()"], "B", 3),
        ("用于浅拷贝的方法是？", "copy()", ["copy()", "clone()", "duplicate()", "replicate()"], "A", 3),
        
        # 控制结构 (61-90)
        ("条件判断的关键字是？", "if", ["if", "when", "case", "check"], "A", 1),
        ("提前结束循环的关键字是？", "break", ["break", "exit", "stop", "end"], "A", 2),
        ("跳过当前循环迭代的关键字是？", "continue", ["continue", "skip", "next", "pass"], "A", 2),
        ("异常处理中捕获异常的关键字是？", "except", ["try", "catch", "except", "finally"], "C", 2),
        ("用于循环遍历序列的关键字是？", "for", ["for", "while", "loop", "each"], "A", 1),
        ("用于条件循环的关键字是？", "while", ["while", "for", "loop", "until"], "A", 1),
        ("if-else的替代语法是？", "elif", ["elif", "elseif", "else if", "elseif"], "A", 1),
        ("用于处理没有异常的情况的关键字是？", "else", ["else", "noexcept", "success", "normal"], "A", 3),
        ("无论是否发生异常都会执行的块是？", "finally", ["finally", "always", "ensure", "must"], "A", 3),
        ("主动抛出异常的关键字是？", "raise", ["raise", "throw", "error", "exception"], "A", 3),
        ("断言检查的关键字是？", "assert", ["assert", "check", "verify", "ensure"], "A", 3),
        ("用于遍历序列索引和值的内置函数是？", "enumerate()", ["enumerate()", "indexed()", "withIndex()", "iterIndex()"], "A", 2),
        ("用于同时遍历多个序列的内置函数是？", "zip()", ["zip()", "parallel()", "together()", "combine()"], "A", 2),
        ("用于生成整数序列的内置函数是？", "range()", ["range()", "sequence()", "numbers()", "ints()"], "A", 2),
        ("用于创建迭代器的内置函数是？", "iter()", ["iter()", "iterator()", "generate()", "createIterator()"], "A", 3),
        ("用于过滤序列的内置函数是？", "filter()", ["filter()", "select()", "where()", "findAll()"], "A", 3),
        ("用于映射函数到序列的内置函数是？", "map()", ["map()", "apply()", "transform()", "convert()"], "A", 3),
        ("用于累积计算的内置函数是？", "reduce()", ["reduce()", "accumulate()", "summarize()", "fold()"], "A", 3),
        ("用于排序序列的内置函数是？", "sorted()", ["sorted()", "sort()", "order()", "arrange()"], "A", 2),
        ("用于反转序列的内置函数是？", "reversed()", ["reversed()", "reverse()", "backwards()", "invert()"], "A", 2),
        ("用于获取序列中最大值的函数是？", "max()", ["max()", "maximum()", "largest()", "biggest()"], "A", 2),
        ("用于获取序列中最小值的函数是？", "min()", ["min()", "minimum()", "smallest()", "least()"], "A", 2),
        ("用于求和的函数是？", "sum()", ["sum()", "total()", "add()", "accumulate()"], "A", 2),
        ("用于计算长度的函数是？", "len()", ["len()", "length()", "size()", "count()"], "A", 1),
        ("用于检查是否为真的函数是？", "all()", ["all()", "any()", "true()", "checkAll()"], "A", 3),
        ("用于检查是否有真的函数是？", "any()", ["any()", "all()", "some()", "exists()"], "A", 3),
        ("用于创建枚举常量的模块是？", "enum", ["enum", "constant", "const", "value"], "A", 3),
        ("用于生成随机数的模块是？", "random", ["random", "rand", "chance", "probability"], "A", 2),
        ("用于数学运算的模块是？", "math", ["math", "calculate", "compute", "arithmetic"], "A", 2),
        ("用于日期时间操作的模块是？", "datetime", ["datetime", "time", "date", "calendar"], "A", 2),
        
        # 函数和模块 (91-120)
        ("函数中用于返回值的关键字是？", "return", ["return", "output", "result", "yield"], "A", 1),
        ("定义匿名函数的关键字是？", "lambda", ["lambda", "def", "function", "anon"], "A", 2),
        ("从模块导入特定函数的语法是？", "from module import function", ["from module import function", "import function from module", "include function from module", "using module.function"], "A", 2),
        ("用于函数参数解包的操作符是？", "*", ["*", "**", "...", "&"], "A", 3),
        ("用于关键字参数解包的操作符是？", "**", ["**", "*", "...", "&"], "B", 3),
        ("定义可变位置参数的语法是？", "*args", ["*args", "**kwargs", "*params", "**options"], "A", 3),
        ("定义可变关键字参数的语法是？", "**kwargs", ["**kwargs", "*args", "**params", "*options"], "A", 3),
        ("用于函数注解的语法是？", "->", ["->", ":", "=>", "annotate"], "A", 3),
        ("用于创建生成器的关键字是？", "yield", ["yield", "generate", "return", "produce"], "A", 3),
        ("用于上下文管理的关键字是？", "with", ["with", "using", "context", "manage"], "A", 3),
        ("用于创建装饰器的语法是？", "@", ["@", "#", "$", "%"], "A", 3),
        ("用于将方法转换为属性的装饰器是？", "@property", ["@property", "@attribute", "@getter", "@prop"], "A", 3),
        ("用于类方法的装饰器是？", "@classmethod", ["@classmethod", "@staticmethod", "@method", "@class"], "A", 3),
        ("用于静态方法的装饰器是？", "@staticmethod", ["@staticmethod", "@classmethod", "@method", "@static"], "B", 3),
        ("用于函数缓存的标准库模块是？", "functools.lru_cache", ["functools.lru_cache", "cache", "memoize", "remember"], "A", 3),
        ("用于序列化对象的模块是？", "pickle", ["pickle", "serialize", "marshal", "dump"], "A", 3),
        ("用于JSON序列化的模块是？", "json", ["json", "simplejson", "ujson", "orjson"], "A", 2),
        ("用于正则表达式操作的模块是？", "re", ["re", "regex", "regexp", "pattern"], "A", 2),
        ("用于系统相关参数的模块是？", "sys", ["sys", "os", "system", "platform"], "A", 2),
        ("用于操作系统相关功能的模块是？", "os", ["os", "sys", "system", "platform"], "A", 2),
        ("用于文件路径操作的模块是？", "os.path", ["os.path", "path", "pathlib", "filepath"], "A", 2),
        ("用于命令行参数解析的模块是？", "argparse", ["argparse", "getopt", "optparse", "sys.argv"], "A", 3),
        ("用于日志记录的模块是？", "logging", ["logging", "log", "logger", "record"], "A", 3),
        ("用于单元测试的模块是？", "unittest", ["unittest", "test", "testing", "pytest"], "A", 3),
        ("用于时间测量的模块是？", "timeit", ["timeit", "time", "timer", "measure"], "A", 3),
        ("用于数据压缩的模块是？", "zipfile", ["zipfile", "gzip", "tarfile", "compress"], "A", 3),
        ("用于网络请求的模块是？", "urllib", ["urllib", "requests", "http.client", "socket"], "A", 3),
        ("用于电子邮件处理的模块是？", "smtplib", ["smtplib", "email", "mail", "message"], "A", 3),
        ("用于多线程编程的模块是？", "threading", ["threading", "thread", "multithreading", "concurrent"], "A", 3),
        ("用于多进程编程的模块是？", "multiprocessing", ["multiprocessing", "process", "multiprocess", "parallel"], "A", 3),
        
        # 面向对象编程 (121-150)
        ("定义类的关键字是？", "class", ["class", "struct", "object", "type"], "A", 2),
        ("类中表示实例自身的关键字是？", "self", ["self", "this", "me", "instance"], "A", 2),
        ("类的构造函数方法是？", "__init__", ["__init__", "__construct__", "__new__", "__create__"], "A", 2),
        ("用于表示继承的语法是？", "class Child(Parent)", ["class Child(Parent)", "class Child extends Parent", "class Child : Parent", "class Child inherits Parent"], "A", 2),
        ("用于访问父类方法的内置函数是？", "super()", ["super()", "parent()", "base()", "superclass()"], "A", 3),
        ("用于表示类方法的第一个参数是？", "cls", ["cls", "self", "class", "this"], "A", 3),
        ("用于定义只读属性的装饰器是？", "@property", ["@property", "@attribute", "@readonly", "@getter"], "A", 3),
        ("用于运算符重载的方法前缀是？", "__", ["__", "operator", "op", "magic"], "A", 3),
        ("用于字符串表示的方法是？", "__str__", ["__str__", "__repr__", "__string__", "__format__"], "A", 3),
        ("用于官方字符串表示的方法是？", "__repr__", ["__repr__", "__str__", "__string__", "__official__"], "A", 3),
        ("用于对象比较相等的方法是？", "__eq__", ["__eq__", "__equal__", "__cmp__", "__same__"], "A", 3),
        ("用于对象比较大小的方法是？", "__lt__", ["__lt__", "__less__", "__cmp__", "__compare__"], "A", 3),
        ("用于对象哈希值的方法是？", "__hash__", ["__hash__", "__hashcode__", "__id__", "__key__"], "A", 3),
        ("用于对象长度的方法是？", "__len__", ["__len__", "__length__", "__size__", "__count__"], "A", 3),
        ("用于对象调用语法的方法是？", "__call__", ["__call__", "__invoke__", "__run__", "__execute__"], "A", 3),
        ("用于属性访问的方法是？", "__getattr__", ["__getattr__", "__getattribute__", "__access__", "__attr__"], "A", 3),
        ("用于属性设置的方法是？", "__setattr__", ["__setattr__", "__setattribute__", "__assign__", "__put__"], "A", 3),
        ("用于属性删除的方法是？", "__delattr__", ["__delattr__", "__delete__", "__remove__", "__clear__"], "A", 3),
        ("用于迭代器协议的方法是？", "__iter__", ["__iter__", "__iterator__", "__next__", "__loop__"], "A", 3),
        ("用于上下文管理器进入的方法是？", "__enter__", ["__enter__", "__start__", "__begin__", "__open__"], "A", 3),
        ("用于上下文管理器退出的方法是？", "__exit__", ["__exit__", "__end__", "__close__", "__finish__"], "A", 3),
        ("用于实现加法运算的方法是？", "__add__", ["__add__", "__plus__", "__sum__", "__append__"], "A", 3),
        ("用于实现减法运算的方法是？", "__sub__", ["__sub__", "__minus__", "__subtract__", "__remove__"], "A", 3),
        ("用于实现乘法运算的方法是？", "__mul__", ["__mul__", "__multiply__", "__times__", "__product__"], "A", 3),
        ("用于实现除法运算的方法是？", "__truediv__", ["__truediv__", "__divide__", "__div__", "__split__"], "A", 3),
        ("用于实现取模运算的方法是？", "__mod__", ["__mod__", "__modulo__", "__remainder__", "__percent__"], "A", 3),
        ("用于实现幂运算的方法是？", "__pow__", ["__pow__", "__power__", "__exponent__", "__exp__"], "A", 3),
        ("用于实现位与运算的方法是？", "__and__", ["__and__", "__bitand__", "__band__", "__binaryand__"], "A", 3),
        ("用于实现位或运算的方法是？", "__or__", ["__or__", "__bitor__", "__bor__", "__binaryor__"], "A", 3),
    ]
    
    # 扩展填空题 (151-250)
    fill_questions = [
        # 基础语法填空
        ("在Python中，表示整数类型的内置函数是__。", "int", 1),
        ("用于将字符串转换为小写的方法是__。", "lower", 1),
        ("列表追加元素的方法是__。", "append", 1),
        ("获得列表长度使用__。", "len", 1),
        ("Python中用于条件判断的关键字是__。", "if", 1),
        ("用于循环遍历序列的关键字是__。", "for", 1),
        ("定义类的关键字是__。", "class", 2),
        ("异常处理中捕获所有异常的关键字是__。", "except", 2),
        ("用于打开文件的内置函数是__。", "open", 2),
        ("从函数中返回值的语句是__。", "return", 2),
        
        # 继续添加更多填空题...
        ("表示空值的特殊关键字是__。", "None", 1),
        ("用于逻辑与操作的关键字是__。", "and", 1),
        ("删除变量的关键字是__。", "del", 2),
        ("用于求幂的运算符是__。", "**", 2),
        ("表示除法的整数部分运算符是__。", "//", 2),
        
        # 数据类型相关
        ("创建空列表的语法是__。", "[]", 1),
        ("创建空字典的语法是__。", "{}", 1),
        ("创建空元组的语法是__。", "()", 1),
        ("检查元素是否在序列中的关键字是__。", "in", 2),
        ("获取字符串长度的内置函数是__。", "len", 2),
        ("将对象转换为字符串的函数是__。", "str", 2),
        ("将字符串转换为整数的函数是__。", "int", 2),
        ("用于字符串分割的方法是__。", "split", 2),
        ("用于字符串连接的方法是__。", "join", 2),
        ("从列表中删除最后一个元素的方法是__。", "pop", 2),
        
        # 函数和模块
        ("定义匿名函数的关键字是__。", "lambda", 2),
        ("从模块导入特定函数的语法是__。", "from module import function", 2),
        ("Python中用于数学运算的标准模块是__。", "math", 2),
        ("用于操作系统相关功能的模块是__。", "os", 2),
        ("用于系统相关参数的模块是__。", "sys", 2),
        
        # 面向对象
        ("类中表示实例自身的第一个参数通常命名为__。", "self", 2),
        ("类的初始化方法名是__。", "__init__", 2),
        ("用于访问父类方法的内置函数是__。", "super", 3),
        ("表示私有属性的命名约定是以__开头。", "__", 3),
        ("用于获取对象类型的内置函数是__。", "type", 2),
        
        # 高级特性
        ("用于创建生成器的关键字是__。", "yield", 3),
        ("用于上下文管理的关键字是__。", "with", 3),
        ("用于将方法转换为属性的装饰器是__。", "@property", 3),
        ("Python 3.5引入的类型提示语法使用__模块。", "typing", 3),
        ("用于格式化字符串的f-string需要在字符串前加__。", "f", 2),
        
        # 继续添加更多填空题...
        ("用于正则表达式操作的模块是__。", "re", 2),
        ("用于JSON序列化的模块是__。", "json", 2),
        ("用于日期时间操作的模块是__。", "datetime", 2),
        ("用于随机数生成的模块是__。", "random", 2),
        ("用于命令行参数解析的模块是__。", "argparse", 3),
        ("用于日志记录的模块是__。", "logging", 3),
        ("用于单元测试的模块是__。", "unittest", 3),
        ("用于多线程编程的模块是__。", "threading", 3),
        ("用于多进程编程的模块是__。", "multiprocessing", 3),
        ("用于网络请求的模块是__。", "urllib", 3),
        
        # 面向对象编程相关
        ("类方法的第一个参数通常命名为__。", "cls", 3),
        ("实例方法的第一个参数通常命名为__。", "self", 2),
        ("用于运算符重载的方法前缀是__。", "__", 3),
        ("用于字符串表示的方法是__。", "__str__", 3),
        ("用于官方字符串表示的方法是__。", "__repr__", 3),
        ("用于对象比较相等的方法是__。", "__eq__", 3),
        ("用于对象长度的方法是__。", "__len__", 3),
        ("用于属性访问的方法是__。", "__getattr__", 3),
        ("用于迭代器协议的方法是__。", "__iter__", 3),
        ("用于上下文管理器进入的方法是__。", "__enter__", 3),
    ]
    
    # 编程题 (251-300)
    code_questions = [
        # 基础算法题
        ("编写函数 fact(n) 返回 n 的阶乘。", 
         "def fact(n):\n    if n <= 1:\n        return 1\n    r = 1\n    for i in range(2, n+1):\n        r *= i\n    return r",
         "inputs = [0,1,5,7]\noutputs = [1,1,120,5040]\nfor i,v in enumerate(inputs):\n    got = fact(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        ("编写函数 is_prime(n) 判断 n 是否为质数。", 
         "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0:\n            return False\n    return True",
         "inputs = [1,2,3,4,5,17,25]\noutputs = [False,True,True,False,True,True,False]\nfor i,v in enumerate(inputs):\n    got = is_prime(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 fibonacci(n) 返回第n个斐波那契数。", 
         "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    a, b = 0, 1\n    for _ in range(2, n+1):\n        a, b = b, a+b\n    return b",
         "inputs = [0,1,5,10]\noutputs = [0,1,5,55]\nfor i,v in enumerate(inputs):\n    got = fibonacci(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 reverse_string(s) 返回字符串的逆序。", 
         "def reverse_string(s):\n    return s[::-1]",
         "inputs = ['','a','hello','python']\noutputs = ['','a','olleh','nohtyp']\nfor i,v in enumerate(inputs):\n    got = reverse_string(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        ("编写函数 count_vowels(s) 统计字符串中元音字母的数量。", 
         "def count_vowels(s):\n    vowels = 'aeiouAEIOU'\n    count = 0\n    for char in s:\n        if char in vowels:\n            count += 1\n    return count",
         "inputs = ['','hello','Python','AEIOU']\noutputs = [0,2,1,5]\nfor i,v in enumerate(inputs):\n    got = count_vowels(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        # 数据结构题
        ("编写函数 find_max(nums) 返回列表中的最大值。", 
         "def find_max(nums):\n    if not nums:\n        return None\n    max_val = nums[0]\n    for num in nums[1:]:\n        if num > max_val:\n            max_val = num\n    return max_val",
         "inputs = [[1,2,3], [5,3,8,1], [-1,-5,-2], [42]]\noutputs = [3,8,-1,42]\nfor i,v in enumerate(inputs):\n    got = find_max(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        ("编写函数 remove_duplicates(lst) 移除列表中的重复元素。", 
         "def remove_duplicates(lst):\n    seen = set()\n    result = []\n    for item in lst:\n        if item not in seen:\n            seen.add(item)\n            result.append(item)\n    return result",
         "inputs = [[1,2,2,3,4,4,5], ['a','b','a','c'], [1,1,1], []]\noutputs = [[1,2,3,4,5], ['a','b','c'], [1], []]\nfor i,v in enumerate(inputs):\n    got = remove_duplicates(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 is_palindrome(s) 判断字符串是否为回文。", 
         "def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]",
         "inputs = ['racecar', 'hello', 'A man a plan a canal Panama', '']\noutputs = [True, False, True, True]\nfor i,v in enumerate(inputs):\n    got = is_palindrome(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        ("编写函数 flatten(nested_list) 将嵌套列表展平。", 
         "def flatten(nested_list):\n    result = []\n    for item in nested_list:\n        if isinstance(item, list):\n            result.extend(flatten(item))\n        else:\n            result.append(item)\n    return result",
         "inputs = [[1,2,[3,4]], [[1,2],[3,[4,5]]], [1], []]\noutputs = [[1,2,3,4], [1,2,3,4,5], [1], []]\nfor i,v in enumerate(inputs):\n    got = flatten(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 word_count(text) 统计文本中单词的出现次数。", 
         "def word_count(text):\n    words = text.lower().split()\n    count = {}\n    for word in words:\n        word = word.strip('.,!?;:')\n        if word:\n            count[word] = count.get(word, 0) + 1\n    return count",
         "text = 'hello world hello python world hello'\nresult = word_count(text)\nexpected = {'hello': 3, 'world': 2, 'python': 1}\nfor k,v in expected.items():\n    if result.get(k) != v:\n        raise AssertionError(f'Expected {v} for {k}, got {result.get(k)}')", 3),
        
        # 继续添加更多编程题...
        ("编写函数 gcd(a, b) 计算两个数的最大公约数。", 
         "def gcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a",
         "inputs = [(48, 18), (17, 13), (100, 25), (0, 5)]\noutputs = [6, 1, 25, 5]\nfor i,v in enumerate(inputs):\n    got = gcd(v[0], v[1])\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 binary_search(arr, target) 实现二分查找。", 
         "def binary_search(arr, target):\n    low, high = 0, len(arr)-1\n    while low <= high:\n        mid = (low+high)//2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid+1\n        else:\n            high = mid-1\n    return -1",
         "inputs = [([1,3,5,7,9], 5), ([1,3,5,7,9], 2), ([], 1)]\noutputs = [2, -1, -1]\nfor i,v in enumerate(inputs):\n    got = binary_search(v[0], v[1])\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        ("编写函数 is_anagram(s1, s2) 判断两个字符串是否为字母异位词。", 
         "def is_anagram(s1, s2):\n    return sorted(s1.lower()) == sorted(s2.lower())",
         "inputs = [('listen', 'silent'), ('hello', 'world'), ('', '')]\noutputs = [True, False, True]\nfor i,v in enumerate(inputs):\n    got = is_anagram(v[0], v[1])\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 2),
        
        ("编写函数 validate_parentheses(s) 检查括号是否匹配。", 
         "def validate_parentheses(s):\n    stack = []\n    mapping = {')': '(', ']': '[', '}': '{'}\n    for char in s:\n        if char in mapping.values():\n            stack.append(char)\n        elif char in mapping:\n            if not stack or stack[-1] != mapping[char]:\n                return False\n            stack.pop()\n    return not stack",
         "inputs = ['()', '()[]{}', '(]', '([)]', '{[]}']\noutputs = [True, True, False, False, True]\nfor i,v in enumerate(inputs):\n    got = validate_parentheses(v)\n    if got != outputs[i]:\n        raise AssertionError(f'Expected {outputs[i]}, got {got}')", 3),
        
        # 面向对象编程题
        ("编写一个简单的类Person，包含name和age属性，以及一个介绍自己的方法。", 
         "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def introduce(self):\n        return f'我叫{self.name}，今年{self.age}岁'",
         "p = Person('张三', 25)\nresult = p.introduce()\nexpected = '我叫张三，今年25岁'\nif result != expected:\n    raise AssertionError(f'Expected {expected}, got {result}')", 2),
        
        ("编写一个计算器类Calculator，实现加减乘除四则运算。", 
         "class Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def subtract(self, a, b):\n        return a - b\n    \n    def multiply(self, a, b):\n        return a * b\n    \n    def divide(self, a, b):\n        if b == 0:\n            raise ValueError('除数不能为零')\n        return a / b",
         "calc = Calculator()\nassert calc.add(5, 3) == 8\nassert calc.subtract(5, 3) == 2\nassert calc.multiply(5, 3) == 15\nassert calc.divide(6, 3) == 2.0", 3),
        
        ("编写一个学生类Student，包含姓名、学号和成绩，以及计算平均成绩的方法。", 
         "class Student:\n    def __init__(self, name, student_id):\n        self.name = name\n        self.student_id = student_id\n        self.grades = []\n    \n    def add_grade(self, grade):\n        self.grades.append(grade)\n    \n    def average_grade(self):\n        if not self.grades:\n            return 0\n        return sum(self.grades) / len(self.grades)",
         "s = Student('李四', '2023001')\ns.add_grade(85)\ns.add_grade(90)\ns.add_grade(78)\navg = s.average_grade()\nif abs(avg - 84.333) > 0.001:\n    raise AssertionError(f'Expected about 84.333, got {avg}')", 3),
        
        ("编写一个银行账户类BankAccount，实现存款、取款和查询余额功能。", 
         "class BankAccount:\n    def __init__(self, account_holder, initial_balance=0):\n        self.account_holder = account_holder\n        self.balance = initial_balance\n    \n    def deposit(self, amount):\n        if amount <= 0:\n            raise ValueError('存款金额必须大于零')\n        self.balance += amount\n        return self.balance\n    \n    def withdraw(self, amount):\n        if amount <= 0:\n            raise ValueError('取款金额必须大于零')\n        if amount > self.balance:\n            raise ValueError('余额不足')\n        self.balance -= amount\n        return self.balance\n    \n    def get_balance(self):\n        return self.balance",
         "account = BankAccount('王五', 1000)\naccount.deposit(500)\naccount.withdraw(200)\nbalance = account.get_balance()\nif balance != 1300:\n    raise AssertionError(f'Expected 1300, got {balance}')", 3),
        
        ("编写一个矩形类Rectangle，计算面积和周长。", 
         "class Rectangle:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n    \n    def area(self):\n        return self.width * self.height\n    \n    def perimeter(self):\n        return 2 * (self.width + self.height)",
         "r = Rectangle(5, 3)\nif r.area() != 15:\n    raise AssertionError('面积计算错误')\nif r.perimeter() != 16:\n    raise AssertionError('周长计算错误')", 2),
        
        # 继续添加更多编程题...
        ("编写一个栈类Stack，实现压栈、弹栈和查看栈顶操作。", 
         "class Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        self.items.append(item)\n    \n    def pop(self):\n        if self.is_empty():\n            raise IndexError('栈为空')\n        return self.items.pop()\n    \n    def peek(self):\n        if self.is_empty():\n            raise IndexError('栈为空')\n        return self.items[-1]\n    \n    def is_empty(self):\n        return len(self.items) == 0\n    \n    def size(self):\n        return len(self.items)",
         "s = Stack()\ns.push(1)\ns.push(2)\nif s.pop() != 2:\n    raise AssertionError('弹栈错误')\nif s.peek() != 1:\n    raise AssertionError('查看栈顶错误')", 3),
        
        ("编写一个队列类Queue，实现入队、出队和查看队首操作。", 
         "class Queue:\n    def __init__(self):\n        self.items = []\n    \n    def enqueue(self, item):\n        self.items.append(item)\n    \n    def dequeue(self):\n        if self.is_empty():\n            raise IndexError('队列为空')\n        return self.items.pop(0)\n    \n    def front(self):\n        if self.is_empty():\n            raise IndexError('队列为空')\n        return self.items[0]\n    \n    def is_empty(self):\n        return len(self.items) == 0\n    \n    def size(self):\n        return len(self.items)",
         "q = Queue()\nq.enqueue(1)\nq.enqueue(2)\nif q.dequeue() != 1:\n    raise AssertionError('出队错误')\nif q.front() != 2:\n    raise AssertionError('查看队首错误')", 3),
        
        ("编写一个简单的装饰器，用于计算函数执行时间。", 
         "import time\n\ndef timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        end = time.time()\n        print(f'{func.__name__} 执行时间: {end - start:.2f}秒')\n        return result\n    return wrapper",
         "@timer\ndef test_func():\n    time.sleep(0.1)\n    return '完成'\n\nresult = test_func()\nif result != '完成':\n    raise AssertionError('装饰器测试失败')", 3),
        
        ("编写一个生成器函数，生成斐波那契数列。", 
         "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b",
         "fib = list(fibonacci(5))\nif fib != [0, 1, 1, 2, 3]:\n    raise AssertionError('斐波那契生成器错误')", 3),
    ]

    # 生成选择题
    # print("正在生成选择题...")
    for i, (title, answer, options, correct, difficulty) in enumerate(choice_questions):
        if len(samples) >= 300:
            break
            
        # 确保选项列表有4个元素
        while len(options) < 4:
            options.append("")  # 用空字符串填充不足的选项
            
        q = Question(
            qtype='choice',
            title=f"{len(samples)+1}. {title}",
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            answer=correct,
            difficulty=difficulty
        )
        samples.append(q)
    
    # 生成填空题
    # print("正在生成填空题...")
    for i, (title, answer, difficulty) in enumerate(fill_questions):
        if len(samples) >= 300:
            break
            
        q = Question(
            qtype='fill',
            title=f"{len(samples)+1}. {title}",
            answer=answer,
            difficulty=difficulty
        )
        samples.append(q)
    
    # 生成编程题
    # print("正在生成编程题...")
    for i, (title, answer, judge_template, difficulty) in enumerate(code_questions):
        if len(samples) >= 300:
            break
            
        q = Question(
            qtype='code',
            title=f"{len(samples)+1}. {title}",
            answer=answer,
            judge_template=judge_template,
            difficulty=difficulty
        )
        samples.append(q)
    added_count = 0
    for i, q in enumerate(samples):
        # 检查题目是否已存在（避免重复添加）
        existing = Question.query.filter_by(title=q.title).first()
        if not existing:
            db.session.add(q)
            added_count += 1
            if added_count % 50 == 0:  # 每50题打印一次进度
                print(f"已添加 {added_count} 道题目...")
    
    try:
        db.session.commit()
        final_count = Question.query.count()
        print(f"✓ 成功添加 {added_count} 道题目")
        print(f"✓ 插入后题目数量: {final_count}")
        return added_count
    except Exception as e:
        db.session.rollback()
        print(f"✗ 插入题目时出错: {e}")
        return 0

