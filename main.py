# main.py - 启动入口（你要求入口文件名为 main.py）
from app import create_app

app = create_app()

if __name__ == '__main__':
    # 开发使用，debug 模式
    app.run(host='127.0.0.1', port=5000, debug=True)
