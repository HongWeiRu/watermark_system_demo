"""
水印服務統一介面
使用 blind_watermark 庫實現隱碼水印功能
"""
from blind_watermark import WaterMark, att, recover
import os
import cv2
import numpy as np
from datetime import datetime
import logging

# 設置日誌
logger = logging.getLogger(__name__)


class WatermarkService:
    """水印服務統一介面"""
    
    def __init__(self, output_dir='output'):
        """
        初始化水印服務
        
        Args:
            output_dir (str): 輸出目錄路徑
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"水印服務初始化完成，輸出目錄: {output_dir}")
    
    def embed_blind_watermark(self, input_path, output_path, watermark_text, 
                             password_img=1, password_wm=1):
        """
        嵌入隱碼水印
        
        Args:
            input_path (str): 輸入圖像路徑
            output_path (str): 輸出圖像路徑
            watermark_text (str): 水印文字
            password_img (int): 圖像密碼，用於加密圖像
            password_wm (int): 水印密碼，用於加密水印
        
        Returns:
            int: 水印位元長度（提取時需要此參數）
        
        Raises:
            FileNotFoundError: 輸入圖像文件不存在
            ValueError: 參數無效
            Exception: 其他嵌入過程中的錯誤
        """
        try:
            # 驗證輸入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"輸入圖像文件不存在: {input_path}")
            
            # 驗證水印文字
            if not watermark_text or not isinstance(watermark_text, str):
                raise ValueError("水印文字必須是非空字符串")
            
            # 驗證密碼參數
            if not isinstance(password_img, int) or password_img < 1:
                raise ValueError("圖像密碼必須是大於0的整數")
            if not isinstance(password_wm, int) or password_wm < 1:
                raise ValueError("水印密碼必須是大於0的整數")
            
            logger.info(f"開始嵌入水印: 輸入={input_path}, 輸出={output_path}, 水印長度={len(watermark_text)}")
            
            # 創建 WaterMark 實例
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)
            
            # 讀取圖像
            bwm.read_img(input_path)
            logger.debug(f"圖像讀取成功: {input_path}")
            
            # 讀取水印文字
            bwm.read_wm(watermark_text, mode='str')
            logger.debug(f"水印文字讀取成功，長度: {len(watermark_text)}")
            
            # 嵌入水印
            bwm.embed(output_path)
            logger.info(f"水印嵌入成功: {output_path}")
            
            # 獲取水印位元長度（提取時需要）
            wm_length = len(bwm.wm_bit)
            logger.info(f"水印位元長度: {wm_length}")
            
            return wm_length
            
        except FileNotFoundError as e:
            logger.error(f"文件未找到錯誤: {e}")
            raise
        except ValueError as e:
            logger.error(f"參數驗證錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"嵌入水印時發生未知錯誤: {e}", exc_info=True)
            raise Exception(f"嵌入水印失敗: {str(e)}")
    
    def extract_blind_watermark(self, input_path, wm_length, 
                                password_img=1, password_wm=1):
        """
        提取隱碼水印
        
        Args:
            input_path (str): 帶水印的圖像路徑
            wm_length (int): 水印位元長度（必須與嵌入時一致）
            password_img (int): 圖像密碼（必須與嵌入時一致）
            password_wm (int): 水印密碼（必須與嵌入時一致）
        
        Returns:
            str: 提取的水印文字
        
        Raises:
            FileNotFoundError: 輸入圖像文件不存在
            ValueError: 參數無效
            Exception: 其他提取過程中的錯誤
        """
        try:
            # 驗證輸入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"輸入圖像文件不存在: {input_path}")
            
            # 驗證水印長度
            if not isinstance(wm_length, int) or wm_length <= 0:
                raise ValueError("水印長度必須是大於0的整數")
            
            # 驗證密碼參數
            if not isinstance(password_img, int) or password_img < 1:
                raise ValueError("圖像密碼必須是大於0的整數")
            if not isinstance(password_wm, int) or password_wm < 1:
                raise ValueError("水印密碼必須是大於0的整數")
            
            logger.info(f"開始提取水印: 輸入={input_path}, 水印長度={wm_length}")
            
            # 創建 WaterMark 實例（必須使用與嵌入時相同的密碼）
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)
            
            # 提取水印
            extracted_text = bwm.extract(
                filename=input_path,
                wm_shape=wm_length,
                mode='str'
            )
            
            logger.info(f"水印提取成功，提取長度: {len(extracted_text) if extracted_text else 0}")
            
            return extracted_text
            
        except FileNotFoundError as e:
            logger.error(f"文件未找到錯誤: {e}")
            raise
        except ValueError as e:
            logger.error(f"參數驗證錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"提取水印時發生未知錯誤: {e}", exc_info=True)
            raise Exception(f"提取水印失敗: {str(e)}")
    
    def apply_attack(self, input_path, output_path, attack_type, **kwargs):
        """
        應用攻擊測試
        
        支援的攻擊類型:
        - 'cut': 裁剪+縮放攻擊 (cut_att3)
        - 'resize': 縮放攻擊 (resize_att)
        - 'bright': 亮度調整攻擊 (bright_att)
        - 'shelter': 遮擋攻擊 (shelter_att)
        - 'salt_pepper': 椒鹽噪聲攻擊 (salt_pepper_att)
        - 'rot': 旋轉攻擊 (rot_att)
        
        Args:
            input_path (str): 輸入圖像路徑（帶水印的圖像）
            output_path (str): 輸出圖像路徑（攻擊後的圖像）
            attack_type (str): 攻擊類型
            **kwargs: 攻擊參數
                - cut: loc_r (tuple), loc (tuple), scale (float)
                - resize: out_shape (tuple)
                - bright: ratio (float)
                - shelter: ratio (float), n (int)
                - salt_pepper: ratio (float)
                - rot: angle (float)
        
        Returns:
            str: 輸出圖像路徑
        
        Raises:
            FileNotFoundError: 輸入圖像文件不存在
            ValueError: 攻擊類型不支援或參數無效
            Exception: 其他攻擊過程中的錯誤
        """
        try:
            # 驗證輸入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"輸入圖像文件不存在: {input_path}")
            
            # 讀取圖像
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError(f"無法讀取圖像: {input_path}，請確認文件格式是否正確")
            
            logger.info(f"開始應用攻擊: 類型={attack_type}, 輸入={input_path}, 輸出={output_path}")
            
            # 根據攻擊類型應用不同的攻擊
            if attack_type == 'cut':
                # 裁剪+縮放攻擊 (cut_att3)
                loc_r = kwargs.get('loc_r', None)
                loc = kwargs.get('loc', None)
                scale = kwargs.get('scale', None)
                
                logger.debug(f"裁剪+縮放參數: loc_r={loc_r}, loc={loc}, scale={scale}")
                attacked_img = att.cut_att3(input_img=img, loc_r=loc_r, loc=loc, scale=scale)
                
            elif attack_type == 'resize':
                # 縮放攻擊 (resize_att)
                out_shape = kwargs.get('out_shape', (500, 500))
                if not isinstance(out_shape, (tuple, list)) or len(out_shape) != 2:
                    raise ValueError("out_shape 必須是包含兩個元素的元組或列表 (width, height)")
                
                logger.debug(f"縮放參數: out_shape={out_shape}")
                attacked_img = att.resize_att(input_img=img, out_shape=out_shape)
                
            elif attack_type == 'bright':
                # 亮度調整攻擊 (bright_att)
                ratio = kwargs.get('ratio', 0.8)
                if not isinstance(ratio, (int, float)) or ratio <= 0:
                    raise ValueError("亮度比例必須是大於0的數值")
                
                logger.debug(f"亮度調整參數: ratio={ratio}")
                attacked_img = att.bright_att(input_img=img, ratio=ratio)
                
            elif attack_type == 'shelter':
                # 遮擋攻擊 (shelter_att)
                ratio = kwargs.get('ratio', 0.1)
                n = kwargs.get('n', 3)
                
                if not isinstance(ratio, (int, float)) or ratio <= 0 or ratio > 1:
                    raise ValueError("遮擋比例必須是0到1之間的數值")
                if not isinstance(n, int) or n < 1:
                    raise ValueError("遮擋塊數量必須是大於0的整數")
                
                logger.debug(f"遮擋參數: ratio={ratio}, n={n}")
                attacked_img = att.shelter_att(input_img=img, ratio=ratio, n=n)
                
            elif attack_type == 'salt_pepper':
                # 椒鹽噪聲攻擊 (salt_pepper_att)
                ratio = kwargs.get('ratio', 0.01)
                if not isinstance(ratio, (int, float)) or ratio <= 0 or ratio > 1:
                    raise ValueError("噪聲比例必須是0到1之間的數值")
                
                logger.debug(f"椒鹽噪聲參數: ratio={ratio}")
                attacked_img = att.salt_pepper_att(input_img=img, ratio=ratio)
                
            elif attack_type == 'rot':
                # 旋轉攻擊 (rot_att)
                angle = kwargs.get('angle', 45)
                if not isinstance(angle, (int, float)):
                    raise ValueError("旋轉角度必須是數值")
                
                logger.debug(f"旋轉參數: angle={angle}")
                attacked_img = att.rot_att(input_img=img, angle=angle)
                
            else:
                raise ValueError(f"不支援的攻擊類型: {attack_type}。支援的類型: cut, resize, bright, shelter, salt_pepper, rot")
            
            # 驗證攻擊後的圖像
            if attacked_img is None or attacked_img.size == 0:
                raise ValueError(f"攻擊後圖像為空，攻擊類型: {attack_type}")
            
            # 儲存攻擊後的圖像
            success = cv2.imwrite(output_path, attacked_img)
            if not success:
                raise IOError(f"無法儲存攻擊後的圖像: {output_path}")
            
            logger.info(f"攻擊測試完成: {output_path}")
            
            return output_path
            
        except FileNotFoundError as e:
            logger.error(f"文件未找到錯誤: {e}")
            raise
        except ValueError as e:
            logger.error(f"參數驗證錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"應用攻擊時發生未知錯誤: {e}", exc_info=True)
            raise Exception(f"應用攻擊失敗: {str(e)}")
    
    def estimate_crop_parameters(self, original_path, template_path):
        """
        估算裁剪參數
        
        用於恢復裁剪攻擊，估算裁剪位置和縮放比例
        
        Args:
            original_path (str): 原始圖像路徑
            template_path (str): 攻擊後的圖像路徑（裁剪後的圖像）
        
        Returns:
            dict: 包含 loc, shape, score, scale 的字典
                - loc: 裁剪位置
                - shape: 形狀
                - score: 匹配分數
                - scale: 縮放比例
        
        Raises:
            FileNotFoundError: 輸入文件不存在
            Exception: 估算過程中的錯誤
        """
        try:
            if not os.path.exists(original_path):
                raise FileNotFoundError(f"原始圖像文件不存在: {original_path}")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"模板圖像文件不存在: {template_path}")
            
            logger.info(f"開始估算裁剪參數: 原始={original_path}, 模板={template_path}")
            
            loc, shape, score, scale = recover.estimate_crop_parameters(
                original_file=original_path,
                template_file=template_path
            )
            
            result = {
                'loc': loc,
                'shape': shape,
                'score': float(score),
                'scale': float(scale)
            }
            
            logger.info(f"裁剪參數估算完成: loc={loc}, scale={scale}, score={score}")
            
            return result
            
        except FileNotFoundError as e:
            logger.error(f"文件未找到錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"估算裁剪參數時發生錯誤: {e}", exc_info=True)
            raise Exception(f"估算裁剪參數失敗: {str(e)}")
    
    def recover_crop(self, template_path, output_path, loc, image_o_shape):
        """
        恢復裁剪
        
        根據估算的裁剪參數恢復原始圖像尺寸
        
        Args:
            template_path (str): 裁剪後的圖像路徑
            output_path (str): 恢復後的圖像輸出路徑
            loc (tuple): 裁剪位置 (x1, y1, x2, y2)
            image_o_shape (tuple): 原始圖像尺寸 (height, width)
        
        Returns:
            str: 輸出圖像路徑
        
        Raises:
            FileNotFoundError: 輸入文件不存在
            ValueError: 參數無效
            Exception: 恢復過程中的錯誤
        """
        try:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"模板圖像文件不存在: {template_path}")
            
            if not isinstance(loc, (tuple, list)) or len(loc) != 4:
                raise ValueError("裁剪位置 loc 必須是包含4個元素的元組或列表 (x1, y1, x2, y2)")
            
            if not isinstance(image_o_shape, (tuple, list)) or len(image_o_shape) != 2:
                raise ValueError("原始圖像尺寸 image_o_shape 必須是包含2個元素的元組或列表 (height, width)")
            
            logger.info(f"開始恢復裁剪: 模板={template_path}, loc={loc}, shape={image_o_shape}")
            
            recovered_img = recover.recover_crop(
                template_file=template_path,
                output_file_name=output_path,
                loc=loc,
                image_o_shape=image_o_shape
            )
            
            logger.info(f"裁剪恢復完成: {output_path}")
            
            return output_path
            
        except FileNotFoundError as e:
            logger.error(f"文件未找到錯誤: {e}")
            raise
        except ValueError as e:
            logger.error(f"參數驗證錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"恢復裁剪時發生錯誤: {e}", exc_info=True)
            raise Exception(f"恢復裁剪失敗: {str(e)}")
