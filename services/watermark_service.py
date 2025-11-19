"""
水印服務統一介面
"""
from blind_watermark import WaterMark, att, recover
import os
import cv2
import numpy as np
from datetime import datetime


class WatermarkService:
    """水印服務統一介面"""
    
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def embed_blind_watermark(self, input_path, output_path, watermark_text, 
                             password_img=1, password_wm=1):
        """
        嵌入隱碼水印
        
        Args:
            input_path (str): 輸入圖像路徑
            output_path (str): 輸出圖像路徑
            watermark_text (str): 水印文字
            password_img (int): 圖像密碼
            password_wm (int): 水印密碼
        
        Returns:
            int: 水印位元長度
        """
        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        
        # 讀取圖像
        bwm.read_img(input_path)
        
        # 讀取水印
        bwm.read_wm(watermark_text, mode='str')
        
        # 嵌入水印
        bwm.embed(output_path)
        
        # 返回水印長度（提取時需要）
        wm_length = len(bwm.wm_bit)
        
        return wm_length
    
    def extract_blind_watermark(self, input_path, wm_length, 
                                password_img=1, password_wm=1):
        """
        提取隱碼水印
        
        Args:
            input_path (str): 帶水印的圖像路徑
            wm_length (int): 水印位元長度
            password_img (int): 圖像密碼
            password_wm (int): 水印密碼
        
        Returns:
            str: 提取的水印文字
        """
        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        
        # 提取水印
        extracted_text = bwm.extract(
            filename=input_path,
            wm_shape=wm_length,
            mode='str'
        )
        
        return extracted_text
    
    def apply_attack(self, input_path, output_path, attack_type, **kwargs):
        """
        應用攻擊測試
        
        Args:
            input_path (str): 輸入圖像路徑
            output_path (str): 輸出圖像路徑
            attack_type (str): 攻擊類型
                - 'cut': 裁剪+縮放
                - 'resize': 縮放
                - 'bright': 亮度調整
                - 'shelter': 遮擋
                - 'salt_pepper': 椒鹽噪聲
                - 'rot': 旋轉
            **kwargs: 攻擊參數
        
        Returns:
            str: 輸出圖像路徑
        """
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"無法讀取圖像: {input_path}")
        
        if attack_type == 'cut':
            # 裁剪+縮放
            loc_r = kwargs.get('loc_r', None)
            loc = kwargs.get('loc', None)
            scale = kwargs.get('scale', None)
            attacked_img = att.cut_att3(input_img=img, loc_r=loc_r, loc=loc, scale=scale)
        
        elif attack_type == 'resize':
            # 縮放
            out_shape = kwargs.get('out_shape', (500, 500))
            attacked_img = att.resize_att(input_img=img, out_shape=out_shape)
        
        elif attack_type == 'bright':
            # 亮度調整
            ratio = kwargs.get('ratio', 0.8)
            attacked_img = att.bright_att(input_img=img, ratio=ratio)
        
        elif attack_type == 'shelter':
            # 遮擋
            ratio = kwargs.get('ratio', 0.1)
            n = kwargs.get('n', 3)
            attacked_img = att.shelter_att(input_img=img, ratio=ratio, n=n)
        
        elif attack_type == 'salt_pepper':
            # 椒鹽噪聲
            ratio = kwargs.get('ratio', 0.01)
            attacked_img = att.salt_pepper_att(input_img=img, ratio=ratio)
        
        elif attack_type == 'rot':
            # 旋轉
            angle = kwargs.get('angle', 45)
            attacked_img = att.rot_att(input_img=img, angle=angle)
        
        else:
            raise ValueError(f"不支援的攻擊類型: {attack_type}")
        
        # 儲存攻擊後的圖像
        cv2.imwrite(output_path, attacked_img)
        return output_path
    
    def estimate_crop_parameters(self, original_path, template_path):
        """
        估算裁剪參數
        
        Args:
            original_path (str): 原始圖像路徑
            template_path (str): 攻擊後的圖像路徑
        
        Returns:
            dict: 包含 loc, shape, score, scale 的字典
        """
        loc, shape, score, scale = recover.estimate_crop_parameters(
            original_file=original_path,
            template_file=template_path
        )
        
        return {
            'loc': loc,
            'shape': shape,
            'score': float(score),
            'scale': float(scale)
        }
    
    def recover_crop(self, template_path, output_path, loc, image_o_shape):
        """
        恢復裁剪
        
        Args:
            template_path (str): 裁剪後的圖像路徑
            output_path (str): 輸出路徑
            loc (tuple): 裁剪位置 (x1, y1, x2, y2)
            image_o_shape (tuple): 原始圖像尺寸 (height, width)
        
        Returns:
            str: 輸出圖像路徑
        """
        recovered_img = recover.recover_crop(
            template_file=template_path,
            output_file_name=output_path,
            loc=loc,
            image_o_shape=image_o_shape
        )
        return output_path

