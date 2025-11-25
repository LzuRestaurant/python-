# app/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_for_coursework_please_change'
    # SQLite 数据库文件放在项目目录下
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'exam_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 其它配置占位（可扩展）
    ITEMS_PER_PAGE = 20
    # 多媒体最大限制 (MB) - 这里保留配置但我们不会实际上传大文件
    MAX_MEDIA_MB = 300
