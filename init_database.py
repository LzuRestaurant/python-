# init_database.py
"""
数据库初始化脚本：确保题目正确添加到数据库
"""

import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Question, insert_sample_questions

def init_database(force=False):
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 创建内置管理员账户
        admin = User.query.filter_by(username='x').first()
        if not admin:
            admin = User(username='x', is_admin=True)
            admin.set_password('1')
            db.session.add(admin)
            db.session.commit()
            print("✓ 管理员账户创建成功: 用户名 'x', 密码 '1'")
        else:
            print("✓ 管理员账户已存在")
        
        # 检查题目数量
        question_count = Question.query.count()
        print(f"当前题库题目数量: {question_count}")
        
        # 如果强制初始化或题目数量不足，则插入题目
        if force or question_count < 300:
            print("开始插入示例题目...")
            added_count = insert_sample_questions()
            final_count = Question.query.count()
            print(f"✓ 成功添加 {added_count} 道题目")
            print(f"✓ 当前题库共有 {final_count} 道题")
        else:
            print(f"✓ 题库已有 {question_count} 道题，无需添加")
        
        print("数据库初始化完成")

if __name__ == '__main__':
    # 检查命令行参数
    force = '--force' in sys.argv
    init_database(force=force)