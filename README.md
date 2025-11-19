# 雙重水印系統

一個完整的雙重水印系統，支援**明碼水印**和**隱碼水印**，包含網頁和圖像兩種載體類型。

## 功能特色

- **網頁明碼水印**: 使用 watermark.js 在網頁上添加可見的半透明文字水印
- **網頁隱碼水印**: 使用零寬字符(Zero-Width Characters)在網頁文本中嵌入不可見水印
- **圖像明碼水印**: 使用 Pillow 在圖像上添加可見水印
- **圖像隱碼水印**: 使用 blind_watermark (DWT-DCT-SVD) 在圖像頻域嵌入不可見水印

## 技術架構

### 後端
- Flask 3.0
- blind-watermark 0.4.4
- Pillow 10.1.0
- OpenCV 4.8.1

### 前端
- HTML5 + Vanilla JavaScript (ES6+)
- watermark.js
- Canvas API

## 安裝步驟

### 1. 環境準備

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 下載 watermark.js

watermark.js 需要手動下載並放置到 `static/js/` 目錄：

**方法 1: 從 GitHub 下載（推薦）**
1. 訪問 https://github.com/saucxs/watermark-dom
2. 下載 `dist/watermark.min.js` 或 `dist/watermark.js`
3. 重命名為 `watermark.js` 並放置到 `static/js/` 目錄

**方法 2: 使用 npm (如果有 Node.js)**
```bash
npm install watermark-dom
cp node_modules/watermark-dom/dist/watermark.min.js static/js/watermark.js
```

**方法 3: 直接使用 CDN（修改 base.html）**
如果無法下載，可以修改 `templates/base.html`，將：
```html
<script src="{{ url_for('static', filename='js/watermark.js') }}"></script>
```
改為：
```html
<script src="https://unpkg.com/watermark-dom@latest/dist/watermark.min.js"></script>
```

### 3. 啟動應用

```bash
python app.py
```

訪問 http://localhost:5000

## 專案結構

```
watermark_system_demo/
├── app.py                      # Flask 主應用
├── requirements.txt            # Python 依賴
├── config.py                   # 配置文件
├── wsgi.py                     # WSGI 入口
│
├── services/                   # 服務層
│   ├── watermark_service.py   # 統一水印服務
│   ├── image_processor.py     # 圖像處理
│   └── file_manager.py        # 檔案管理
│
├── static/                     # 靜態資源
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── watermark.js        # 需要下載
│   │   ├── zero-width.js       # 網頁隱碼水印庫
│   │   └── main.js             # 主要邏輯
│   └── uploads/                # 上傳目錄
│
├── templates/                  # HTML 模板
│   ├── base.html               # 基礎模板
│   ├── index.html              # 首頁
│   ├── webpage.html            # 網頁水印頁面
│   ├── image_visible.html      # 圖像明碼頁面
│   └── image_blind.html        # 圖像隱碼頁面
│
└── output/                     # 輸出目錄
```

## API 端點

### 圖像明碼水印
- `POST /api/image/visible/embed` - 嵌入明碼水印

### 圖像隱碼水印
- `POST /api/image/blind/embed` - 嵌入隱碼水印
- `POST /api/image/blind/extract` - 提取隱碼水印

## 使用說明

### 網頁水印
1. 訪問 `/webpage`
2. 配置明碼水印參數（文字、透明度、顏色等）
3. 點擊「套用明碼水印」
4. 輸入隱藏文字，點擊「嵌入隱碼水印」
5. 點擊「提取隱碼水印」查看結果

### 圖像明碼水印
1. 訪問 `/image-visible`
2. 上傳圖像
3. 配置水印參數
4. 點擊「嵌入水印」
5. 下載帶水印的圖像

### 圖像隱碼水印
1. 訪問 `/image-blind`
2. 上傳圖像並輸入水印文字
3. 點擊「嵌入水印」
4. 記下水印長度（位元數）
5. 上傳帶水印的圖像，輸入水印長度
6. 點擊「提取水印」查看結果

## 注意事項

1. **watermark.js 必須下載**: 網頁明碼水印功能需要 watermark.js 庫，請確保已下載並放置在 `static/js/watermark.js`
2. **圖像格式**: 支援 PNG, JPG, JPEG, BMP, GIF
3. **文件大小**: 最大支援 16MB
4. **隱碼水印長度**: 提取隱碼水印時必須提供正確的水印長度（位元數）

## 開發說明

本專案按照《雙重水印系統開發文件.md》規格開發，包含完整的服務層、API 路由和前端界面。

## 授權

MIT License

