"""
圖像處理服務
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math


class ImageProcessor:
    """圖像處理服務"""
    
    def add_visible_watermark(self, input_path, output_path, text, 
                             position='bottomright', opacity=50, 
                             font_size=36, color='#000000',
                             watermark_x=20, watermark_y=20,
                             watermark_rows=0, watermark_cols=0,
                             watermark_x_space=50, watermark_y_space=50,
                             watermark_angle=0, watermark_font='微軟雅黑',
                             watermark_width=None, watermark_height=None):
        """
        添加明碼文字浮水印（支援多個浮水印網格排列）
        
        Args:
            input_path (str): 輸入圖像路徑
            output_path (str): 輸出圖像路徑
            text (str): 浮水印文字
            position (str): 位置模式 (single: 單個位置, grid: 網格)
            opacity (int): 透明度 (0-100)
            font_size (int): 字體大小
            color (str): 顏色 (hex)
            watermark_x (int): 起始 X 座標
            watermark_y (int): 起始 Y 座標
            watermark_rows (int): 行數 (0=自動計算)
            watermark_cols (int): 列數 (0=自動計算)
            watermark_x_space (int): X 軸間隔
            watermark_y_space (int): Y 軸間隔
            watermark_angle (int): 旋轉角度 (度)
            watermark_font (str): 字體名稱
            watermark_width (int): 浮水印寬度 (None=自動)
            watermark_height (int): 浮水印高度 (None=自動)
        """
        # 開啟圖像
        image = Image.open(input_path).convert('RGBA')
        img_width, img_height = image.size
        
        # 建立透明圖層
        watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 載入字體
        font = self._get_font(font_size, watermark_font)
        
        # 計算文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 使用指定的寬高或文字尺寸
        wm_width = watermark_width if watermark_width else text_width
        wm_height = watermark_height if watermark_height else text_height
        
        # 解析顏色
        rgb = self._hex_to_rgb(color)
        alpha = int(255 * opacity / 100)
        text_color = (*rgb, alpha)
        
        # 判斷是單個浮水印還是網格浮水印
        if position in ['topleft', 'topright', 'center', 'bottomleft', 'bottomright']:
            # 單個浮水印模式（向後兼容）
            x, y = self._calculate_position(
                position, img_width, img_height, 
                text_width, text_height
            )
            self._draw_watermark_text(watermark_layer, draw, text, x, y, font, text_color, watermark_angle, text_width, text_height)
        else:
            # 網格浮水印模式
            # 計算可用的空間
            available_width = img_width - watermark_x
            available_height = img_height - watermark_y
            
            # 計算行數和列數（如果為0則自動計算）
            if watermark_cols == 0:
                watermark_cols = max(1, int((available_width) / (wm_width + watermark_x_space)))
            if watermark_rows == 0:
                watermark_rows = max(1, int((available_height) / (wm_height + watermark_y_space)))
            
            # 繪製網格浮水印
            for row in range(watermark_rows):
                for col in range(watermark_cols):
                    x = watermark_x + col * (wm_width + watermark_x_space)
                    y = watermark_y + row * (wm_height + watermark_y_space)
                    
                    # 檢查是否超出圖像範圍
                    if x + wm_width <= img_width and y + wm_height <= img_height:
                        self._draw_watermark_text(watermark_layer, draw, text, x, y, font, text_color, watermark_angle, text_width, text_height)
        
        # 合併圖層
        watermarked = Image.alpha_composite(image, watermark_layer)
        
        # 轉換為 RGB 並儲存
        watermarked = watermarked.convert('RGB')
        watermarked.save(output_path)
    
    def _draw_watermark_text(self, watermark_layer, draw, text, x, y, font, color, angle, text_width, text_height):
        """繪製帶旋轉的浮水印文字"""
        if angle == 0:
            # 無旋轉，直接繪製
            draw.text((x, y), text, font=font, fill=color)
        else:
            # 需要旋轉：創建臨時圖像
            # 計算所需尺寸（考慮旋轉）
            margin = int(math.sqrt(text_width**2 + text_height**2)) + 50
            temp_size = max(text_width, text_height) + margin * 2
            
            # 創建臨時圖像
            temp_img = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 在臨時圖像中心繪製文字
            temp_x = (temp_size - text_width) // 2
            temp_y = (temp_size - text_height) // 2
            temp_draw.text((temp_x, temp_y), text, font=font, fill=color)
            
            # 旋轉臨時圖像（注意：PIL 的 rotate 角度是逆時針，我們需要取負）
            rotated = temp_img.rotate(-angle, expand=False, center=(temp_size//2, temp_size//2))
            
            # 計算貼圖位置（使旋轉後的文字中心對齊原位置）
            center_x = x + text_width // 2
            center_y = y + text_height // 2
            paste_x = center_x - temp_size // 2
            paste_y = center_y - temp_size // 2
            
            # 將旋轉後的圖像合成到浮水印圖層
            watermark_layer.paste(rotated, (paste_x, paste_y), rotated)
    
    def _get_font(self, font_size, font_name=None):
        """獲取字體"""
        # 如果指定了字體名稱，優先嘗試
        if font_name:
            font_paths_by_name = {
                '微軟雅黑': ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/msyhbd.ttc'],
                'arial': ['C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'],
                'times': ['C:/Windows/Fonts/times.ttf'],
            }
            if font_name in font_paths_by_name:
                for font_path in font_paths_by_name[font_name]:
                    if os.path.exists(font_path):
                        try:
                            return ImageFont.truetype(font_path, font_size)
                        except:
                            continue
        
        # 嘗試載入系統字體
        font_paths = [
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/msyh.ttc',  # 微軟雅黑
            'C:/Windows/Fonts/simsun.ttc',  # 宋體
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            # Mac
            '/System/Library/Fonts/Helvetica.ttc',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
        
        # 如果都失敗，使用預設字體
        return ImageFont.load_default()
    
    def _calculate_position(self, position, img_width, img_height, 
                           text_width, text_height):
        """計算浮水印位置"""
        padding = 20
        
        positions = {
            'topleft': (padding, padding),
            'topright': (img_width - text_width - padding, padding),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'bottomleft': (padding, img_height - text_height - padding),
            'bottomright': (img_width - text_width - padding, img_height - text_height - padding)
        }
        
        return positions.get(position, positions['bottomright'])
    
    def _hex_to_rgb(self, hex_color):
        """十六進制顏色轉 RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
