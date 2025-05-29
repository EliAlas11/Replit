import os
import sys
import platform
import subprocess
from flask import Flask, jsonify

def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = ['flask', 'pytube', 'moviepy', 'opencv-python-headless']
    installed_packages = []
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            installed_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    return {
        'installed': installed_packages,
        'missing': missing_packages
    }

def check_file_permissions():
    """Check if the application has necessary file permissions."""
    folders_to_check = [
        'uploads',
        'processed',
        'assets/sounds'
    ]
    
    results = {}
    
    for folder in folders_to_check:
        folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
        
        if not os.path.exists(folder_path):
            results[folder] = {
                'exists': False,
                'readable': False,
                'writable': False
            }
            continue
        
        results[folder] = {
            'exists': True,
            'readable': os.access(folder_path, os.R_OK),
            'writable': os.access(folder_path, os.W_OK)
        }
    
    return results

def run_compatibility_tests():
    """Run all server-side compatibility tests."""
    return {
        'system': {
            'os': platform.system(),
            'python_version': sys.version,
            'platform': platform.platform()
        },
        'ffmpeg': check_ffmpeg(),
        'python_packages': check_python_packages(),
        'file_permissions': check_file_permissions()
    }

# Create a route to run compatibility tests
def add_compatibility_route(app):
    @app.route('/api/compatibility-test', methods=['GET'])
    def compatibility_test():
        results = run_compatibility_tests()
        return jsonify(results)

# Run tests directly if script is executed
if __name__ == '__main__':
    results = run_compatibility_tests()
    print(results)
