# db_init.py
"""
数据库初始化脚本：创建数据库表并插入100道示例题目。
"""

import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Question, ExamRecord, insert_sample_questions

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功")
        
        # 创建内置管理员账户（如果不存在）
        admin = User.query.filter_by(username='x').first()
        if not admin:
            admin = User(username='x', is_admin=True)
            admin.set_password('1')
            db.session.add(admin)
            db.session.commit()
            print("管理员账户创建成功: 用户名 'x', 密码 '1'")
        else:
            print("管理员账户已存在")
        
        # 插入300道示例题目
        question_count = Question.query.count()
        if question_count < 300:
            added_count = insert_sample_questions()
            print(f"成功添加 {added_count} 道题目，当前题库共有 {Question.query.count()} 道题")
        else:
            print(f"题库已有 {question_count} 道题，无需添加")
        
        print("数据库初始化完成")

if __name__ == '__main__':
    init_database()