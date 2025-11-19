"""
檔案管理服務
"""
import os
from werkzeug.utils import secure_filename
from datetime import datetime


class FileManager:
    """檔案管理服務"""
    
    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
        
        # 確保目錄存在
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """檢查文件類型"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_upload(self, file, filename=None):
        """
        儲存上傳的檔案
        
        Args:
            file: FileStorage 物件
            filename: 可選的自訂檔名
        
        Returns:
            str: 儲存的文件路徑
        """
        if filename is None:
            # 生成安全的文件名
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{timestamp}{ext}"
        else:
            filename = secure_filename(filename)
        
        # 儲存文件
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        
        return filepath
    
    def get_output_path(self, filename):
        """生成輸出檔案路徑"""
        return os.path.join(self.output_folder, filename)
    
    def cleanup_old_files(self, max_age_hours=24):
        """清理舊檔案"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for folder in [self.upload_folder, self.output_folder]:
            if not os.path.exists(folder):
                continue
                
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print(f"無法刪除檔案 {filepath}: {e}")

