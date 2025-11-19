"""
WSGI 入口文件
用於生產環境部署
"""
from app import app

if __name__ == "__main__":
    app.run()

