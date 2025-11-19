"""
Flask 主應用
雙重水印系統
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback
import time
from functools import wraps

# 自定義服務
from services.watermark_service import WatermarkService
from services.image_processor import ImageProcessor
from services.file_manager import FileManager
from services.logger_service import logger_service

# 初始化 Flask
app = Flask(__name__)
CORS(app)

# 配置
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

# 確保目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 初始化服務
watermark_service = WatermarkService(app.config['OUTPUT_FOLDER'])
image_processor = ImageProcessor()
file_manager = FileManager(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])


# ==================== 日誌裝飾器 ====================

def log_api_call(operation_type):
    """API 調用日誌裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            error_message = None
            
            try:
                result = func(*args, **kwargs)
                
                # 如果是 JSON 響應，檢查是否有錯誤
                if isinstance(result, tuple) and len(result) == 2:
                    response, code = result
                    status_code = code
                    if code >= 400:
                        if isinstance(response, dict) and 'error' in response:
                            error_message = response['error']
                elif hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                processing_time = (time.time() - start_time) * 1000  # 轉為毫秒
                
                # 記錄成功日誌
                logger_service.log_api_request(
                    operation_type=operation_type,
                    request=request,
                    status_code=status_code,
                    error_message=error_message,
                    processing_time=round(processing_time, 2)
                )
                
                return result
                
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                error_message = str(e)
                
                # 記錄錯誤日誌
                logger_service.log_error(
                    error_type=type(e).__name__,
                    error_message=error_message,
                    request=request,
                    operation_type=operation_type,
                    processing_time=round(processing_time, 2),
                    traceback=traceback.format_exc()
                )
                
                # 重新拋出異常
                raise
        
        return wrapper
    return decorator


# ==================== 路由 ====================

@app.route('/')
def index():
    """首頁"""
    logger_service.log_page_view('index', request)
    return render_template('index.html')


@app.route('/webpage')
def webpage_watermark():
    """網頁水印展示頁"""
    logger_service.log_page_view('webpage', request)
    return render_template('webpage.html')


@app.route('/image-visible')
def image_visible_watermark():
    """圖像明碼水印頁"""
    logger_service.log_page_view('image_visible', request)
    return render_template('image_visible.html')


@app.route('/image-blind')
def image_blind_watermark():
    """圖像隱碼水印頁"""
    logger_service.log_page_view('image_blind', request)
    return render_template('image_blind.html')


# ==================== API 端點 ====================

@app.route('/api/image/visible/embed', methods=['POST'])
@log_api_call('embed_visible')
def embed_visible_watermark():
    """
    嵌入明碼水印（圖像）
    
    參數:
        file: 上傳的圖像
        text: 水印文字
        position: 位置 (topleft, topright, center, bottomleft, bottomright)
        opacity: 透明度 (0-100)
        font_size: 字體大小
        color: 顏色 (hex)
    """
    try:
        # 檢查文件
        if 'file' not in request.files:
            return jsonify({'error': '未上傳文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名為空'}), 400
        
        if not file_manager.allowed_file(file.filename):
            return jsonify({'error': '不支援的文件格式'}), 400
        
        # 儲存上傳文件
        input_path = file_manager.save_upload(file)
        
        # 獲取參數
        watermark_text = request.form.get('text', '機密文件')
        position = request.form.get('position', 'grid')  # 預設為網格模式
        opacity = int(request.form.get('opacity', 50))
        font_size = int(request.form.get('font_size', 36))
        color = request.form.get('color', '#000000')
        
        # 網格水印參數
        watermark_x = int(request.form.get('watermark_x', 20))
        watermark_y = int(request.form.get('watermark_y', 20))
        watermark_rows = int(request.form.get('watermark_rows', 0))
        watermark_cols = int(request.form.get('watermark_cols', 0))
        watermark_x_space = int(request.form.get('watermark_x_space', 50))
        watermark_y_space = int(request.form.get('watermark_y_space', 50))
        watermark_angle = int(request.form.get('watermark_angle', 0))
        watermark_font = request.form.get('watermark_font', '微軟雅黑')
        watermark_width = request.form.get('watermark_width')
        watermark_width = int(watermark_width) if watermark_width else None
        watermark_height = request.form.get('watermark_height')
        watermark_height = int(watermark_height) if watermark_height else None
        
        # 處理圖像
        output_filename = f"visible_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        image_processor.add_visible_watermark(
            input_path=input_path,
            output_path=output_path,
            text=watermark_text,
            position=position,
            opacity=opacity,
            font_size=font_size,
            color=color,
            watermark_x=watermark_x,
            watermark_y=watermark_y,
            watermark_rows=watermark_rows,
            watermark_cols=watermark_cols,
            watermark_x_space=watermark_x_space,
            watermark_y_space=watermark_y_space,
            watermark_angle=watermark_angle,
            watermark_font=watermark_font,
            watermark_width=watermark_width,
            watermark_height=watermark_height
        )
        
        # 記錄額外資訊
        logger_service.log_operation(
            operation_type='embed_visible',
            description=f'嵌入明碼水印成功: {watermark_text}',
            ip_address=request.remote_addr,
            method=request.method,
            path=request.path,
            status_code=200,
            extra_info={
                'text': watermark_text,
                'position': position,
                'opacity': opacity,
                'font_size': font_size,
                'output_file': output_filename
            }
        )
        
        return jsonify({
            'success': True,
            'output_path': f'/output/{output_filename}',
            'message': '明碼水印嵌入成功'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in embed_visible_watermark: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='embed_visible',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/api/image/blind/embed', methods=['POST'])
@log_api_call('embed_blind')
def embed_blind_watermark():
    """
    嵌入隱碼水印
    
    參數:
        file: 上傳的圖像
        watermark: 水印文字
        password_img: 圖像密碼
        password_wm: 水印密碼
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上傳文件'}), 400
        
        file = request.files['file']
        if not file_manager.allowed_file(file.filename):
            return jsonify({'error': '不支援的文件格式'}), 400
        
        # 儲存上傳文件
        input_path = file_manager.save_upload(file)
        
        # 獲取參數
        watermark_text = request.form.get('watermark', 'BlindWatermark')
        password_img = int(request.form.get('password_img', 1))
        password_wm = int(request.form.get('password_wm', 1))
        
        # 嵌入水印
        output_filename = f"blind_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        wm_length = watermark_service.embed_blind_watermark(
            input_path=input_path,
            output_path=output_path,
            watermark_text=watermark_text,
            password_img=password_img,
            password_wm=password_wm
        )
        
        # 記錄額外資訊
        logger_service.log_operation(
            operation_type='embed_blind',
            description=f'嵌入隱碼水印成功: {watermark_text[:20]}...',
            ip_address=request.remote_addr,
            method=request.method,
            path=request.path,
            status_code=200,
            extra_info={
                'watermark_length': len(watermark_text),
                'wm_length': wm_length,
                'output_file': output_filename
            }
        )
        
        return jsonify({
            'success': True,
            'output_path': f'/output/{output_filename}',
            'wm_length': wm_length,
            'message': '隱碼水印嵌入成功'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in embed_blind_watermark: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='embed_blind',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/api/image/blind/extract', methods=['POST'])
@log_api_call('extract_blind')
def extract_blind_watermark():
    """
    提取隱碼水印
    
    參數:
        file: 帶水印的圖像
        wm_length: 水印位元長度
        password_img: 圖像密碼
        password_wm: 水印密碼
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上傳文件'}), 400
        
        file = request.files['file']
        input_path = file_manager.save_upload(file)
        
        # 獲取參數
        wm_length = int(request.form.get('wm_length'))
        password_img = int(request.form.get('password_img', 1))
        password_wm = int(request.form.get('password_wm', 1))
        
        # 提取水印
        extracted_text = watermark_service.extract_blind_watermark(
            input_path=input_path,
            wm_length=wm_length,
            password_img=password_img,
            password_wm=password_wm
        )
        
        # 記錄額外資訊
        logger_service.log_operation(
            operation_type='extract_blind',
            description=f'提取隱碼水印成功: {extracted_text[:20] if extracted_text else "空"}...',
            ip_address=request.remote_addr,
            method=request.method,
            path=request.path,
            status_code=200,
            extra_info={
                'wm_length': wm_length,
                'extracted_length': len(extracted_text) if extracted_text else 0
            }
        )
        
        return jsonify({
            'success': True,
            'watermark': extracted_text,
            'message': '隱碼水印提取成功'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in extract_blind_watermark: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='extract_blind',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/api/image/blind/attack', methods=['POST'])
@log_api_call('attack')
def apply_attack():
    """
    應用攻擊測試
    
    參數:
        file: 帶水印的圖像
        attack_type: 攻擊類型 (cut, resize, bright, shelter, salt_pepper, rot)
        其他參數根據攻擊類型而定
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上傳文件'}), 400
        
        file = request.files['file']
        if not file_manager.allowed_file(file.filename):
            return jsonify({'error': '不支援的文件格式'}), 400
        
        # 儲存上傳文件
        input_path = file_manager.save_upload(file)
        
        # 獲取攻擊類型
        attack_type = request.form.get('attack_type')
        if not attack_type:
            return jsonify({'error': '未指定攻擊類型'}), 400
        
        # 準備攻擊參數
        attack_params = {}
        
        if attack_type == 'cut':
            # 裁剪+縮放
            if request.form.get('loc_r_x1'):
                attack_params['loc_r'] = (
                    (float(request.form.get('loc_r_x1', 0)), float(request.form.get('loc_r_y1', 0))),
                    (float(request.form.get('loc_r_x2', 1)), float(request.form.get('loc_r_y2', 1)))
                )
            if request.form.get('scale'):
                attack_params['scale'] = float(request.form.get('scale'))
        
        elif attack_type == 'resize':
            # 縮放
            width = int(request.form.get('width', 500))
            height = int(request.form.get('height', 500))
            attack_params['out_shape'] = (width, height)
        
        elif attack_type == 'bright':
            # 亮度調整
            attack_params['ratio'] = float(request.form.get('ratio', 0.8))
        
        elif attack_type == 'shelter':
            # 遮擋
            attack_params['ratio'] = float(request.form.get('ratio', 0.1))
            attack_params['n'] = int(request.form.get('n', 3))
        
        elif attack_type == 'salt_pepper':
            # 椒鹽噪聲
            attack_params['ratio'] = float(request.form.get('ratio', 0.01))
        
        elif attack_type == 'rot':
            # 旋轉
            attack_params['angle'] = float(request.form.get('angle', 45))
        
        else:
            return jsonify({'error': f'不支援的攻擊類型: {attack_type}'}), 400
        
        # 應用攻擊
        output_filename = f"attacked_{attack_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        watermark_service.apply_attack(
            input_path=input_path,
            output_path=output_path,
            attack_type=attack_type,
            **attack_params
        )
        
        # 記錄額外資訊
        logger_service.log_operation(
            operation_type='attack',
            description=f'攻擊測試完成: {attack_type}',
            ip_address=request.remote_addr,
            method=request.method,
            path=request.path,
            status_code=200,
            extra_info={
                'attack_type': attack_type,
                'attack_params': attack_params,
                'output_file': output_filename
            }
        )
        
        return jsonify({
            'success': True,
            'output_path': f'/output/{output_filename}',
            'attack_type': attack_type,
            'message': '攻擊測試完成'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in apply_attack: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='attack',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/api/image/blind/estimate_crop', methods=['POST'])
@log_api_call('estimate_crop')
def estimate_crop():
    """
    估算裁剪參數
    """
    try:
        if 'original' not in request.files or 'template' not in request.files:
            return jsonify({'error': '需要上傳原始圖像和模板圖像'}), 400
        
        original_file = request.files['original']
        template_file = request.files['template']
        
        # 儲存文件
        original_path = file_manager.save_upload(original_file)
        template_path = file_manager.save_upload(template_file)
        
        # 估算參數
        result = watermark_service.estimate_crop_parameters(
            original_path=original_path,
            template_path=template_path
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'message': '參數估算完成'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in estimate_crop: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='estimate_crop',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/api/image/blind/recover_crop', methods=['POST'])
@log_api_call('recover_crop')
def recover_crop():
    """
    恢復裁剪
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未上傳文件'}), 400
        
        file = request.files['file']
        input_path = file_manager.save_upload(file)
        
        # 獲取參數
        loc = (
            int(request.form.get('x1')),
            int(request.form.get('y1')),
            int(request.form.get('x2')),
            int(request.form.get('y2'))
        )
        image_o_shape = (
            int(request.form.get('height')),
            int(request.form.get('width'))
        )
        
        # 恢復
        output_filename = f"recovered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        watermark_service.recover_crop(
            template_path=input_path,
            output_path=output_path,
            loc=loc,
            image_o_shape=image_o_shape
        )
        
        return jsonify({
            'success': True,
            'output_path': f'/output/{output_filename}',
            'message': '裁剪恢復完成'
        })
    
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Error in recover_crop: {traceback.format_exc()}")
        logger_service.log_error(
            error_type=type(e).__name__,
            error_message=error_msg,
            request=request,
            operation_type='recover_crop',
            traceback=traceback.format_exc()
        )
        return jsonify({'error': error_msg}), 500


@app.route('/output/<filename>')
def serve_output(filename):
    """提供輸出文件下載"""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404


# ==================== 錯誤處理 ====================

@app.errorhandler(413)
def request_entity_too_large(error):
    logger_service.log_error(
        error_type='RequestEntityTooLarge',
        error_message='文件過大，最大支援 16MB',
        request=request
    )
    return jsonify({'error': '文件過大，最大支援 16MB'}), 413


@app.errorhandler(404)
def not_found(error):
    logger_service.log_error(
        error_type='NotFound',
        error_message='頁面不存在',
        request=request
    )
    return jsonify({'error': '頁面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger_service.log_error(
        error_type='InternalServerError',
        error_message='伺服器內部錯誤',
        request=request,
        traceback=traceback.format_exc()
    )
    return jsonify({'error': '伺服器內部錯誤'}), 500


# ==================== 啟動應用 ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

