/**
 * 雙重浮水印系統 - 主要前端邏輯
 */

// 初始化零寬字符浮水印引擎
const zwm = new ZeroWidthWatermark();

/**
 * 網頁浮水印功能
 */
const WebpageWatermark = {
  // 套用網頁明碼浮水印
  applyVisible: function(config) {
    if (typeof watermark === 'undefined') {
      console.error('watermark.js 未載入');
      return;
    }
    
    // 構建完整的配置對象，使用提供的參數或預設值
    const watermarkConfig = {
      watermark_id: config.watermark_id || 'wm_div_id',
      watermark_prefix: config.watermark_prefix || 'mask_div_id',
      watermark_txt: config.watermark_txt || "測試浮水印",
      watermark_x: config.watermark_x !== undefined ? config.watermark_x : 20,
      watermark_y: config.watermark_y !== undefined ? config.watermark_y : 20,
      watermark_rows: config.watermark_rows !== undefined ? config.watermark_rows : 0,
      watermark_cols: config.watermark_cols !== undefined ? config.watermark_cols : 0,
      watermark_x_space: config.watermark_x_space !== undefined ? config.watermark_x_space : 50,
      watermark_y_space: config.watermark_y_space !== undefined ? config.watermark_y_space : 50,
      watermark_font: config.watermark_font || '微軟雅黑',
      watermark_color: config.watermark_color || 'black',
      watermark_fontsize: config.watermark_fontsize || '18px',
      watermark_alpha: config.watermark_alpha !== undefined ? config.watermark_alpha : 0.15,
      watermark_width: config.watermark_width !== undefined ? config.watermark_width : 100,
      watermark_height: config.watermark_height !== undefined ? config.watermark_height : 100,
      watermark_angle: config.watermark_angle !== undefined ? config.watermark_angle : 15,
      watermark_parent_width: config.watermark_parent_width !== undefined ? config.watermark_parent_width : 0,
      watermark_parent_height: config.watermark_parent_height !== undefined ? config.watermark_parent_height : 0,
      watermark_parent_node: config.watermark_parent_node || null,
      monitor: config.monitor !== undefined ? config.monitor : true
    };
    
    watermark.load(watermarkConfig);
  },
  
  // 移除網頁明碼浮水印
  removeVisible: function() {
    try {
      // 使用 watermark.js 的 remove 方法
      if (typeof watermark !== 'undefined' && typeof watermark.remove === 'function') {
        watermark.remove();
      }
      
      // 手動移除浮水印元素（作為備用方案）
      // 查找所有可能的浮水印容器
      const possibleIds = ['wm_div_id', 'watermark_div'];
      possibleIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
          // 處理 Shadow DOM
          if (element.shadowRoot) {
            while (element.shadowRoot.firstChild) {
              element.shadowRoot.removeChild(element.shadowRoot.firstChild);
            }
          }
          if (element.parentNode) {
            element.parentNode.removeChild(element);
          } else {
            element.remove();
          }
        }
      });
      
      // 移除所有以 mask_div_id 開頭的元素
      const prefixElements = document.querySelectorAll('[id^="mask_div_id"]');
      prefixElements.forEach(el => {
        if (el.parentNode) {
          el.parentNode.removeChild(el);
        } else {
          el.remove();
        }
      });
      
      return true;
    } catch (error) {
      console.error('移除浮水印時發生錯誤:', error);
      return false;
    }
  },
  
  // 套用網頁隱碼浮水印
  applyInvisible: function(text, selector = 'p, h1, h2, h3, div') {
    zwm.embedIntoPage(selector, text);
    console.log('隱碼浮水印已嵌入:', text);
  },
  
  // 提取網頁隱碼浮水印
  extractInvisible: function() {
    const extracted = zwm.extractFromPage();
    console.log('提取的隱碼浮水印:', extracted);
    return extracted;
  }
};

/**
 * 圖像浮水印功能
 */
const ImageWatermark = {
  // 嵌入明碼浮水印
  embedVisible: async function(file, options) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('text', options.text || '機密文件');
    formData.append('position', options.position || 'grid');
    formData.append('opacity', options.opacity || 50);
    formData.append('font_size', options.font_size || 36);
    formData.append('color', options.color || '#000000');
    
    // 網格浮水印參數
    if (options.watermark_x !== undefined) formData.append('watermark_x', options.watermark_x);
    if (options.watermark_y !== undefined) formData.append('watermark_y', options.watermark_y);
    if (options.watermark_rows !== undefined) formData.append('watermark_rows', options.watermark_rows);
    if (options.watermark_cols !== undefined) formData.append('watermark_cols', options.watermark_cols);
    if (options.watermark_x_space !== undefined) formData.append('watermark_x_space', options.watermark_x_space);
    if (options.watermark_y_space !== undefined) formData.append('watermark_y_space', options.watermark_y_space);
    if (options.watermark_angle !== undefined) formData.append('watermark_angle', options.watermark_angle);
    if (options.watermark_font !== undefined) formData.append('watermark_font', options.watermark_font);
    if (options.watermark_width !== undefined) formData.append('watermark_width', options.watermark_width);
    if (options.watermark_height !== undefined) formData.append('watermark_height', options.watermark_height);
    
    const response = await fetch('/api/image/visible/embed', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '嵌入浮水印失敗');
    }
    
    const data = await response.json();
    return data.output_path;
  },
  
  // 嵌入隱碼浮水印
  embedBlind: async function(file, text, password_img = 1, password_wm = 1) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('watermark', text || 'SecretWatermark');
    formData.append('password_img', password_img);
    formData.append('password_wm', password_wm);
    
    const response = await fetch('/api/image/blind/embed', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '嵌入隱碼浮水印失敗');
    }
    
    const data = await response.json();
    return {
      output_path: data.output_path,
      wm_length: data.wm_length
    };
  },
  
  // 提取隱碼浮水印
  extractBlind: async function(file, length, password_img = 1, password_wm = 1) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('wm_length', length || 100);
    formData.append('password_img', password_img);
    formData.append('password_wm', password_wm);
    
    const response = await fetch('/api/image/blind/extract', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '提取隱碼浮水印失敗');
    }
    
    const data = await response.json();
    return data.watermark;
  },
  
  // 應用攻擊測試
  applyAttack: async function(file, attackType, params = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('attack_type', attackType);
    
    // 添加攻擊參數
    for (const key in params) {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        formData.append(key, params[key]);
      }
    }
    
    const response = await fetch('/api/image/blind/attack', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '攻擊測試失敗');
    }
    
    const data = await response.json();
    return data.output_path;
  },
  
  // 估算裁剪參數
  estimateCrop: async function(originalFile, templateFile) {
    const formData = new FormData();
    formData.append('original', originalFile);
    formData.append('template', templateFile);
    
    const response = await fetch('/api/image/blind/estimate_crop', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '估算裁剪參數失敗');
    }
    
    const data = await response.json();
    return data.result;
  },
  
  // 恢復裁剪
  recoverCrop: async function(templateFile, loc, imageShape) {
    const formData = new FormData();
    formData.append('file', templateFile);
    formData.append('x1', loc[0]);
    formData.append('y1', loc[1]);
    formData.append('x2', loc[2]);
    formData.append('y2', loc[3]);
    formData.append('width', imageShape[1]);
    formData.append('height', imageShape[0]);
    
    const response = await fetch('/api/image/blind/recover_crop', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '恢復裁剪失敗');
    }
    
    const data = await response.json();
    return data.output_path;
  }
};

/**
 * 工具函數
 */
const Utils = {
  // 顯示訊息
  showMessage: function(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 'alert-info';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.padding = '1rem 1.5rem';
    alertDiv.style.borderRadius = '8px';
    alertDiv.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    alertDiv.style.minWidth = '200px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
      alertDiv.style.opacity = '0';
      alertDiv.style.transition = 'opacity 0.3s';
      setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
  },
  
  // 下載檔案
  downloadFile: function(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
  
  // 讀取檔案為 DataURL
  readFileAsDataURL: function(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => resolve(e.target.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
};

// 匯出到全域
if (typeof window !== 'undefined') {
  window.WebpageWatermark = WebpageWatermark;
  window.ImageWatermark = ImageWatermark;
  window.Utils = Utils;
}

