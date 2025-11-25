# main.py - 启动入口（你要求入口文件名为 main.py）
from app import create_app
import sys

app = create_app()

if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        print("正在初始化数据库...")
        from db_init import init_database
        init_database()
        print("数据库初始化完成，启动应用...")
    
    # 开发使用，debug 模式
    app.run(host='127.0.0.1', port=5000, debug=True)
