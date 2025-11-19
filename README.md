# App Storage Manager

A Python-based solution for managing mobile app storage efficiently. This system helps users:

1. **Reduce app storage usage** - Track and manage app sizes
2. **Automatically identify unused/junk apps** - Find apps that haven't been used recently
3. **Pause rarely used apps** - Automatically suspend apps that are rarely accessed to save storage space

## Features

- 📊 **Storage Tracking**: Monitor app sizes and total storage usage
- 🔍 **Smart Detection**: Automatically identify unused and junk apps
- ⏸️ **Auto-Pause**: Suspend rarely used apps to optimize storage
- 📈 **Usage Analytics**: Track app usage patterns over time
- ⚙️ **Configurable**: Customize thresholds and policies
- 💾 **Persistent Storage**: Data is saved and persists across sessions
- 🔒 **Safe Deletion**: Requires confirmation before deleting apps

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Clone or download the repository
git clone https://github.com/hzhihan/-
cd -

# Make CLI executable (optional)
chmod +x cli.py
```

## Quick Start

### Using the Python API

```python
from app_storage_manager import AppStorageManager

# Initialize the manager
manager = AppStorageManager()

# Add apps to track
manager.add_app('com.example.app1', 'Social App', 150.5)
manager.add_app('com.example.app2', 'Game', 500.0)
manager.add_app('com.example.app3', 'Utility', 25.0)

# Record app usage
manager.record_app_usage('com.example.app1')

# Get storage summary
summary = manager.get_storage_summary()
print(f"Total apps: {summary['total_apps']}")
print(f"Total size: {summary['total_size_mb']} MB")

# Run optimization
results = manager.optimize_storage()
print(f"Paused {len(results['paused_apps'])} apps")
print(f"Potential savings: {results['space_saved_mb']} MB")
```

### Using the CLI

```bash
# Add an app
python cli.py add com.example.app "My App" 150.5

# Record app usage
python cli.py use com.example.app

# List all apps
python cli.py list

# Show unused apps
python cli.py unused

# Show junk apps that can be removed
python cli.py junk

# Get storage summary
python cli.py summary

# Run automatic optimization
python cli.py optimize

# Pause a specific app
python cli.py pause com.example.app

# Delete an app
python cli.py delete com.example.app
```

## Configuration

Create a `config.json` file to customize behavior:

```json
{
  "unused_days_threshold": 30,
  "rarely_used_threshold": 7,
  "min_usage_count": 5,
  "junk_size_threshold_mb": 100,
  "auto_pause_enabled": true,
  "auto_delete_enabled": false,
  "data_file": "app_data.json"
}
```

### Configuration Options

- **unused_days_threshold**: Number of days before an app is considered unused (default: 30)
- **rarely_used_threshold**: Number of days to classify as "rarely used" (default: 7)
- **min_usage_count**: Minimum times an app should be used to not be considered junk (default: 5)
- **junk_size_threshold_mb**: Size in MB above which unused apps are considered junk (default: 100)
- **auto_pause_enabled**: Automatically pause rarely used apps (default: true)
- **auto_delete_enabled**: Automatically delete marked apps without confirmation (default: false)
- **data_file**: File to store app data (default: app_data.json)

## How It Works

### Junk App Detection

An app is identified as "junk" if it meets any of these criteria:
- Not used for more than the `unused_days_threshold` (default: 30 days)
- Has fewer than `min_usage_count` total uses (default: 5)
- Size exceeds `junk_size_threshold_mb` (default: 100 MB) and is unused

### Automatic Pausing

Apps that haven't been used within the `rarely_used_threshold` (default: 7 days) are automatically paused during optimization. Paused apps can be reactivated simply by recording their usage.

### Storage Optimization

The `optimize_storage()` function:
1. Identifies rarely used apps and pauses them
2. Identifies junk apps and marks them for deletion
3. Returns potential space savings

Apps marked for deletion require explicit confirmation before actual deletion (safety feature).

## API Reference

### AppStorageManager

Main class for managing app storage.

#### Methods

- `__init__(config_path: Optional[str])` - Initialize the manager
- `add_app(app_id: str, name: str, size_mb: float)` - Add a new app
- `record_app_usage(app_id: str)` - Record app usage
- `get_unused_apps()` - Get list of unused apps
- `get_rarely_used_apps()` - Get list of rarely used apps
- `identify_junk_apps()` - Identify potential junk apps
- `pause_app(app_id: str)` - Pause an app
- `auto_pause_rarely_used_apps()` - Auto-pause rarely used apps
- `mark_for_deletion(app_id: str)` - Mark an app for deletion
- `delete_app(app_id: str)` - Delete an app
- `get_storage_summary()` - Get storage statistics
- `optimize_storage()` - Run automatic optimization

### AppInfo

Data class representing an app.

#### Attributes

- `app_id: str` - Unique app identifier
- `name: str` - Display name
- `size_mb: float` - Size in megabytes
- `last_used: str` - Last usage timestamp (ISO format)
- `install_date: str` - Installation date (ISO format)
- `usage_count: int` - Number of times used
- `status: str` - Current status (active, paused, marked_for_deletion, junk)

## Testing

Run the test suite:

```bash
python -m unittest test_app_storage_manager.py -v
```

## Example Usage Scenario

```python
from app_storage_manager import AppStorageManager
import json

# Initialize
manager = AppStorageManager('config.json')

# Add some apps
manager.add_app('com.social.app', 'Social Media', 250.0)
manager.add_app('com.game.heavy', 'Heavy Game', 1500.0)
manager.add_app('com.utility.tool', 'Utility Tool', 15.0)
manager.add_app('com.old.app', 'Old App', 500.0)

# Simulate usage patterns
for i in range(10):
    manager.record_app_usage('com.social.app')
    manager.record_app_usage('com.utility.tool')

# Only use game once
manager.record_app_usage('com.game.heavy')

# Make old app appear unused (you would manually edit last_used in real scenario)

# Check storage summary
print("\nBefore optimization:")
summary = manager.get_storage_summary()
print(json.dumps(summary, indent=2))

# Run optimization
print("\nRunning optimization...")
results = manager.optimize_storage()
print(json.dumps(results, indent=2))

# Check summary again
print("\nAfter optimization:")
summary = manager.get_storage_summary()
print(json.dumps(summary, indent=2))
```

## CLI Examples

### List apps with filtering
```bash
# List all apps
python cli.py list

# List only paused apps
python cli.py list --status paused

# List only active apps
python cli.py list --status active
```

### Get insights
```bash
# Show storage summary
python cli.py summary

# Find unused apps
python cli.py unused

# Find junk apps that waste space
python cli.py junk
```

### Manage apps
```bash
# Add a new app
python cli.py add com.example.newapp "New App" 75.5

# Record usage
python cli.py use com.example.newapp

# Pause an app
python cli.py pause com.example.oldapp

# Delete an app (with confirmation)
python cli.py delete com.example.junkapp

# Delete without confirmation
python cli.py delete com.example.junkapp --force
```

### Optimize storage
```bash
# Run optimization (will prompt for deletion)
python cli.py optimize

# Run optimization without deletion prompt
python cli.py optimize --no-prompt
```

## Use Cases

1. **Regular Maintenance**: Run `python cli.py optimize` weekly to keep storage clean
2. **Before Installing New Apps**: Check `python cli.py summary` to see available space
3. **Finding Space Hogs**: Use `python cli.py junk` to find large unused apps
4. **Monitoring**: Use `python cli.py list` to review all tracked apps

## Safety Features

- **No Auto-Delete**: By default, apps are only marked for deletion, not automatically deleted
- **Confirmation Required**: CLI prompts for confirmation before deleting apps
- **Reactivation**: Paused apps are automatically reactivated when used
- **Persistent Data**: All data is saved to disk and persists across sessions

## Requirements

- Python 3.7 or higher
- No external dependencies

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Language Support

系統功能（中文說明）：
- **減少應用程式容量**：追蹤和管理應用程式大小
- **自動刪除垃圾應用程式**：找出長時間未使用的應用程式
- **自動暫停很少使用的應用程式**：自動暫停較少存取的應用程式以節省儲存空間