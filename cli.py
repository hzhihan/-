#!/usr/bin/env python3
"""
CLI interface for App Storage Manager

Provides command-line access to app storage management features
"""

import argparse
import json
import sys
from app_storage_manager import AppStorageManager, AppStatus


def format_app_list(apps, title):
    """Format a list of apps for display"""
    if not apps:
        return f"\n{title}: None"
    
    lines = [f"\n{title}:"]
    lines.append("-" * 60)
    for app in apps:
        lines.append(f"  • {app.name} ({app.app_id})")
        lines.append(f"    Size: {app.size_mb} MB | Last used: {app.last_used}")
        lines.append(f"    Status: {app.status} | Usage count: {app.usage_count}")
    return "\n".join(lines)


def cmd_add(args, manager):
    """Add a new app"""
    app = manager.add_app(args.app_id, args.name, args.size)
    print(f"✓ Added app: {app.name} ({app.app_id})")
    print(f"  Size: {app.size_mb} MB")


def cmd_use(args, manager):
    """Record app usage"""
    manager.record_app_usage(args.app_id)
    print(f"✓ Recorded usage for app: {args.app_id}")


def cmd_list(args, manager):
    """List apps"""
    apps = list(manager.apps.values())
    
    if args.status:
        apps = [app for app in apps if app.status == args.status]
    
    if not apps:
        print("No apps found.")
        return
    
    print(f"\nTotal apps: {len(apps)}")
    print("-" * 60)
    for app in apps:
        print(f"• {app.name} ({app.app_id})")
        print(f"  Size: {app.size_mb} MB | Status: {app.status}")
        print(f"  Last used: {app.last_used} | Usage: {app.usage_count}")
        print()


def cmd_unused(args, manager):
    """Show unused apps"""
    unused = manager.get_unused_apps()
    print(format_app_list(unused, "Unused Apps"))
    if unused:
        total_size = sum(app.size_mb for app in unused)
        print(f"\nTotal unused space: {total_size:.2f} MB")


def cmd_junk(args, manager):
    """Show junk apps"""
    junk = manager.identify_junk_apps()
    print(format_app_list(junk, "Junk Apps"))
    if junk:
        total_size = sum(app.size_mb for app in junk)
        print(f"\nPotential space savings: {total_size:.2f} MB")


def cmd_pause(args, manager):
    """Pause an app"""
    if manager.pause_app(args.app_id):
        print(f"✓ Paused app: {args.app_id}")
    else:
        print(f"✗ App not found: {args.app_id}")


def cmd_delete(args, manager):
    """Delete an app"""
    if args.app_id in manager.apps:
        app = manager.apps[args.app_id]
        if not args.force:
            response = input(f"Delete '{app.name}' ({app.size_mb} MB)? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        if manager.delete_app(args.app_id):
            print(f"✓ Deleted app: {app.name}")
        else:
            print(f"✗ Failed to delete app")
    else:
        print(f"✗ App not found: {args.app_id}")


def cmd_summary(args, manager):
    """Show storage summary"""
    summary = manager.get_storage_summary()
    print("\n" + "=" * 60)
    print("Storage Summary")
    print("=" * 60)
    print(f"Total Apps: {summary['total_apps']}")
    print(f"Total Size: {summary['total_size_mb']} MB")
    print(f"\nActive Apps: {summary['active_apps']} ({summary['active_size_mb']} MB)")
    print(f"Paused Apps: {summary['paused_apps']} ({summary['paused_size_mb']} MB)")
    print(f"Unused Apps: {summary['unused_apps']} ({summary['unused_size_mb']} MB)")
    print(f"Junk Apps: {summary['junk_apps']}")
    print(f"\nPotential Space Savings: {summary['potential_space_saving_mb']} MB")
    print("=" * 60)


def cmd_optimize(args, manager):
    """Run storage optimization"""
    print("Running storage optimization...")
    results = manager.optimize_storage()
    
    print(f"\n✓ Optimization complete!")
    print(f"\nPaused {len(results['paused_apps'])} rarely used apps:")
    for app in results['paused_apps']:
        print(f"  • {app['name']} ({app['size_mb']} MB)")
    
    print(f"\nMarked {len(results['marked_for_deletion'])} apps for deletion:")
    for app in results['marked_for_deletion']:
        print(f"  • {app['name']} ({app['size_mb']} MB)")
    
    print(f"\nPotential space savings: {results['space_saved_mb']} MB")
    
    if results['marked_for_deletion'] and not args.no_prompt:
        response = input("\nDelete marked apps? [y/N]: ")
        if response.lower() == 'y':
            for app in results['marked_for_deletion']:
                manager.delete_app(app['app_id'])
            print("✓ Deleted marked apps")


def main():
    parser = argparse.ArgumentParser(
        description='App Storage Manager - Manage mobile app storage efficiently'
    )
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add app
    add_parser = subparsers.add_parser('add', help='Add a new app')
    add_parser.add_argument('app_id', help='Unique app identifier')
    add_parser.add_argument('name', help='App name')
    add_parser.add_argument('size', type=float, help='App size in MB')
    
    # Record usage
    use_parser = subparsers.add_parser('use', help='Record app usage')
    use_parser.add_argument('app_id', help='App identifier')
    
    # List apps
    list_parser = subparsers.add_parser('list', help='List apps')
    list_parser.add_argument(
        '--status', '-s',
        choices=[s.value for s in AppStatus],
        help='Filter by status'
    )
    
    # Show unused apps
    subparsers.add_parser('unused', help='Show unused apps')
    
    # Show junk apps
    subparsers.add_parser('junk', help='Show junk apps')
    
    # Pause app
    pause_parser = subparsers.add_parser('pause', help='Pause an app')
    pause_parser.add_argument('app_id', help='App identifier')
    
    # Delete app
    delete_parser = subparsers.add_parser('delete', help='Delete an app')
    delete_parser.add_argument('app_id', help='App identifier')
    delete_parser.add_argument('--force', '-f', action='store_true',
                              help='Skip confirmation')
    
    # Show summary
    subparsers.add_parser('summary', help='Show storage summary')
    
    # Optimize storage
    optimize_parser = subparsers.add_parser('optimize', help='Optimize storage')
    optimize_parser.add_argument('--no-prompt', action='store_true',
                                help='Skip deletion prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = AppStorageManager(args.config)
    
    # Execute command
    commands = {
        'add': cmd_add,
        'use': cmd_use,
        'list': cmd_list,
        'unused': cmd_unused,
        'junk': cmd_junk,
        'pause': cmd_pause,
        'delete': cmd_delete,
        'summary': cmd_summary,
        'optimize': cmd_optimize
    }
    
    if args.command in commands:
        commands[args.command](args, manager)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
