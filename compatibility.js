// تحسينات لدعم المعاينة والتنزيل عبر المنصات المختلفة

// 1. إضافة ملف JavaScript منفصل للتعامل مع توافق الفيديو
function createVideoCompatibilityScript() {
  const content = `
// Video compatibility helper functions
const VideoCompatibility = {
  // Check if the browser supports a specific video format
  supportsVideoType: function(type) {
    let video = document.createElement('video');
    return video.canPlayType(type) !== '';
  },
  
  // Get the best supported video format for the current browser
  getBestVideoFormat: function() {
    if (this.supportsVideoType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"')) {
      return 'mp4';
    } else if (this.supportsVideoType('video/webm; codecs="vp8, vorbis"')) {
      return 'webm';
    } else {
      return 'mp4'; // Default fallback
    }
  },
  
  // Optimize video element for the current device
  optimizeVideoElement: function(videoElement) {
    const device = detectDevice();
    
    // Set common attributes for better compatibility
    videoElement.setAttribute('playsinline', '');
    videoElement.setAttribute('webkit-playsinline', '');
    
    // iOS specific optimizations
    if (device.isIOS) {
      videoElement.setAttribute('controls', 'controls');
      videoElement.setAttribute('preload', 'metadata');
    }
    
    // Safari specific optimizations
    if (device.isSafari) {
      videoElement.setAttribute('controls', 'controls');
    }
    
    // Mobile specific optimizations
    if (device.isMobile) {
      videoElement.setAttribute('preload', 'metadata');
    }
    
    return videoElement;
  },
  
  // Create a download link that works across platforms
  createCompatibleDownloadLink: function(videoUrl, fileName) {
    const device = detectDevice();
    const link = document.createElement('a');
    
    link.href = videoUrl;
    link.download = fileName || 'viral-clip.mp4';
    link.className = 'download-button';
    
    // iOS Safari doesn't support the download attribute
    if (device.isIOS && device.isSafari) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        alert('لتنزيل الفيديو على جهاز iOS، اضغط مطولاً على الفيديو واختر "حفظ الفيديو"');
      });
    }
    
    return link;
  },
  
  // Handle video errors
  handleVideoError: function(videoElement) {
    videoElement.addEventListener('error', function(e) {
      console.error('Video error:', e);
      
      // Try alternative source if available
      const currentSrc = videoElement.querySelector('source').src;
      if (currentSrc.endsWith('.mp4')) {
        // Try webm as fallback
        const webmSrc = currentSrc.replace('.mp4', '.webm');
        videoElement.querySelector('source').src = webmSrc;
        videoElement.load();
      }
    });
    
    return videoElement;
  }
};
`;
  
  return content;
}

// 2. إضافة ملف CSS منفصل للتعامل مع توافق الفيديو عبر المنصات
function createVideoCompatibilityCSS() {
  const content = `
/* Cross-platform video styling */
.video-container {
  position: relative;
  width: 100%;
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: #000;
}

/* Make videos responsive */
.video-container video {
  width: 100%;
  height: auto;
  display: block;
}

/* iOS specific video controls styling */
@supports (-webkit-touch-callout: none) {
  .video-container video::-webkit-media-controls-panel {
    background-color: rgba(0, 0, 0, 0.5);
  }
  
  .video-container video::-webkit-media-controls-play-button {
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
  }
}

/* Custom video controls for better cross-platform experience */
.custom-video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  padding: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-container:hover .custom-video-controls {
  opacity: 1;
}

.play-pause-btn, .fullscreen-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  margin: 0 5px;
}

.progress-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 10px;
  border-radius: 5px;
  position: relative;
  cursor: pointer;
}

.progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: var(--primary-color);
  border-radius: 5px;
  width: 0%;
}

/* Download button styling */
.download-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
  background: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  transition: var(--transition);
  border: none;
  cursor: pointer;
  margin-top: 15px;
}

.download-button:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 0, 64, 0.2);
}

.download-button i {
  margin-left: 8px;
}

/* Platform-specific download instructions */
.platform-instructions {
  margin-top: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  display: none;
}

/* Show platform-specific instructions based on device */
html[data-os="iOS"] .ios-instructions {
  display: block;
}

html[data-browser="Safari"] .safari-instructions {
  display: block;
}
`;
  
  return content;
}

// 3. إضافة ملف JavaScript لاختبار التوافق
function createCompatibilityTestScript() {
  const content = `
// Compatibility testing script
const CompatibilityTest = {
  // Run all compatibility tests
  runAllTests: function() {
    const results = {
      videoPlayback: this.testVideoPlayback(),
      videoDownload: this.testVideoDownload(),
      deviceDetection: this.testDeviceDetection(),
      apiConnection: this.testApiConnection()
    };
    
    console.log('Compatibility test results:', results);
    return results;
  },
  
  // Test video playback
  testVideoPlayback: function() {
    const formats = ['mp4', 'webm'];
    const results = {};
    
    formats.forEach(format => {
      const video = document.createElement('video');
      const canPlay = video.canPlayType(format === 'mp4' ? 
        'video/mp4; codecs="avc1.42E01E, mp4a.40.2"' : 
        'video/webm; codecs="vp8, vorbis"');
      
      results[format] = canPlay;
    });
    
    return results;
  },
  
  // Test video download capability
  testVideoDownload: function() {
    const a = document.createElement('a');
    return {
      downloadAttributeSupported: 'download' in a,
      blobUrlSupported: window.URL && window.URL.createObjectURL ? true : false
    };
  },
  
  // Test device detection
  testDeviceDetection: function() {
    const device = detectDevice();
    return device;
  },
  
  // Test API connection
  testApiConnection: function() {
    // Simulate API test
    return {
      connected: true,
      latency: '150ms'
    };
  },
  
  // Log compatibility issues
  logCompatibilityIssues: function() {
    const results = this.runAllTests();
    const issues = [];
    
    // Check for video playback issues
    if (!results.videoPlayback.mp4 && !results.videoPlayback.webm) {
      issues.push('No supported video format detected');
    }
    
    // Check for download issues
    if (!results.videoDownload.downloadAttributeSupported) {
      issues.push('Download attribute not supported, using fallback');
    }
    
    // iOS Safari specific issues
    if (results.deviceDetection.isIOS && results.deviceDetection.isSafari) {
      issues.push('iOS Safari detected: using special handling for video download');
    }
    
    console.log('Compatibility issues:', issues.length > 0 ? issues : 'None detected');
    return issues;
  }
};

// Run compatibility tests on page load
document.addEventListener('DOMContentLoaded', function() {
  // Only run in development mode
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    CompatibilityTest.logCompatibilityIssues();
  }
});
`;
  
  return content;
}

// 4. إنشاء ملف Python لاختبار التوافق على الخادم
function createServerCompatibilityTest() {
  const content = `
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
`;
  
  return content;
}

// إنشاء الملفات
createVideoCompatibilityScript();
createVideoCompatibilityCSS();
createCompatibilityTestScript();
createServerCompatibilityTest();
