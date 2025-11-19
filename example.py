#!/usr/bin/env python3
"""
Example usage of the App Storage Manager

This script demonstrates the key features of the app storage management system.
"""

from app_storage_manager import AppStorageManager
from datetime import datetime, timedelta
import json


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """Run example demonstration"""
    print_section("App Storage Manager - Example Demo")
    
    # Initialize the manager
    print("\n1. Initializing App Storage Manager...")
    manager = AppStorageManager('config.json')
    print("✓ Manager initialized")
    
    # Add sample apps
    print_section("2. Adding Sample Apps")
    apps_to_add = [
        ('com.social.facebook', 'Facebook', 245.5),
        ('com.game.candycrush', 'Candy Crush', 180.0),
        ('com.utility.calculator', 'Calculator', 8.5),
        ('com.game.pubg', 'PUBG Mobile', 1500.0),
        ('com.music.spotify', 'Spotify', 120.0),
        ('com.old.myspace', 'MySpace', 250.0),
        ('com.rarely.used', 'Old Game', 450.0),
    ]
    
    for app_id, name, size in apps_to_add:
        manager.add_app(app_id, name, size)
        print(f"  ✓ Added: {name} ({size} MB)")
    
    # Simulate usage patterns
    print_section("3. Simulating Usage Patterns")
    
    # Frequently used apps
    print("\nFrequently used apps:")
    for i in range(20):
        manager.record_app_usage('com.social.facebook')
    print("  • Facebook: 20 uses")
    
    for i in range(15):
        manager.record_app_usage('com.music.spotify')
    print("  • Spotify: 15 uses")
    
    for i in range(12):
        manager.record_app_usage('com.utility.calculator')
    print("  • Calculator: 12 uses")
    
    # Occasionally used apps
    print("\nOccasionally used apps:")
    for i in range(5):
        manager.record_app_usage('com.game.candycrush')
    print("  • Candy Crush: 5 uses")
    
    for i in range(3):
        manager.record_app_usage('com.game.pubg')
    print("  • PUBG Mobile: 3 uses")
    
    # Simulate old apps by modifying last_used date
    print("\nSimulating old/unused apps:")
    old_app = manager.apps['com.old.myspace']
    old_app.last_used = (datetime.now() - timedelta(days=45)).isoformat()
    old_app.usage_count = 2
    print("  • MySpace: Last used 45 days ago, 2 total uses")
    
    rarely_app = manager.apps['com.rarely.used']
    rarely_app.last_used = (datetime.now() - timedelta(days=15)).isoformat()
    rarely_app.usage_count = 3
    print("  • Old Game: Last used 15 days ago, 3 total uses")
    
    manager._save_apps()
    
    # Show initial storage summary
    print_section("4. Initial Storage Summary")
    summary = manager.get_storage_summary()
    print(f"\nTotal Apps: {summary['total_apps']}")
    print(f"Total Size: {summary['total_size_mb']} MB")
    print(f"Active Apps: {summary['active_apps']}")
    print(f"Paused Apps: {summary['paused_apps']}")
    
    # Show unused apps
    print_section("5. Identifying Unused Apps")
    unused = manager.get_unused_apps()
    if unused:
        print(f"\nFound {len(unused)} unused app(s):")
        for app in unused:
            print(f"  • {app.name}")
            print(f"    Size: {app.size_mb} MB")
            print(f"    Last used: {app.last_used[:10]}")
            print(f"    Usage count: {app.usage_count}")
    else:
        print("\nNo unused apps found")
    
    # Show junk apps
    print_section("6. Identifying Junk Apps")
    junk = manager.identify_junk_apps()
    if junk:
        print(f"\nFound {len(junk)} junk app(s):")
        total_junk_size = 0
        for app in junk:
            print(f"  • {app.name}")
            print(f"    Size: {app.size_mb} MB")
            print(f"    Last used: {app.last_used[:10]}")
            print(f"    Usage count: {app.usage_count}")
            total_junk_size += app.size_mb
        print(f"\nTotal junk size: {total_junk_size:.2f} MB")
    else:
        print("\nNo junk apps found")
    
    # Show rarely used apps
    print_section("7. Identifying Rarely Used Apps")
    rarely = manager.get_rarely_used_apps()
    if rarely:
        print(f"\nFound {len(rarely)} rarely used app(s):")
        for app in rarely:
            print(f"  • {app.name} ({app.size_mb} MB)")
    else:
        print("\nNo rarely used apps found")
    
    # Run optimization
    print_section("8. Running Storage Optimization")
    results = manager.optimize_storage()
    
    print(f"\n✓ Optimization complete!")
    print(f"\nPaused {len(results['paused_apps'])} rarely used app(s):")
    for app in results['paused_apps']:
        print(f"  • {app['name']} ({app['size_mb']} MB)")
    
    print(f"\nMarked {len(results['marked_for_deletion'])} app(s) for deletion:")
    for app in results['marked_for_deletion']:
        print(f"  • {app['name']} ({app['size_mb']} MB)")
    
    print(f"\nPotential space savings: {results['space_saved_mb']} MB")
    
    # Show final storage summary
    print_section("9. Final Storage Summary")
    summary = manager.get_storage_summary()
    print(f"\nTotal Apps: {summary['total_apps']}")
    print(f"Total Size: {summary['total_size_mb']} MB")
    print(f"Active Apps: {summary['active_apps']} ({summary['active_size_mb']} MB)")
    print(f"Paused Apps: {summary['paused_apps']} ({summary['paused_size_mb']} MB)")
    print(f"Unused Apps: {summary['unused_apps']} ({summary['unused_size_mb']} MB)")
    print(f"Junk Apps: {summary['junk_apps']}")
    print(f"Potential Space Savings: {summary['potential_space_saving_mb']} MB")
    
    print_section("Demo Complete")
    print("\nThe app data has been saved to 'app_data.json'")
    print("You can now use the CLI to manage these apps:")
    print("  python cli.py list")
    print("  python cli.py summary")
    print("  python cli.py optimize")
    print()


if __name__ == '__main__':
    main()
