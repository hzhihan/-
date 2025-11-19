"""
Unit tests for App Storage Manager
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from app_storage_manager import AppStorageManager, AppInfo, AppStatus


class TestAppInfo(unittest.TestCase):
    """Test AppInfo class"""
    
    def test_app_info_creation(self):
        """Test creating an AppInfo instance"""
        now = datetime.now().isoformat()
        app = AppInfo(
            app_id='com.test.app',
            name='Test App',
            size_mb=100.0,
            last_used=now,
            install_date=now,
            usage_count=5
        )
        self.assertEqual(app.app_id, 'com.test.app')
        self.assertEqual(app.name, 'Test App')
        self.assertEqual(app.size_mb, 100.0)
        self.assertEqual(app.status, AppStatus.ACTIVE.value)
    
    def test_app_info_serialization(self):
        """Test AppInfo to_dict and from_dict"""
        now = datetime.now().isoformat()
        app = AppInfo(
            app_id='com.test.app',
            name='Test App',
            size_mb=100.0,
            last_used=now,
            install_date=now,
            usage_count=5
        )
        
        # Convert to dict and back
        app_dict = app.to_dict()
        app_restored = AppInfo.from_dict(app_dict)
        
        self.assertEqual(app.app_id, app_restored.app_id)
        self.assertEqual(app.name, app_restored.name)
        self.assertEqual(app.size_mb, app_restored.size_mb)


class TestAppStorageManager(unittest.TestCase):
    """Test AppStorageManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_app_data.json')
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        
        # Create test config
        test_config = {
            'unused_days_threshold': 30,
            'rarely_used_threshold': 7,
            'min_usage_count': 5,
            'junk_size_threshold_mb': 100,
            'auto_pause_enabled': True,
            'auto_delete_enabled': False,
            'data_file': self.data_file
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        self.manager = AppStorageManager(self.config_file)
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_app(self):
        """Test adding a new app"""
        app = self.manager.add_app('com.test.app1', 'Test App 1', 150.0)
        
        self.assertIn('com.test.app1', self.manager.apps)
        self.assertEqual(app.name, 'Test App 1')
        self.assertEqual(app.size_mb, 150.0)
        self.assertEqual(app.status, AppStatus.ACTIVE.value)
    
    def test_record_usage(self):
        """Test recording app usage"""
        app = self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        initial_count = app.usage_count
        initial_time = app.last_used
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)
        
        self.manager.record_app_usage('com.test.app1')
        
        updated_app = self.manager.apps['com.test.app1']
        self.assertEqual(updated_app.usage_count, initial_count + 1)
        self.assertNotEqual(updated_app.last_used, initial_time)
    
    def test_get_unused_apps(self):
        """Test identifying unused apps"""
        # Add a recent app
        self.manager.add_app('com.test.recent', 'Recent App', 50.0)
        
        # Add an old app
        old_app = self.manager.add_app('com.test.old', 'Old App', 100.0)
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        old_app.last_used = old_date
        self.manager._save_apps()
        
        unused = self.manager.get_unused_apps()
        unused_ids = [app.app_id for app in unused]
        
        self.assertIn('com.test.old', unused_ids)
        self.assertNotIn('com.test.recent', unused_ids)
    
    def test_get_rarely_used_apps(self):
        """Test identifying rarely used apps"""
        # Add a recent app
        self.manager.add_app('com.test.recent', 'Recent App', 50.0)
        
        # Add a rarely used app
        rarely_used = self.manager.add_app('com.test.rarely', 'Rarely Used', 100.0)
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        rarely_used.last_used = old_date
        self.manager._save_apps()
        
        rarely = self.manager.get_rarely_used_apps()
        rarely_ids = [app.app_id for app in rarely]
        
        self.assertIn('com.test.rarely', rarely_ids)
        self.assertNotIn('com.test.recent', rarely_ids)
    
    def test_identify_junk_apps(self):
        """Test identifying junk apps"""
        # Add a large, unused app with low usage
        junk_app = self.manager.add_app('com.test.junk', 'Junk App', 200.0)
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        junk_app.last_used = old_date
        junk_app.usage_count = 2
        self.manager._save_apps()
        
        # Add a normal app
        self.manager.add_app('com.test.normal', 'Normal App', 50.0)
        
        junk = self.manager.identify_junk_apps()
        junk_ids = [app.app_id for app in junk]
        
        self.assertIn('com.test.junk', junk_ids)
        self.assertNotIn('com.test.normal', junk_ids)
    
    def test_pause_app(self):
        """Test pausing an app"""
        app = self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        self.assertEqual(app.status, AppStatus.ACTIVE.value)
        
        success = self.manager.pause_app('com.test.app1')
        self.assertTrue(success)
        
        updated_app = self.manager.apps['com.test.app1']
        self.assertEqual(updated_app.status, AppStatus.PAUSED.value)
    
    def test_auto_pause_rarely_used(self):
        """Test automatic pausing of rarely used apps"""
        # Add rarely used apps
        for i in range(3):
            app = self.manager.add_app(f'com.test.rarely{i}', f'Rarely {i}', 50.0)
            old_date = (datetime.now() - timedelta(days=10)).isoformat()
            app.last_used = old_date
        
        self.manager._save_apps()
        
        paused = self.manager.auto_pause_rarely_used_apps()
        self.assertEqual(len(paused), 3)
        
        for i in range(3):
            app = self.manager.apps[f'com.test.rarely{i}']
            self.assertEqual(app.status, AppStatus.PAUSED.value)
    
    def test_mark_for_deletion(self):
        """Test marking an app for deletion"""
        app = self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        
        success = self.manager.mark_for_deletion('com.test.app1')
        self.assertTrue(success)
        
        updated_app = self.manager.apps['com.test.app1']
        self.assertEqual(updated_app.status, AppStatus.MARKED_FOR_DELETION.value)
    
    def test_delete_app(self):
        """Test deleting an app"""
        self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        self.assertIn('com.test.app1', self.manager.apps)
        
        success = self.manager.delete_app('com.test.app1')
        self.assertTrue(success)
        self.assertNotIn('com.test.app1', self.manager.apps)
    
    def test_storage_summary(self):
        """Test getting storage summary"""
        # Add various apps
        self.manager.add_app('com.test.active', 'Active App', 100.0)
        
        paused_app = self.manager.add_app('com.test.paused', 'Paused App', 50.0)
        self.manager.pause_app('com.test.paused')
        
        old_app = self.manager.add_app('com.test.old', 'Old App', 75.0)
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        old_app.last_used = old_date
        old_app.usage_count = 2
        self.manager._save_apps()
        
        summary = self.manager.get_storage_summary()
        
        self.assertEqual(summary['total_apps'], 3)
        self.assertEqual(summary['total_size_mb'], 225.0)
        self.assertEqual(summary['active_apps'], 2)
        self.assertEqual(summary['paused_apps'], 1)
        self.assertGreater(summary['unused_apps'], 0)
    
    def test_optimize_storage(self):
        """Test storage optimization"""
        # Add rarely used app
        rarely_app = self.manager.add_app('com.test.rarely', 'Rarely Used', 80.0)
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        rarely_app.last_used = old_date
        self.manager._save_apps()
        
        # Add junk app
        junk_app = self.manager.add_app('com.test.junk', 'Junk App', 200.0)
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        junk_app.last_used = old_date
        junk_app.usage_count = 2
        self.manager._save_apps()
        
        results = self.manager.optimize_storage()
        
        self.assertGreater(len(results['paused_apps']), 0)
        self.assertGreater(len(results['marked_for_deletion']), 0)
        self.assertGreater(results['space_saved_mb'], 0)
    
    def test_persistence(self):
        """Test that data persists across manager instances"""
        # Add apps
        self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        self.manager.add_app('com.test.app2', 'Test App 2', 150.0)
        
        # Create new manager instance with same data file
        new_manager = AppStorageManager(self.config_file)
        
        self.assertEqual(len(new_manager.apps), 2)
        self.assertIn('com.test.app1', new_manager.apps)
        self.assertIn('com.test.app2', new_manager.apps)
    
    def test_usage_reactivates_paused_app(self):
        """Test that using a paused app reactivates it"""
        app = self.manager.add_app('com.test.app1', 'Test App 1', 100.0)
        self.manager.pause_app('com.test.app1')
        
        self.assertEqual(self.manager.apps['com.test.app1'].status, 
                        AppStatus.PAUSED.value)
        
        self.manager.record_app_usage('com.test.app1')
        
        self.assertEqual(self.manager.apps['com.test.app1'].status,
                        AppStatus.ACTIVE.value)


if __name__ == '__main__':
    unittest.main()
