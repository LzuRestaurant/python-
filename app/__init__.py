# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """
    创建 Flask 应用并注册蓝图。
    这里尽量写清楚每一步，方便你理解项目结构。
    """
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    # 加载配置
    app.config.from_object('app.config.Config')

    # 初始化第三方扩展
    db.init_app(app)

    # 导入并注册蓝图模块
    from .auth.routes import auth_bp
    from .student.routes import student_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # 创建数据库（如果尚未创建）
    with app.app_context():
        # 导入 models 以确保表模型已定义
        from . import models
        db.create_all()
        # 创建内置用户（如果不存在）
        models.create_builtin_users()

    return app
