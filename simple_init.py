# simple_init.py
"""
简化的数据库初始化脚本，专门用于测试题目插入功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simple_init():
    """简化初始化，专注于题目插入"""
    from app import create_app, db
    from app.models import Question, User, insert_sample_questions
    
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("开始简化数据库初始化")
        print("=" * 50)
        
        # 创建表
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 创建管理员账户（如果不存在）
        admin = User.query.filter_by(username='x').first()
        if not admin:
            admin = User(username='x', is_admin=True)
            admin.set_password('1')
            db.session.add(admin)
            db.session.commit()
            print("✓ 管理员账户创建成功")
        else:
            print("✓ 管理员账户已存在")
        
        # 检查当前题目数量
        initial_count = Question.query.count()
        print(f"初始题目数量: {initial_count}")
        
        # 插入题目
        # if initial_count < 300:
        #     print("开始插入题目...")
        #     added_count = insert_sample_questions()
        #     final_count = Question.query.count()
        #     print(f"✓ 题目插入完成: 添加了 {added_count} 道题，当前总数 {final_count}")
        # else:
        #     print(f"✓ 题库已有 {initial_count} 道题，无需添加")
        
        print("=" * 50)
        print("数据库初始化完成")
        print("=" * 50)

if __name__ == '__main__':
    simple_init()