#!/usr/bin/env python3
"""
Enhanced Performance Tracking Module
====================================
Performance tracking utilities for the Photochop Progress Analyzer

Copyright (c) 2025
Licensed under MIT License
"""

import time
import json
import os
from datetime import datetime, timedelta
import psutil

def get_system_resources():
    """Get current system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        ram_used_gb = memory.used / (1024**3)
        ram_total_gb = memory.total / (1024**3)
        
        # Try to get GPU usage (basic attempt)
        gpu_usage = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
        except ImportError:
            pass
        
        return {
            'cpu_percent': cpu_percent,
            'ram_percent': ram_percent,
            'ram_used_gb': ram_used_gb,
            'ram_total_gb': ram_total_gb,
            'gpu_percent': gpu_usage
        }
    except Exception:
        return None

def calculate_processing_speed(log_data):
    """Calculate processing speed based on running average of last 5 completed folders"""
    
    # Check if we have individual folder completion data
    completed_folders = log_data.get('completed_folders', [])
    
    if len(completed_folders) < 2:
        # Fall back to session-based calculation if no individual folder data
        return calculate_processing_speed_legacy(log_data)
    
    # Get the most recent folder completions (up to 5)
    recent_completions = completed_folders[-5:] if len(completed_folders) >= 5 else completed_folders
    
    if len(recent_completions) < 2:
        return None
    
    # Calculate time differences between consecutive folder completions
    processing_times = []
    
    for i in range(1, len(recent_completions)):
        current_completion = recent_completions[i]
        previous_completion = recent_completions[i-1]
        
        try:
            current_time = datetime.fromisoformat(current_completion['completion_time'])
            previous_time = datetime.fromisoformat(previous_completion['completion_time'])
            
            time_diff_seconds = (current_time - previous_time).total_seconds()
            
            # Only include reasonable processing times (between 10 seconds and 10 minutes per folder)
            if 10 <= time_diff_seconds <= 600:
                processing_times.append(time_diff_seconds)
                
        except (ValueError, KeyError) as e:
            continue  # Skip invalid timestamps
    
    if not processing_times:
        return None
    
    # Calculate running average processing time
    avg_processing_time_seconds = sum(processing_times) / len(processing_times)
    avg_processing_time_minutes = avg_processing_time_seconds / 60
    
    # Calculate speeds
    folders_per_minute = 1 / avg_processing_time_minutes if avg_processing_time_minutes > 0 else 0
    folders_per_hour = folders_per_minute * 60
    
    return {
        'folders_per_minute': folders_per_minute,
        'folders_per_hour': folders_per_hour,
        'minutes_per_folder': avg_processing_time_minutes,
        'seconds_per_folder': avg_processing_time_seconds,
        'samples_count': len(processing_times),
        'recent_times': processing_times[-3:],  # Last 3 processing times in seconds
        'calculation_method': 'individual_folders',
        'folders_used': len(recent_completions)
    }

def calculate_processing_speed_legacy(log_data):
    """Legacy processing speed calculation based on session data"""
    sessions = log_data.get('sessions', [])
    if len(sessions) < 2:
        return None
    
    # Get last 5 sessions with progress
    progress_sessions = []
    for session in reversed(sessions):
        if len(progress_sessions) >= 5:
            break
        if session.get('processed_count', 0) > 0:
            progress_sessions.append(session)
    
    if len(progress_sessions) < 2:
        return None
    
    # Calculate time differences and folder differences
    speed_samples = []
    for i in range(len(progress_sessions) - 1):
        current = progress_sessions[i]
        previous = progress_sessions[i + 1]
        
        current_time = datetime.fromisoformat(current['timestamp'])
        previous_time = datetime.fromisoformat(previous['timestamp'])
        
        time_diff = (current_time - previous_time).total_seconds() / 60  # minutes
        folder_diff = current['processed_count'] - previous['processed_count']
        
        if time_diff > 0 and folder_diff > 0:
            folders_per_minute = folder_diff / time_diff
            speed_samples.append(folders_per_minute)
    
    if not speed_samples:
        return None
    
    # Average speed over samples
    avg_speed = sum(speed_samples) / len(speed_samples)
    return {
        'folders_per_minute': avg_speed,
        'folders_per_hour': avg_speed * 60,
        'minutes_per_folder': 1 / avg_speed if avg_speed > 0 else None,
        'samples_count': len(speed_samples),
        'recent_speeds': speed_samples[:3],  # Last 3 speed samples
        'calculation_method': 'legacy_sessions'
    }

def estimate_completion_time(current_processed, total_folders, processing_speed):
    """Estimate time to completion based on current speed"""
    if not processing_speed or processing_speed['folders_per_minute'] <= 0:
        return None
    
    remaining_folders = total_folders - current_processed
    if remaining_folders <= 0:
        return {'eta': 'Complete!', 'remaining_minutes': 0}
    
    speed = processing_speed['folders_per_minute']
    remaining_minutes = remaining_folders / speed
    
    eta_time = datetime.now() + timedelta(minutes=remaining_minutes)
    
    # Format ETA nicely
    if remaining_minutes < 60:
        eta_str = f"{int(remaining_minutes)}m"
    elif remaining_minutes < 1440:  # 24 hours
        hours = int(remaining_minutes // 60)
        minutes = int(remaining_minutes % 60)
        eta_str = f"{hours}h {minutes}m"
    else:
        days = int(remaining_minutes // 1440)
        hours = int((remaining_minutes % 1440) // 60)
        eta_str = f"{days}d {hours}h"
    
    return {
        'eta': eta_str,
        'eta_time': eta_time.strftime('%H:%M'),
        'remaining_minutes': remaining_minutes,
        'remaining_folders': remaining_folders
    }

def analyze_speed_trend(processing_speed, log_data):
    """Analyze if processing speed is increasing, decreasing, or steady"""
    if not processing_speed or len(processing_speed.get('recent_speeds', [])) < 2:
        return None
    
    recent_speeds = processing_speed['recent_speeds']
    current_speed = recent_speeds[0]
    
    # Compare with previous speeds
    if len(recent_speeds) >= 3:
        previous_avg = sum(recent_speeds[1:]) / len(recent_speeds[1:])
    else:
        previous_avg = recent_speeds[-1]
    
    speed_change = ((current_speed - previous_avg) / previous_avg) * 100
    
    if abs(speed_change) < 10:  # Less than 10% change
        trend = 'steady'
        trend_icon = 'STEADY'
        trend_color = '\033[92m'  # Green
    elif speed_change > 10:
        trend = 'increasing'
        trend_icon = 'UP'
        trend_color = '\033[94m'  # Blue
    else:
        trend = 'decreasing'
        trend_icon = 'DOWN'
        trend_color = '\033[93m'  # Yellow
    
    return {
        'trend': trend,
        'change_percent': speed_change,
        'icon': trend_icon,
        'color': trend_color,
        'current_speed': current_speed,
        'previous_speed': previous_avg
    }

def save_enhanced_progress_log(data):
    """Enhanced progress logging with speed tracking and file-level detection"""
    if not data:
        return None, None, None, None, None
        
    log_file = 'photoshop_progress_log.json'
    
    # Load existing log or create new with better error handling
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {
                'sessions': [], 
                'last_progress_time': None, 
                'last_progress_count': 0,
                'last_gen_files_count': 0,
                'speed_history': []
            }
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        # If JSON is corrupted, start fresh
        print(f"[WARNING] Progress log corrupted, creating fresh log: {e}")
        log_data = {
            'sessions': [], 
            'last_progress_time': None, 
            'last_progress_count': 0,
            'last_gen_files_count': 0,
            'speed_history': []
        }
    
    # Calculate total gen- files across all folders
    total_gen_files = sum(folder.get('gen_files', 0) for folder in data.get('processed_folders', []) + data.get('unprocessed_folders', []))
    
    # Check if progress was made - folder OR file level
    current_count = data['processed_count']
    last_count = log_data.get('last_progress_count', 0)
    last_gen_count = log_data.get('last_gen_files_count', 0)
    current_time = datetime.now().isoformat()
    
    # Progress detected if more folders completed OR more gen- files created
    folder_progress = current_count > last_count
    file_progress = total_gen_files > last_gen_count
    first_run = log_data.get('last_progress_time') is None
    
    progress_made = folder_progress or file_progress or first_run
    
    if progress_made:
        # Update progress tracking
        log_data['last_progress_time'] = current_time
        log_data['last_progress_count'] = current_count
        log_data['last_gen_files_count'] = total_gen_files
    
    # Add current session with system resources
    system_resources = get_system_resources()
    session_data = {
        'timestamp': data['timestamp'],
        'progress_percent': data['progress_percent'],
        'processed_count': data['processed_count'],
        'total_folders': data['total_folders'],
        'total_gen_files': total_gen_files,
        'system_resources': system_resources
    }
    
    log_data['sessions'].append(session_data)
    
    # Keep only last 100 entries for performance
    log_data['sessions'] = log_data['sessions'][-100:]
    
    # Calculate processing speed
    processing_speed = calculate_processing_speed(log_data)
    if processing_speed:
        if 'speed_history' not in log_data:
            log_data['speed_history'] = []
        log_data['speed_history'].append({
            'timestamp': current_time,
            'speed': processing_speed['folders_per_minute']
        })
        log_data['speed_history'] = log_data['speed_history'][-20:]  # Keep last 20 speed records
    
    # Save updated log with error handling
    try:
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    except (PermissionError, OSError) as e:
        print(f"[ERROR] Could not save progress log: {e}")
        # Continue without saving rather than crashing
    
    # Calculate ETA and speed trend
    eta_info = None
    speed_trend = None
    
    if processing_speed:
        eta_info = estimate_completion_time(
            data['processed_count'], 
            data['total_folders'], 
            processing_speed
        )
        speed_trend = analyze_speed_trend(processing_speed, log_data)
    
    return log_data.get('last_progress_time'), processing_speed, eta_info, speed_trend, system_resources
