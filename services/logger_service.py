"""
日誌服務
記錄使用者操作和系統錯誤
"""
import os
import csv
from datetime import datetime
from functools import wraps


class LoggerService:
    """日誌服務"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def _get_log_file_path(self):
        """獲取當天的日誌文件路徑"""
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"watermark_system_{today}.csv"
        return os.path.join(self.log_dir, filename)
    
    def _ensure_csv_header(self, filepath):
        """確保 CSV 文件有標題行"""
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    '時間戳', '操作類型', '操作描述', 'IP地址', 
                    '請求方法', '請求路徑', '狀態碼', '錯誤訊息', 
                    '處理時間(ms)', '額外資訊'
                ])
    
    def log_operation(self, operation_type, description, 
                     ip_address=None, method=None, path=None, 
                     status_code=200, error_message=None, 
                     processing_time=None, extra_info=None):
        """
        記錄操作日誌
        
        Args:
            operation_type (str): 操作類型
                - 'embed_visible': 嵌入明碼浮水印
                - 'embed_blind': 嵌入隱碼浮水印
                - 'extract_blind': 提取隱碼浮水印
                - 'attack': 攻擊測試
                - 'error': 錯誤
                - 'page_view': 頁面訪問
            description (str): 操作描述
            ip_address (str): 客戶端 IP
            method (str): HTTP 方法
            path (str): 請求路徑
            status_code (int): HTTP 狀態碼
            error_message (str): 錯誤訊息（如果有）
            processing_time (float): 處理時間（毫秒）
            extra_info (dict): 額外資訊（JSON 字符串）
        """
        try:
            filepath = self._get_log_file_path()
            self._ensure_csv_header(filepath)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # 將額外資訊轉為 JSON 字符串
            if extra_info and isinstance(extra_info, dict):
                import json
                extra_info_str = json.dumps(extra_info, ensure_ascii=False)
            else:
                extra_info_str = str(extra_info) if extra_info else ''
            
            # 寫入 CSV
            with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    operation_type,
                    description,
                    ip_address or '',
                    method or '',
                    path or '',
                    status_code,
                    error_message or '',
                    processing_time or '',
                    extra_info_str
                ])
        except Exception as e:
            # 日誌記錄失敗不應影響主程序
            print(f"日誌記錄失敗: {e}")
    
    def log_api_request(self, operation_type, request, status_code=200, 
                       error_message=None, processing_time=None, **kwargs):
        """記錄 API 請求"""
        ip_address = request.remote_addr if request else None
        method = request.method if request else None
        path = request.path if request else None
        
        # 構建描述
        description = f"{operation_type} - {path or 'unknown'}"
        
        # 構建額外資訊
        extra_info = {}
        if request and request.form:
            # 記錄表單參數（排除敏感資訊）
            for key, value in request.form.items():
                if key not in ['password', 'password_img', 'password_wm']:
                    extra_info[key] = str(value)[:100]  # 限制長度
        
        if kwargs:
            extra_info.update(kwargs)
        
        self.log_operation(
            operation_type=operation_type,
            description=description,
            ip_address=ip_address,
            method=method,
            path=path,
            status_code=status_code,
            error_message=error_message,
            processing_time=processing_time,
            extra_info=extra_info if extra_info else None
        )
    
    def log_error(self, error_type, error_message, request=None, **kwargs):
        """記錄錯誤"""
        self.log_api_request(
            operation_type='error',
            request=request,
            status_code=500,
            error_message=f"{error_type}: {error_message}",
            **kwargs
        )
    
    def log_page_view(self, page_name, request=None):
        """記錄頁面訪問"""
        self.log_api_request(
            operation_type='page_view',
            request=request,
            status_code=200,
            extra_info={'page': page_name}
        )


# 全域日誌服務實例
logger_service = LoggerService()

