/**
 * 零寬字符浮水印引擎
 * 用於網頁文本隱碼浮水印
 */
class ZeroWidthWatermark {
  constructor() {
    // 二進制編碼：0 和 1
    this.ZERO = '\u200B';  // 零寬空格 (0)
    this.ONE = '\u200C';   // 零寬不連字 (1)
  }
  
  /**
   * 將文字轉換為零寬字符
   * @param {string} text - 要隱藏的文字
   * @returns {string} - 零寬字符串
   */
  encode(text) {
    // 1. 轉換為二進制
    const binary = Array.from(text)
      .map(char => char.charCodeAt(0).toString(2).padStart(8, '0'))
      .join('');
    
    // 2. 二進制轉零寬字符
    const zeroWidth = binary
      .split('')
      .map(bit => bit === '0' ? this.ZERO : this.ONE)
      .join('');
    
    return zeroWidth;
  }
  
  /**
   * 從零寬字符解碼文字
   * @param {string} text - 包含零寬字符的文字
   * @returns {string} - 解碼後的文字
   */
  decode(text) {
    // 1. 提取零寬字符
    const zeroWidthChars = text
      .split('')
      .filter(char => char === this.ZERO || char === this.ONE)
      .join('');
    
    if (zeroWidthChars.length === 0) {
      return '';
    }
    
    // 2. 零寬字符轉二進制
    const binary = zeroWidthChars
      .split('')
      .map(char => char === this.ZERO ? '0' : '1')
      .join('');
    
    // 3. 二進制轉文字
    const chars = binary.match(/.{8}/g) || [];
    const decoded = chars
      .map(byte => String.fromCharCode(parseInt(byte, 2)))
      .join('');
    
    return decoded;
  }
  
  /**
   * 將浮水印嵌入到網頁元素中
   * @param {string} selector - CSS 選擇器
   * @param {string} watermark - 浮水印文字
   */
  embedIntoPage(selector, watermark) {
    const encoded = this.encode(watermark);
    const elements = document.querySelectorAll(selector);
    
    elements.forEach(el => {
      // 在元素文本末尾添加零寬字符
      if (el.textContent) {
        el.textContent = el.textContent + encoded;
      }
    });
  }
  
  /**
   * 從網頁中提取浮水印
   * @returns {string} - 提取的浮水印文字
   */
  extractFromPage() {
    const bodyText = document.body.innerText;
    return this.decode(bodyText);
  }
  
  /**
   * 將浮水印嵌入到 HTML 字符串中
   * @param {string} html - 原始 HTML
   * @param {string} watermark - 浮水印文字
   * @returns {string} - 帶浮水印的 HTML
   */
  embedIntoHTML(html, watermark) {
    const encoded = this.encode(watermark);
    // 插入到 </body> 之前
    return html.replace(/<\/body>/, encoded + '</body>');
  }
  
  /**
   * 從 HTML 字符串中提取浮水印
   * @param {string} html - 帶浮水印的 HTML
   * @returns {string} - 浮水印文字
   */
  extractFromHTML(html) {
    return this.decode(html);
  }
}

// 全域實例
if (typeof window !== 'undefined') {
  window.ZeroWidthWatermark = ZeroWidthWatermark;
}

