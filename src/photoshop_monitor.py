#!/usr/bin/env python3
"""
Photochop Progress Analyzer
===========================
Real-time CLI monitoring system for Photoshop generative expand operations
with colorized output, progress bars, and detailed folder-by-folder analysis.

Copyright (c) 2025
Licensed under MIT License
"""

import os
import time
import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import psutil  # For system resource monitoring
import tkinter as tk
from tkinter import filedialog, messagebox

# Import our performance tracking functions
try:
    from performance_tracker import (
        save_enhanced_progress_log, 
        get_system_resources,
        analyze_speed_trend
    )
    PERFORMANCE_TRACKING = True
except ImportError:
    PERFORMANCE_TRACKING = False

# Color codes for Windows console
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_GREEN = '\033[102m'
    BG_RED = '\033[101m'
    BG_YELLOW = '\033[103m'

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

# Configuration management
CONFIG_FILE = "monitor_config.json"
DEFAULT_CONFIG = {
    "base_path": os.path.expanduser("~/Downloads"),
    "last_update": None
}

def load_config():
    """Load configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f) 
                # Ensure all required keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not load config ({e}), using defaults{Colors.RESET}")
    
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to JSON file"""
    try:
        # Normalize path to OS format
        if "base_path" in config:
            config["base_path"] = os.path.normpath(config["base_path"])
        
        config["last_update"] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Colors.RED}Error saving config: {e}{Colors.RESET}")
        return False

def select_folder():
    """Open folder picker dialog and update config"""
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Bring to front
        
        # Load current config to set initial directory
        config = load_config()
        initial_dir = config.get("base_path", "")
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")  # Default to home directory
        
        print(f"{Colors.CYAN}Opening folder picker dialog...{Colors.RESET}")
        print(f"{Colors.GRAY}   Current path: {config['base_path']}{Colors.RESET}")
        print(f"{Colors.YELLOW}   Please select the folder containing subfolders to monitor{Colors.RESET}")
        print()
        
        # Open folder picker
        selected_path = filedialog.askdirectory(
            title="Select Folder to Monitor for gen- files",
            initialdir=initial_dir
        )
        
        root.destroy()
        
        if selected_path:
            # Validate the selected path
            if not os.path.exists(selected_path):
                print(f"{Colors.RED}Selected path does not exist: {selected_path}{Colors.RESET}")
                return False
            
            # Update config
            config["base_path"] = os.path.normpath(selected_path)
            if save_config(config):
                print(f"{Colors.GREEN}Successfully updated monitored path:{Colors.RESET}")
                print(f"{Colors.CYAN}   New path: {os.path.normpath(selected_path)}{Colors.RESET}")
                
                # Quick scan to show what we'll be monitoring
                quick_scan_info(selected_path)
                return True
            else:
                print(f"{Colors.RED}Failed to save configuration{Colors.RESET}")
                return False
        else:
            print(f"{Colors.YELLOW}No folder selected, keeping current path{Colors.RESET}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}Error in folder selection: {e}{Colors.RESET}")
        return False

def quick_scan_info(path):
    """Show quick info about what will be monitored in the selected path"""
    try:
        if not os.path.exists(path):
            return
            
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        total_folders = len(subdirs)
        
        # Count processed folders quickly
        processed_count = 0
        for folder_name in subdirs[:50]:  # Check first 50 for speed
            folder_path = os.path.join(path, folder_name)
            try:
                files = os.listdir(folder_path)
                gen_files = [f for f in files if f.startswith('gen-') and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if len(gen_files) > 0:
                    processed_count += 1
            except:
                continue
        
        print(f"{Colors.CYAN}Quick scan results:{Colors.RESET}")
        print(f"   Total subfolders found: {total_folders}")
        if total_folders > 0:
            if total_folders <= 50:
                print(f"   Processed folders: {processed_count}")
                print(f"   Pending folders: {total_folders - processed_count}")
            else:
                print(f"   Processed (first 50): {processed_count}")
                print(f"   Full scan available with monitoring")
            
            # Show some example folders
            example_folders = subdirs[:5]
            print(f"   Example folders: {', '.join(example_folders)}")
        else:
            print(f"   {Colors.YELLOW}No subfolders found to monitor{Colors.RESET}")
        print()
        
    except Exception as e:
        print(f"{Colors.YELLOW}Could not scan folder: {e}{Colors.RESET}")

def print_header():
    """Print fancy header with fixed border"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 80)
    print(f"{'':>20}PHOTOCHOP PROGRESS ANALYZER{'':>21}")
    print(f"{'':>15}Real-time Generative Expand Operation Tracking{'':>16}")
    print("=" * 80)
    print(f"{Colors.RESET}")

def create_progress_bar(current, total, width=50):
    """Create beautiful Unicode progress bar"""
    if total == 0:
        return f"[{'?' * width}] 0%"
    
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    percentage = progress * 100
    
    # Color coding based on progress
    if percentage >= 80:
        color = Colors.GREEN
    elif percentage >= 50:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    return f"{color}[{bar}] {percentage:.1f}%{Colors.RESET}"
def analyze_progress(custom_base_path=None):
    """Analyze current Photoshop operation progress - FLEXIBLE PATH SUPPORT"""
    if custom_base_path:
        base_path = custom_base_path
    else:
        config = load_config()
        base_path = config.get("base_path", DEFAULT_CONFIG["base_path"])
    
    if not os.path.exists(base_path):
        return None
    
    # Auto-detect project structure - look for common patterns
    possible_subdirs = []
    user_folders = []
    
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            possible_subdirs.append((item_path, item))
            # Check if this looks like a user folder (contains image files)
            if item.startswith('user_') or any(f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))):
                user_folders.append((item_path, item))
    
    # Determine monitoring mode based on content
    if user_folders and len(user_folders) >= len(possible_subdirs) * 0.5:
        # Direct monitoring mode - base_path contains user folders to monitor
        projects = [(base_path, "direct_monitoring", "")]
    elif not possible_subdirs:
        # Direct monitoring mode - base_path contains the folders to monitor  
        projects = [(base_path, "direct_monitoring", "")]
    else:
        # Project-based monitoring - base_path contains project subdirectories
        projects = [(path, name, name + "\\") for path, name in possible_subdirs]
    
    processed_folders = []
    unprocessed_folders = []
    empty_folders = []
    total_folders = 0
    
    # Dynamic folder details based on detected projects
    folder_details = {}
    for _, project_name, _ in projects:
        folder_details[project_name] = {'processed': 0, 'total': 0, 'folders': []}
    
    for project_path, category, prefix in projects:
        if not os.path.exists(project_path):
            continue
            
        for folder_name in os.listdir(project_path):
            folder_path = os.path.join(project_path, folder_name)
            
            # Skip if not a directory
            if not os.path.isdir(folder_path):
                continue
                
            total_folders += 1
            rel_path = prefix + folder_name
            
            try:
                files = os.listdir(folder_path)
            except PermissionError:
                continue
            
            if not files:
                empty_folders.append(rel_path)
                continue
            
            # Count only image files
            gen_files = [f for f in files if f.startswith('gen-') and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            original_files = [f for f in files if not f.startswith('gen-') and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not f.endswith('.txt')]
            
            gen_count = len(gen_files)
            original_count = len(original_files)
            total_file_count = len(files)
            
            # SIMPLIFIED LOGIC: ANY gen- files = processed
            is_processed = gen_count > 0
            
            if gen_count > 0:
                completion_status = "processed"
            elif original_count == 0 and gen_count == 0:
                completion_status = "no_images"
            else:
                completion_status = "pending"
            
            folder_info = {
                'path': rel_path,
                'name': folder_name,
                'gen_files': gen_count,
                'original_files': original_count,
                'total_files': total_file_count,
                'processed': is_processed,
                'status': completion_status,
                'completion_ratio': f"{gen_count}/{original_count}" if original_count > 0 else f"{gen_count}/0",
                'project': category
            }
            
            folder_details[category]['total'] += 1
            folder_details[category]['folders'].append(folder_info)
            
            if is_processed:
                processed_folders.append(folder_info)
                folder_details[category]['processed'] += 1
            else:
                unprocessed_folders.append(folder_info)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_folders': total_folders,
        'processed_count': len(processed_folders),
        'unprocessed_count': len(unprocessed_folders),
        'empty_count': len(empty_folders),
        'progress_percent': (len(processed_folders) / total_folders * 100) if total_folders > 0 else 0,
        'processed_folders': processed_folders,
        'unprocessed_folders': unprocessed_folders,
        'empty_folders': empty_folders,
        'categories': folder_details
    }

def print_summary(data):
    """Print progress summary with colors and bars"""
    if not data:
        print(f"{Colors.RED}Could not analyze progress - check path{Colors.RESET}")
        return
    
    print(f"{Colors.BOLD}Operation Summary{Colors.RESET}")
    print(f"Last Update: {Colors.CYAN}{datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
    
    # Show debug info if available
    if data.get('debug_written'):
        print(f"Debug: folder_count_debug.txt updated")
    
    print()
    
    # Overall progress with enhanced info
    total = data['total_folders']
    processed = data['processed_count']
    pending = data['unprocessed_count']
    
    print(f"{Colors.BOLD}Overall Progress{Colors.RESET}")
    progress_bar = create_progress_bar(processed, total)
    print(f"   {progress_bar}")
    print(f"   Processed: {Colors.GREEN}{processed:3d}{Colors.RESET} folders")
    print(f"   Pending:   {Colors.YELLOW}{pending:3d}{Colors.RESET} folders")
    print(f"   Empty:     {Colors.GRAY}{data['empty_count']:3d}{Colors.RESET} folders")
    print(f"   Total:     {Colors.BOLD}{total:3d}{Colors.RESET} folders")
    
    # Show counting validation
    calculated_total = processed + pending + data['empty_count']
    if calculated_total != total:
        print(f"   {Colors.RED}Count mismatch: {calculated_total} vs {total}{Colors.RESET}")
    
    print()
    
    # Category breakdown with enhanced display
    print(f"{Colors.BOLD}Detailed Breakdown{Colors.RESET}")
    
    for category, info in data['categories'].items():
        if info['total'] == 0:
            continue
            
        cat_progress = (info['processed'] / info['total'] * 100) if info['total'] > 0 else 0
        cat_bar = create_progress_bar(info['processed'], info['total'], 30)
        
        print(f"   Project: {category}")
        print(f"      {cat_bar}")
        print(f"      {Colors.GREEN}{info['processed']}{Colors.RESET}/{Colors.BOLD}{info['total']}{Colors.RESET} folders ({cat_progress:.1f}%)")
        print()

def print_recent_activity(data, limit=10):
    """Print recently processed folders with enhanced info"""
    if not data or not data['processed_folders']:
        return
    
    print(f"{Colors.BOLD}Recently Completed{Colors.RESET}")
    
    # Sort by modification time if possible, otherwise show last few
    recent = data['processed_folders'][-limit:] if len(data['processed_folders']) > limit else data['processed_folders']
    
    for folder in recent[-5:]:  # Show last 5
        completion_info = folder.get('completion_ratio', f"{folder['gen_files']}/{folder['total_files']}")
        status_color = Colors.GREEN if folder.get('status') == 'complete' else Colors.YELLOW
        print(f"   {status_color}{folder['path']}{Colors.RESET} ({completion_info} gen/orig)")
    
    if len(data['processed_folders']) > 5:
        print(f"   {Colors.GRAY}... and {len(data['processed_folders']) - 5} more{Colors.RESET}")
    print()

def print_next_pending(data, limit=8):
    """Print next folders to be processed with enhanced info"""
    if not data or not data['unprocessed_folders']:
        print(f"{Colors.GREEN}ALL FOLDERS COMPLETED!{Colors.RESET}")
        return
    
    print(f"{Colors.BOLD}Next in Queue{Colors.RESET}")
    
    for folder in data['unprocessed_folders'][:limit]:
        original_count = folder.get('original_files', folder['total_files'])
        status = folder.get('status', 'pending')
        
        if status == 'partial':
            status_icon = "In progress"
            status_color = Colors.YELLOW
            file_info = f"{folder['gen_files']}/{original_count} processed"
        else:
            status_icon = "Pending"
            status_color = Colors.YELLOW
            file_info = f"{original_count} files to process"
        
        print(f"   {status_color}{folder['path']}{Colors.RESET} ({file_info})")
    
    if len(data['unprocessed_folders']) > limit:
        remaining = len(data['unprocessed_folders']) - limit
        print(f"   {Colors.GRAY}... and {remaining} more pending{Colors.RESET}")
    print()
            'completion_time': current_time,
            'timestamp': current_time
        })
    
    # Keep only the last 50 folder completions for performance
    log_data['completed_folders'] = log_data['completed_folders'][-50:]
    
    # Update last processed folders set
    log_data['last_processed_folders'] = list(current_processed_folders)  # Convert to list for JSON serialization
    
    # Progress detected if:
    # 1. More folders completed, OR
    # 2. More gen- files created (individual file progress), OR
    # 3. This is the first run
    folder_progress = current_count > last_count
    file_progress = total_gen_files > last_gen_count
    first_run = log_data.get('last_progress_time') is None
    
    progress_made = folder_progress or file_progress or first_run or len(newly_completed) > 0
    
    if progress_made:
        # Update the last progress time and counts
        log_data['last_progress_time'] = current_time
        log_data['last_progress_count'] = current_count
        log_data['last_gen_files_count'] = total_gen_files
        
        # Log what type of progress was detected
        if newly_completed:
            print(f"[PROGRESS] New folders completed: {', '.join(newly_completed)}")
        elif folder_progress:
            print(f"[PROGRESS] Folder progress: {last_count} -> {current_count} completed folders")
        elif file_progress:
            print(f"[PROGRESS] File progress: {last_gen_count} -> {total_gen_files} gen- files")
    
    # Add current session with enhanced tracking
    session_entry = {
        'timestamp': data['timestamp'],
        'progress_percent': data['progress_percent'],
        'processed_count': data['processed_count'],
        'total_folders': data['total_folders'],
        'unprocessed_count': data['unprocessed_count'],
        'total_gen_files': total_gen_files,
        'progress_made': progress_made,
        'progress_type': 'folder' if folder_progress else ('file' if file_progress else ('first_run' if first_run else 'none')),
        'newly_completed_count': len(newly_completed)
    }
    
    log_data['sessions'].append(session_entry)
    
    # Keep only last 100 entries
    log_data['sessions'] = log_data['sessions'][-100:]
    
    # Save the updated log
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    return log_data.get('last_progress_time')

def get_stagnation_status():
    """Check if progress has been stagnant and for how long"""
    log_file = 'photoshop_progress_log.json'
    
    if not os.path.exists(log_file):
        return None, None
    
    try:
        with open(log_file, 'r') as f:
            log_data = json.load(f)
        
        last_progress_time = log_data.get('last_progress_time')
        if not last_progress_time:
            return None, None
        
        # Calculate time since last progress
        last_time = datetime.fromisoformat(last_progress_time)
        current_time = datetime.now()
        time_diff = current_time - last_time
        
        minutes_stagnant = time_diff.total_seconds() / 60
        
        return minutes_stagnant, last_progress_time
        
    except Exception:
        return None, None

def print_stagnation_warning(minutes_stagnant, last_progress_time):
    """Print warning banner for stagnant progress"""
    if minutes_stagnant is None or minutes_stagnant < 3:
        return
    
    # Color coding based on severity
    if minutes_stagnant >= 10:
        color = Colors.RED
        severity = "CRITICAL"
        icon = "ALERT"
    elif minutes_stagnant >= 5:
        color = Colors.YELLOW
        severity = "WARNING"
        icon = "WARNING"
    else:
        color = Colors.YELLOW
        severity = "NOTICE"
        icon = "INFO"
    
    print()
    print(f"{color}{Colors.BOLD}")
    print("*" * 80)
    print("*")
    print(f"* {icon}: NO PROGRESS DETECTED FOR {int(minutes_stagnant)} MINUTES")
    print("*")
    
    if last_progress_time:
        last_time_str = datetime.fromisoformat(last_progress_time).strftime('%H:%M:%S')
        print(f"*    Last progress was at: {last_time_str}")
    
    print("*")
    
    if minutes_stagnant >= 10:
        print("*    SUGGESTED ACTIONS:")
        print("*       - Check if Photoshop is still running")
        print("*       - Verify Photoshop isn't waiting for user input")
        print("*       - Check system resources (RAM/GPU)")
        print("*       - Consider restarting the operation")
    elif minutes_stagnant >= 5:
        print("*    CHECK: Photoshop may need attention")
    else:
        print("*    Processing may be slower than usual")
    
    print("*")
    print("*" * 80)
    print(f"{Colors.RESET}")
    print()

def countdown_timer(seconds):
    """Display countdown timer"""
    for i in range(seconds, 0, -1):
        # Clear the line and print countdown
        print(f"\r{Colors.GRAY}Refreshing in {Colors.CYAN}{i:2d}{Colors.GRAY} seconds... {Colors.RESET}", end='', flush=True)
        time.sleep(1)
    print(f"\r{Colors.GREEN}Refreshing now...{' ' * 20}{Colors.RESET}")

def print_progress_analytics(data):
    """Print enhanced progress analytics with accurate speed calculations"""
    if not data:
        return
    
    processed_count = data.get('processed_count', 0)
    total_folders = data.get('total_folders', 0)
    
    if total_folders > 0 and processed_count > 0:
        progress_percent = (processed_count / total_folders) * 100
        remaining_folders = total_folders - processed_count
        
        print(f"{Colors.BOLD}Processing Analytics{Colors.RESET}")
        
        # Load progress log for speed calculation
        try:
            if os.path.exists('photoshop_progress_log.json'):
                with open('photoshop_progress_log.json', 'r') as f:
                    log_data = json.load(f)
                
                # Import performance tracker functions
                if PERFORMANCE_TRACKING:
                    from performance_tracker import calculate_processing_speed, estimate_completion_time, analyze_speed_trend
                    
                    # Calculate processing speed
                    processing_speed = calculate_processing_speed(log_data)
                    
                    if processing_speed:
                        # Display speed information
                        speed = processing_speed['folders_per_minute']
                        time_per_folder = processing_speed.get('seconds_per_folder', 0)
                        method = processing_speed.get('calculation_method', 'unknown')
                        
                        print(f"   Speed: {Colors.CYAN}{speed:.2f} folders/min{Colors.RESET}")
                        
                        if method == 'individual_folders':
                            print(f"   Avg Time: {Colors.YELLOW}{time_per_folder:.0f}s per folder{Colors.RESET}")
                        
                        # Estimate completion time
                        if remaining_folders > 0:
                            eta_info = estimate_completion_time(processed_count, total_folders, processing_speed)
                            if eta_info:
                                eta_str = eta_info['eta']
                                eta_time = eta_info.get('eta_time', '')
                                print(f"   ETA: {Colors.GREEN}{eta_str}{Colors.RESET}", end="")
                                if eta_time:
                                    print(f" {Colors.GRAY}(finishes ~{eta_time}){Colors.RESET}")
                                else:
                                    print()
                        
                        # Speed trend analysis
                        speed_trend = analyze_speed_trend(processing_speed, log_data)
                        if speed_trend and abs(speed_trend.get('change_percent', 0)) > 5:
                            change = speed_trend['change_percent']
                            if change > 0:
                                print(f"   Trend: {Colors.GREEN}+{change:.1f}% faster{Colors.RESET}")
                            else:
                                print(f"   Trend: {Colors.YELLOW}{change:.1f}% slower{Colors.RESET}")
                    
                    else:
                        # Fallback if speed calculation fails
                        if remaining_folders > 0:
                            estimated_minutes = remaining_folders * 1  # 1 minute per folder estimate
                            if estimated_minutes < 60:
                                eta_str = f"{estimated_minutes}m"
                            else:
                                hours = estimated_minutes // 60
                                minutes = estimated_minutes % 60
                                eta_str = f"{hours}h {minutes}m"
                            print(f"   ETA: {Colors.GREEN}{eta_str}{Colors.RESET} {Colors.GRAY}(estimated){Colors.RESET}")
                            
        except Exception as e:
            # Fallback calculation if anything goes wrong
            if remaining_folders > 0:
                estimated_minutes = remaining_folders * 1
                if estimated_minutes < 60:
                    eta_str = f"{estimated_minutes}m"
                else:
                    hours = estimated_minutes // 60
                    minutes = estimated_minutes % 60
                    eta_str = f"{hours}h {minutes}m"
                print(f"   ETA: {Colors.GREEN}{eta_str}{Colors.RESET} {Colors.GRAY}(basic estimate){Colors.RESET}")
        
        print(f"   Remaining: {Colors.CYAN}{remaining_folders}{Colors.RESET} folders")
        print()

def print_system_resources_simple():
    """Print basic system resource usage"""
    try:
        # Get current system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        print(f"{Colors.BOLD}System Resources{Colors.RESET}")
        
        # CPU usage
        if cpu_percent >= 80:
            cpu_color = Colors.RED
            cpu_icon = "HIGH"
        elif cpu_percent >= 60:
            cpu_color = Colors.YELLOW
            cpu_icon = "MED"
        else:
            cpu_color = Colors.GREEN
            cpu_icon = "OK"
        
        print(f"   {cpu_icon} CPU: {cpu_color}{cpu_percent:.1f}%{Colors.RESET}")
        
        # Memory usage
        if memory_percent >= 90:
            mem_color = Colors.RED
            mem_icon = "HIGH"
        elif memory_percent >= 70:
            mem_color = Colors.YELLOW
            mem_icon = "MED"
        else:
            mem_color = Colors.GREEN
            mem_icon = "OK"
        
        print(f"   {mem_icon} RAM: {mem_color}{memory_percent:.1f}%{Colors.RESET} ({memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB)")
        
    except Exception as e:
        print(f"{Colors.BOLD}System Resources{Colors.RESET}")
        print(f"   Unable to get system info: {str(e)}")
    
    print()

def monitor_mode(custom_path=None):
    """Enhanced continuous monitoring mode with custom path support"""
    print(f"{Colors.BOLD}[MONITOR] CONTINUOUS MONITORING MODE{Colors.RESET}")
    print(f"{Colors.GRAY}Press Ctrl+C to exit{Colors.RESET}")
    print()
    
    # Load config for path if not provided
    if not custom_path:
        config = load_config()
        custom_path = config.get("base_path")
    
    try:
        while True:
            clear_screen()
            print_header()
            
            data = analyze_progress(custom_path)
            if data:
                print_summary(data)
                print_progress_analytics(data)
                print_system_resources_simple()
                print_recent_activity(data)
                print_next_pending(data)
                save_progress_log(data)
            else:
                print(f"{Colors.RED}No data found for path: {custom_path}{Colors.RESET}")
                print(f"{Colors.YELLOW}Use option 4 to select a different folder{Colors.RESET}")
                break
            
            # Countdown with status
            for i in range(30, 0, -1):
                print(f"\r{Colors.GRAY}Refreshing in {Colors.CYAN}{i:2d}{Colors.GRAY} seconds... {Colors.RESET}", end="", flush=True)
                time.sleep(1)
            
            print(f"\r{Colors.GREEN}Refreshing now...                    {Colors.RESET}")
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Monitoring stopped by user{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error in monitoring: {e}{Colors.RESET}")

def main():
    """Main function with enhanced diagnostics and command line support"""
    # Enable ANSI color codes on Windows
    if os.name == 'nt':
        os.system('color')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Photochop Progress Analyzer')
    parser.add_argument('--monitor', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--select-folder', action='store_true', help='Select new folder to monitor')
    parser.add_argument('--path', type=str, help='Custom path to monitor (overrides config)')
    
    args = parser.parse_args()
    
    # Handle folder selection
    if args.select_folder:
        clear_screen()
        print_header()
        print(f"{Colors.BOLD}Folder Selection Mode{Colors.RESET}")
        print(f"   Select the folder containing subfolders to monitor for gen- files")
        print()
        
        if select_folder():
            print(f"{Colors.GREEN}Folder selection completed successfully!{Colors.RESET}")
            print(f"{Colors.CYAN}You can now run monitoring with the new path{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Folder selection cancelled or failed{Colors.RESET}")
        return
    
    # Handle monitoring modes
    if args.monitor:
        monitor_mode(args.path)
    else:
        clear_screen()
        print_header()
        
        # Load config and show current path
        config = load_config()
        current_path = args.path if args.path else config.get("base_path", "NOT SET")
        
        print(f"{Colors.BOLD}Current Configuration:{Colors.RESET}")
        print(f"   Base Path: {Colors.CYAN}{current_path}{Colors.RESET}")
        print(f"   Logic: Only count end-level folders (no subdirectories)")
        print(f"   Processed = ANY gen- files found in folder")
        print(f"   Pending = NO gen- files found")
        print()
        
        data = analyze_progress(args.path)
        if data:
            print_summary(data)
            print_progress_analytics(data)
            print_recent_activity(data)
            print_next_pending(data)
            save_progress_log(data)
        else:
            print(f"{Colors.RED}No data found. Check if the path exists and contains folders to monitor.{Colors.RESET}")
            print(f"{Colors.YELLOW}Use option 4 in the batch file to select a different folder{Colors.RESET}")
        
        print(f"{Colors.CYAN}Run with --monitor flag for continuous tracking{Colors.RESET}")

if __name__ == "__main__":
    main()
