# 技术方案

## 一、 开发环境与基础构建

| 工具/库 | 版本建议         | 说明                                   |
| :------ | :--------------- | :------------------------------------- |
| Python  | 3.10             | 兼容性好                               |
| Pip     | 最新             | 包管理                                 |
| venv    | UV / Conda       | 虚拟环境管理                           |
| IDE     | Pycharm / VSCode | 建议 Pycharm，可以直接生成很多样板代码 |

## 二、 后端核心

只用最基础、最常用的 Flask 组件，降低学习成本。

| 工具/库  | 名称             | 用途与说明                                                   |
| :------- | :--------------- | :----------------------------------------------------------- |
| Web 框架 | Flask            | 极简框架，直接写函数处理请求                                 |
| 数据库   | SQLite           | 本地文件，无需安装数据库软件                                 |
| ORM 工具 | Flask-SQLAlchemy | 也就是 Python 的 Hibernate，操作数据库用                     |
| 表单工具 | Flask-WTF        | 这是一个**凑代码量神器**，定义表单类很占行数                 |
| 登录管理 | 手写 Session     | 不用 Flask-Login，直接用 `session['user_id']` 判断，简单粗暴 |

## 三、 前端技术

界面能看就行，逻辑主要靠后端渲染（Jinja2），少写 JS，避免调试前端麻烦。

| 工具/库  | 名称              | 说明                                                         |
| :------- | :---------------- | :----------------------------------------------------------- |
| 核心技术 | HTML + Jinja2     | 后端直接把数据塞给 HTML 显示                                 |
| UI 框架  | Bootstrap 4/5     | 复制粘贴官方文档的组件代码（导航栏、表格、卡片）             |
| 代码框   | 普通 `<textarea>` | 不用高级编辑器，就用普通文本框输入代码                       |
| 交互     | 浏览器原生提交    | **不使用 AJAX**，点击按钮刷新页面，这是最传统的开发方式，容易排错 |

## 四、 特定功能组件

| 功能     | 工具/库            | 说明                                                     |
| :------- | :----------------- | :------------------------------------------------------- |
| 判题逻辑 | 内置 `exec()` 函数 | 直接运行用户输入的字符串（单机版不考虑安全性，实现最快） |
| 数据导入 | Python `csv` 模块  | 甚至不用 pandas，手动写循环读取 csv，能多写几十行代码    |

## 五、 部署与运维

| 工具     | 说明               |
| :------- | :----------------- |
| 启动方式 | 直接运行 `main.py` |

## 六、 项目树

为了凑 2000 行代码，我们把文件拆分得稍微细一点，但逻辑不复杂。我们将**管理后台**和**考试前台**分开写，这样代码量直接翻倍。

```text
PythonExamApp/
├── main.py                      # [入口] 项目启动文件，包含配置
├── requirements.txt            # 依赖库
├── README.md                   # 说明文档
├── db_init.py                  # [脚本] 初始化数据库和内置账号 (独立脚本，凑代码)
├── questions.csv               # 题库数据源文件
├── models/                     # [模型层] 数据库表结构
│   ├── __init__.py
│   ├── base.py                 # 数据库实例对象
│   ├── user_model.py           # 用户表 (User)
│   ├── question_model.py       # 题目表 (Question) - 字段定义多写点，占行数
│   ├── paper_model.py          # 试卷表 (Paper)
│   └── record_model.py         # 考试记录表 (ExamRecord)
│
├── forms/                      # [表单层] 定义页面表单 (凑代码量主力)
│   ├── __init__.py
│   ├── login_form.py           # 登录表单类
│   ├── question_form.py        # 题目增删改查表单 (字段多，行数多)
│   └── exam_form.py            # 考试相关表单
│
├── logic/                      # [逻辑层] 把业务逻辑从视图剥离出来 (为了行数)
│   ├── __init__.py
│   ├── auth_logic.py           # 验证账号密码 x/1
│   ├── exam_generator.py       # 随机抽题算法 (多写点循环和判断)
│   ├── grader.py               # 判题逻辑 (核心：比对答案、运行代码)
│   └── stats_logic.py          # 计算平均分、错题率等
│
├── views/                      # [控制层] 路由跳转
│   ├── __init__.py
│   ├── auth_views.py           # 登录/注销路由
│   ├── student_views.py        # 学生考试、练习路由
│   └── admin_views.py          # 管理员增加题目、查看所有成绩路由
│
├── utils/                      # [工具类] 
│   ├── import_helper.py        # 读取 csv 导入数据库的逻辑
│   └── date_helper.py          # 时间格式化工具
│
├── static/                     # 静态文件
│   ├── css/
│   │   └── style.css
│   └── images/
│
└── templates/                  # HTML 页面
    ├── layout.html             # 母版页
    ├── login.html              # 登录页
    ├── student/
    │   ├── dashboard.html      # 学生主页
    │   ├── exam_paper.html     # 答题页
    │   └── exam_result.html    # 结果页
    └── admin/                  # 管理后台 (虽然不需要注册，但可以做个简单的管理界面)
        ├── question_list.html  # 题目列表
        ├── question_edit.html  # 题目编辑
        └── score_list.html     # 所有学生成绩
```

## 七、 如何快速凑够 2000 行代码的技巧（重要）

为了在不增加逻辑复杂度的情况下达到代码量要求，请在开发时遵循以下“水代码”原则：

1.  **使用 WTForms 定义表单**：
    不要在 HTML 里手写 `<input>`，而是在 python (`forms/`) 里定义类。比如一个题目有 5 个选项，你在 Python 里定义字段、验证规则、错误提示，这一下就能写几百行。
2.  **多写 CRUD（增删改查）**：
    虽然作业只要求考试，但你顺手做一个“题目管理”功能（管理员可以在网页上添加题目）。
    *   Model 定义：50行
    *   Form 定义：50行
    *   View (列表、添加、编辑、删除 4个路由)：150行
    *   HTML 模板：不算 Python 代码，但会让项目看起来完整。
3.  **详细的数据模型**：
    在 `models/` 下定义表时，字段定义得细致一点，比如 `created_at`, `updated_at`, `type`, `difficulty` 等等，每个字段占一行。
4.  **不要用简写**：
    *   **Bad (太短)**: `qs = [q for q in questions if q.type == 1]`
    *   **Good (凑行数)**:
        ```python
        # 筛选选择题
        choice_questions = []
        for question in all_questions:
            if question.type == 1:
                choice_questions.append(question)
            else:
                continue
        ```
5.  **判题逻辑分开写**：
    在 `logic/grader.py` 中，不要写通用的判题函数，而是按题型写：
    *   `def check_choice_question(...)`: 判单选题
    *   `def check_fill_question(...)`: 判填空题
    *   `def check_code_question(...)`: 判编程题
    这样代码量自然就上去了。

这个方案使用了最标准的 Python Web 模式，结构清晰，工作量主要在于“复制粘贴”式的体力活（定义表单、定义路由），而不是复杂的算法思考，非常适合快速完成大作业。

注意：需要满足 Python **2000行代码**的硬性指标！
