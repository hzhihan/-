# App Storage Manager - Quick Usage Guide

## 快速開始指南 (Quick Start Guide)

### 安裝 (Installation)
```bash
git clone https://github.com/hzhihan/-
cd -
```

無需額外依賴！僅使用 Python 標準庫。
No external dependencies needed! Uses only Python standard library.

### 基本使用 (Basic Usage)

#### 1. 查看儲存空間摘要 (View Storage Summary)
```bash
python cli.py summary
```

#### 2. 列出所有應用程式 (List All Apps)
```bash
python cli.py list
```

#### 3. 識別未使用的應用程式 (Identify Unused Apps)
```bash
python cli.py unused
```

#### 4. 識別垃圾應用程式 (Identify Junk Apps)
```bash
python cli.py junk
```

#### 5. 執行自動優化 (Run Automatic Optimization)
```bash
python cli.py optimize
```

這將：
- 自動暫停很少使用的應用程式
- 標記垃圾應用程式以供刪除
- 顯示可節省的空間

This will:
- Automatically pause rarely used apps
- Mark junk apps for deletion
- Show potential space savings

### 進階功能 (Advanced Features)

#### 添加應用程式 (Add an App)
```bash
python cli.py add com.example.app "App Name" 150.5
```

#### 記錄應用程式使用 (Record App Usage)
```bash
python cli.py use com.example.app
```

#### 暫停特定應用程式 (Pause a Specific App)
```bash
python cli.py pause com.example.app
```

#### 刪除應用程式 (Delete an App)
```bash
python cli.py delete com.example.app
```

### 配置自定義 (Configuration Customization)

編輯 `config.json` 以自定義行為：

Edit `config.json` to customize behavior:

```json
{
  "unused_days_threshold": 30,      // 未使用天數門檻
  "rarely_used_threshold": 7,       // 很少使用天數門檻
  "min_usage_count": 5,             // 最小使用次數
  "junk_size_threshold_mb": 100,    // 垃圾應用大小門檻 (MB)
  "auto_pause_enabled": true,       // 自動暫停啟用
  "auto_delete_enabled": false      // 自動刪除啟用（默認關閉以保安全）
}
```

### Python API 使用 (Python API Usage)

```python
from app_storage_manager import AppStorageManager

# 初始化管理器 (Initialize manager)
manager = AppStorageManager('config.json')

# 添加應用程式 (Add apps)
manager.add_app('com.example.app', 'My App', 150.0)

# 記錄使用 (Record usage)
manager.record_app_usage('com.example.app')

# 獲取摘要 (Get summary)
summary = manager.get_storage_summary()
print(f"總空間: {summary['total_size_mb']} MB")

# 執行優化 (Run optimization)
results = manager.optimize_storage()
print(f"可節省空間: {results['space_saved_mb']} MB")
```

### 運行示例 (Run Example)

```bash
python example.py
```

這將創建示例數據並演示所有功能。
This will create sample data and demonstrate all features.

### 運行測試 (Run Tests)

```bash
python -m unittest test_app_storage_manager.py -v
```

### 常見使用情境 (Common Use Cases)

#### 情境 1: 定期維護 (Regular Maintenance)
每週運行一次以保持儲存空間整潔：
Run weekly to keep storage clean:
```bash
python cli.py optimize
```

#### 情境 2: 安裝新應用前檢查 (Before Installing New Apps)
檢查可用空間：
Check available space:
```bash
python cli.py summary
python cli.py junk
```

#### 情境 3: 尋找佔用大量空間的應用 (Find Space Hogs)
尋找大型未使用的應用：
Find large unused apps:
```bash
python cli.py junk
```

#### 情境 4: 監控所有應用 (Monitor All Apps)
查看所有追蹤的應用：
Review all tracked apps:
```bash
python cli.py list
```

### 安全功能 (Safety Features)

- ✅ 默認不自動刪除應用程式
- ✅ 刪除前需要確認
- ✅ 暫停的應用在使用時會自動重新激活
- ✅ 所有數據持久化保存

- ✅ No auto-delete by default
- ✅ Confirmation required before deletion
- ✅ Paused apps automatically reactivate when used
- ✅ All data persists across sessions

### 系統要求 (System Requirements)

- Python 3.7 或更高版本
- 無外部依賴

- Python 3.7 or higher
- No external dependencies

### 支援 (Support)

如有問題或建議，請在 GitHub 上提交 issue。

For questions or suggestions, please submit an issue on GitHub.
