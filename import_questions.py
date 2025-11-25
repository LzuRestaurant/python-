# import_questions.py
"""
批量导入题目脚本：用于快速导入300道题目到数据库。
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Question, User

def import_questions():
    """导入300道题目到数据库"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有题目
        count_before = Question.query.count()
        print(f"导入前题目数量: {count_before}")
        
        if count_before >= 300:
            print("题库已有足够题目，无需导入")
            return
        
        # 导入题目
        from app.models import insert_sample_questions
        added_count = insert_sample_questions()
        
        count_after = Question.query.count()
        print(f"成功导入 {added_count} 道题目")
        print(f"导入后题目数量: {count_after}")
        
        # 检查用户
        users = User.query.all()
        print(f"系统用户数量: {len(users)}")
        for user in users:
            print(f"用户: {user.username} (管理员: {user.is_admin})")

if __name__ == '__main__':
    import_questions()