"""
App Storage Manager - A tool to manage mobile app storage efficiently

This module provides functionality to:
1. Track app usage patterns
2. Identify and remove junk/unused apps
3. Automatically pause rarely used apps to save storage
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class AppStatus(Enum):
    """Status of an app in the system"""
    ACTIVE = "active"
    PAUSED = "paused"
    MARKED_FOR_DELETION = "marked_for_deletion"
    JUNK = "junk"


@dataclass
class AppInfo:
    """Information about an installed app"""
    app_id: str
    name: str
    size_mb: float
    last_used: str  # ISO format datetime
    install_date: str  # ISO format datetime
    usage_count: int
    status: str = AppStatus.ACTIVE.value
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'AppInfo':
        return AppInfo(**data)


class AppStorageManager:
    """Main class for managing app storage"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the App Storage Manager
        
        Args:
            config_path: Path to configuration file
        """
        self.apps: Dict[str, AppInfo] = {}
        self.config = self._load_config(config_path)
        self.data_file = self.config.get('data_file', 'app_data.json')
        self._load_apps()
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'unused_days_threshold': 30,  # Days before app is considered unused
            'rarely_used_threshold': 7,   # Days between uses for "rarely used"
            'min_usage_count': 5,          # Minimum uses before considering deletion
            'junk_size_threshold_mb': 100, # Size threshold for junk detection
            'auto_pause_enabled': True,
            'auto_delete_enabled': False,  # Safety: require explicit confirmation
            'data_file': 'app_data.json'
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
        
        return default_config
    
    def _load_apps(self):
        """Load app data from storage"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.apps = {
                        app_id: AppInfo.from_dict(app_data)
                        for app_id, app_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load app data: {e}")
                self.apps = {}
    
    def _save_apps(self):
        """Save app data to storage"""
        try:
            data = {
                app_id: app.to_dict()
                for app_id, app in self.apps.items()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving app data: {e}")
    
    def add_app(self, app_id: str, name: str, size_mb: float) -> AppInfo:
        """
        Add a new app to tracking
        
        Args:
            app_id: Unique identifier for the app
            name: Display name of the app
            size_mb: Size of the app in megabytes
            
        Returns:
            AppInfo object for the added app
        """
        now = datetime.now().isoformat()
        app = AppInfo(
            app_id=app_id,
            name=name,
            size_mb=size_mb,
            last_used=now,
            install_date=now,
            usage_count=1
        )
        self.apps[app_id] = app
        self._save_apps()
        return app
    
    def record_app_usage(self, app_id: str):
        """
        Record that an app was used
        
        Args:
            app_id: ID of the app that was used
        """
        if app_id in self.apps:
            app = self.apps[app_id]
            app.last_used = datetime.now().isoformat()
            app.usage_count += 1
            if app.status == AppStatus.PAUSED.value:
                app.status = AppStatus.ACTIVE.value
            self._save_apps()
    
    def get_unused_apps(self) -> List[AppInfo]:
        """
        Get list of apps that haven't been used recently
        
        Returns:
            List of unused apps
        """
        threshold_days = self.config['unused_days_threshold']
        threshold_date = datetime.now() - timedelta(days=threshold_days)
        
        unused = []
        for app in self.apps.values():
            last_used = datetime.fromisoformat(app.last_used)
            if last_used < threshold_date:
                unused.append(app)
        
        return sorted(unused, key=lambda x: x.last_used)
    
    def get_rarely_used_apps(self) -> List[AppInfo]:
        """
        Get list of apps that are rarely used
        
        Returns:
            List of rarely used apps
        """
        threshold_days = self.config['rarely_used_threshold']
        threshold_date = datetime.now() - timedelta(days=threshold_days)
        
        rarely_used = []
        for app in self.apps.values():
            last_used = datetime.fromisoformat(app.last_used)
            if last_used < threshold_date and app.status == AppStatus.ACTIVE.value:
                rarely_used.append(app)
        
        return sorted(rarely_used, key=lambda x: x.last_used)
    
    def identify_junk_apps(self) -> List[AppInfo]:
        """
        Identify potential junk apps based on usage patterns
        
        An app is considered junk if:
        - It hasn't been used in the threshold period
        - It has low usage count
        - It takes up significant space
        
        Returns:
            List of apps identified as junk
        """
        unused_apps = self.get_unused_apps()
        min_usage = self.config['min_usage_count']
        size_threshold = self.config['junk_size_threshold_mb']
        
        junk_apps = []
        for app in unused_apps:
            if app.usage_count < min_usage or app.size_mb > size_threshold:
                junk_apps.append(app)
        
        return junk_apps
    
    def pause_app(self, app_id: str) -> bool:
        """
        Pause an app (mark it as suspended)
        
        Args:
            app_id: ID of the app to pause
            
        Returns:
            True if successful, False otherwise
        """
        if app_id in self.apps:
            self.apps[app_id].status = AppStatus.PAUSED.value
            self._save_apps()
            return True
        return False
    
    def auto_pause_rarely_used_apps(self) -> List[AppInfo]:
        """
        Automatically pause rarely used apps
        
        Returns:
            List of apps that were paused
        """
        if not self.config['auto_pause_enabled']:
            return []
        
        rarely_used = self.get_rarely_used_apps()
        paused = []
        
        for app in rarely_used:
            if self.pause_app(app.app_id):
                paused.append(app)
        
        return paused
    
    def mark_for_deletion(self, app_id: str) -> bool:
        """
        Mark an app for deletion
        
        Args:
            app_id: ID of the app to mark
            
        Returns:
            True if successful, False otherwise
        """
        if app_id in self.apps:
            self.apps[app_id].status = AppStatus.MARKED_FOR_DELETION.value
            self._save_apps()
            return True
        return False
    
    def delete_app(self, app_id: str) -> bool:
        """
        Remove an app from tracking (simulates deletion)
        
        Args:
            app_id: ID of the app to delete
            
        Returns:
            True if successful, False otherwise
        """
        if app_id in self.apps:
            del self.apps[app_id]
            self._save_apps()
            return True
        return False
    
    def get_storage_summary(self) -> dict:
        """
        Get summary of storage usage
        
        Returns:
            Dictionary with storage statistics
        """
        total_size = sum(app.size_mb for app in self.apps.values())
        active_size = sum(
            app.size_mb for app in self.apps.values()
            if app.status == AppStatus.ACTIVE.value
        )
        paused_size = sum(
            app.size_mb for app in self.apps.values()
            if app.status == AppStatus.PAUSED.value
        )
        
        unused_apps = self.get_unused_apps()
        unused_size = sum(app.size_mb for app in unused_apps)
        
        junk_apps = self.identify_junk_apps()
        junk_size = sum(app.size_mb for app in junk_apps)
        
        return {
            'total_apps': len(self.apps),
            'total_size_mb': round(total_size, 2),
            'active_apps': sum(1 for app in self.apps.values() 
                             if app.status == AppStatus.ACTIVE.value),
            'active_size_mb': round(active_size, 2),
            'paused_apps': sum(1 for app in self.apps.values() 
                             if app.status == AppStatus.PAUSED.value),
            'paused_size_mb': round(paused_size, 2),
            'unused_apps': len(unused_apps),
            'unused_size_mb': round(unused_size, 2),
            'junk_apps': len(junk_apps),
            'potential_space_saving_mb': round(junk_size, 2)
        }
    
    def optimize_storage(self) -> dict:
        """
        Perform automatic storage optimization
        
        Returns:
            Dictionary with optimization results
        """
        results = {
            'paused_apps': [],
            'marked_for_deletion': [],
            'space_saved_mb': 0
        }
        
        # Auto-pause rarely used apps
        paused = self.auto_pause_rarely_used_apps()
        results['paused_apps'] = [
            {'app_id': app.app_id, 'name': app.name, 'size_mb': app.size_mb}
            for app in paused
        ]
        
        # Mark junk apps for deletion (but don't auto-delete)
        junk_apps = self.identify_junk_apps()
        for app in junk_apps:
            if self.mark_for_deletion(app.app_id):
                results['marked_for_deletion'].append({
                    'app_id': app.app_id,
                    'name': app.name,
                    'size_mb': app.size_mb
                })
                results['space_saved_mb'] += app.size_mb
        
        results['space_saved_mb'] = round(results['space_saved_mb'], 2)
        return results


def main():
    """Example usage of the App Storage Manager"""
    manager = AppStorageManager()
    
    # Example: Add some sample apps
    manager.add_app('com.example.app1', 'Social App', 150.5)
    manager.add_app('com.example.app2', 'Game', 500.0)
    manager.add_app('com.example.app3', 'Utility', 25.0)
    
    # Show storage summary
    summary = manager.get_storage_summary()
    print("Storage Summary:")
    print(json.dumps(summary, indent=2))
    
    # Run optimization
    print("\nRunning storage optimization...")
    results = manager.optimize_storage()
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
