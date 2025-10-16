# Zuvio Auto Check-in System

自動化的 Zuvio 簽到系統，支援多種學校網域。

## 功能特色

- 🔐 支援完整郵箱地址或學號自動補全
- 📍 自訂位置資訊設定
- 🔄 自動登入測試和重試機制
- 📊 完整的日誌記錄
- 🧪 完整的單元測試覆蓋
- 🚀 GitHub Actions 自動化 CI/CD

## 安裝說明

### 使用 uv（推薦）

```bash
# 安裝 uv
pip install uv

# 建立虛擬環境
uv venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝基本依賴
uv pip install -r requirements.txt
```

### 使用 pip

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

## 開發環境設定

如果您要進行開發，請安裝開發依賴：

```bash
# 使用 uv
uv pip install -r requirements-dev.txt

# 或使用 pip
pip install -r requirements-dev.txt
```

## 使用方式

```bash
# 執行程式
python main.py

# 執行測試
python -m pytest tests/ -v

# 執行測試並生成覆蓋率報告
python -m pytest tests/ -v --cov=main --cov-report=html

# 使用測試腳本
python run_tests.py --coverage --verbose
```

## 測試

### 執行所有測試
```bash
python -m pytest tests/ -v
```

### 執行特定測試
```bash
python -m pytest tests/test_auth_service.py -v
```

### 測試覆蓋率
```bash
python -m pytest tests/ --cov=main --cov-report=html
```

## 程式碼品質檢查

### 格式化程式碼
```bash
black .
isort .
```

### 程式碼檢查
```bash
flake8 .
mypy main.py
```

### 安全性檢查
```bash
bandit -r main.py
safety check
```

## 專案結構

```
auto-zuvio/
├── main.py                 # 主程式
├── requirements.txt        # 基本依賴
├── requirements-dev.txt    # 開發依賴
├── pytest.ini            # pytest 配置
├── run_tests.py          # 測試執行腳本
├── tests/                # 測試目錄
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_auth_service.py
│   ├── test_config_manager.py
│   ├── test_course_service.py
│   ├── test_user_credentials.py
│   └── test_zuvio_auto_checker.py
└── .github/
    └── workflows/
        └── test.yml      # GitHub Actions 工作流程
```

## 依賴套件說明

### 基本依賴 (requirements.txt)
- `requests` - HTTP 請求處理
- `beautifulsoup4` - HTML 解析
- `configparser` - 配置檔案處理

### 測試依賴
- `pytest` - 測試框架
- `pytest-cov` - 測試覆蓋率
- `pytest-mock` - Mock 功能

### 開發依賴 (requirements-dev.txt)
- `black` - 程式碼格式化
- `flake8` - 程式碼檢查
- `isort` - import 排序
- `mypy` - 類型檢查
- `bandit` - 安全性檢查
- `safety` - 依賴安全性檢查

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 注意事項

- 請確保您的網路連線穩定
- 首次使用需要設定帳號密碼和位置資訊
- 建議在正式使用前先測試登入功能