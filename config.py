"""
配置文件
"""
import os

class Config:
    """應用配置"""
    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 上傳配置
    UPLOAD_FOLDER = 'static/uploads'
    OUTPUT_FOLDER = 'output'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
    
    # 水印配置
    DEFAULT_WATERMARK_TEXT = '機密文件'
    DEFAULT_FONT_SIZE = 36
    DEFAULT_OPACITY = 0.5
    DEFAULT_POSITION = 'bottomright'
    
    # blind_watermark 配置
    DEFAULT_PASSWORD_IMG = 1
    DEFAULT_PASSWORD_WM = 1

