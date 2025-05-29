"""
وحدة تحسين الأداء للتطبيق.
توفر وظائف لتحسين الأداء وتقليل استهلاك الموارد.
"""

import os
import time
import logging
import functools
import threading
import multiprocessing
from flask import request, current_app, g
import gzip
import pickle
from werkzeug.contrib.cache import SimpleCache

logger = logging.getLogger(__name__)

# إنشاء ذاكرة تخزين مؤقت بسيطة
cache = SimpleCache(threshold=1000, default_timeout=300)

def setup_performance_optimization(app):
    """
    إعداد تحسينات الأداء للتطبيق.
    
    المعلمات:
        app (Flask): تطبيق Flask.
    """
    # إضافة ضغط الاستجابة
    if app.config.get('ENABLE_COMPRESSION', True):
        import flask_compress
        flask_compress.Compress(app)
    
    # إضافة وظيفة لتتبع استخدام الذاكرة
    @app.before_request
    def track_memory_usage():
        """تتبع استخدام الذاكرة قبل معالجة الطلب."""
        if app.config.get('TRACK_MEMORY_USAGE', False):
            import psutil
            process = psutil.Process(os.getpid())
            g.memory_before = process.memory_info().rss
    
    # إضافة وظيفة لتسجيل استخدام الذاكرة بعد الانتهاء
    @app.after_request
    def log_memory_usage(response):
        """تسجيل استخدام الذاكرة بعد معالجة الطلب."""
        if app.config.get('TRACK_MEMORY_USAGE', False) and hasattr(g, 'memory_before'):
            import psutil
            process = psutil.Process(os.getpid())
            memory_after = process.memory_info().rss
            memory_diff = memory_after - g.memory_before
            logger.debug(f"استخدام الذاكرة: {memory_diff / 1024 / 1024:.2f} ميجابايت")
        return response
    
    return app

def cache_result(timeout=300):
    """
    مزخرف لتخزين نتائج الدالة في ذاكرة التخزين المؤقت.
    
    المعلمات:
        timeout (int): مدة صلاحية التخزين المؤقت بالثواني.
    
    العائد:
        function: الدالة المزخرفة.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # محاولة استرداد النتيجة من التخزين المؤقت
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"تم استرداد النتيجة من التخزين المؤقت: {cache_key}")
                return result
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"تم تخزين النتيجة في التخزين المؤقت: {cache_key}")
            return result
        return wrapper
    return decorator

def disk_cache(base_path, timeout=3600):
    """
    مزخرف لتخزين نتائج الدالة على القرص.
    
    المعلمات:
        base_path (str): المسار الأساسي لملفات التخزين المؤقت.
        timeout (int): مدة صلاحية التخزين المؤقت بالثواني.
    
    العائد:
        function: الدالة المزخرفة.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            import hashlib
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # إنشاء مسار ملف التخزين المؤقت
            os.makedirs(base_path, exist_ok=True)
            cache_file = os.path.join(base_path, f"{cache_key}.cache")
            
            # التحقق من وجود ملف التخزين المؤقت وصلاحيته
            if os.path.exists(cache_file):
                file_age = time.time() - os.path.getmtime(cache_file)
                if file_age < timeout:
                    try:
                        with gzip.open(cache_file, 'rb') as f:
                            result = pickle.load(f)
                        logger.debug(f"تم استرداد النتيجة من التخزين المؤقت على القرص: {cache_key}")
                        return result
                    except Exception as e:
                        logger.warning(f"فشل استرداد النتيجة من التخزين المؤقت على القرص: {str(e)}")
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            try:
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
                logger.debug(f"تم تخزين النتيجة في التخزين المؤقت على القرص: {cache_key}")
            except Exception as e:
                logger.warning(f"فشل تخزين النتيجة في التخزين المؤقت على القرص: {str(e)}")
            return result
        return wrapper
    return decorator

def run_in_thread(func):
    """
    مزخرف لتنفيذ الدالة في خيط منفصل.
    
    المعلمات:
        func (function): الدالة المراد تنفيذها.
    
    العائد:
        function: الدالة المزخرفة.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

def run_in_process(func):
    """
    مزخرف لتنفيذ الدالة في عملية منفصلة.
    
    المعلمات:
        func (function): الدالة المراد تنفيذها.
    
    العائد:
        function: الدالة المزخرفة.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
        process.daemon = True
        process.start()
        return process
    return wrapper

def optimize_ffmpeg_command(command, preset=None, threads=None):
    """
    تحسين أمر FFmpeg لتقليل استهلاك الموارد.
    
    المعلمات:
        command (list): أمر FFmpeg.
        preset (str, اختياري): إعداد الترميز المسبق.
        threads (int, اختياري): عدد الخيوط.
    
    العائد:
        list: أمر FFmpeg المحسن.
    """
    # نسخ الأمر الأصلي
    optimized_command = command.copy()
    
    # إضافة إعداد الترميز المسبق
    if preset and '-preset' not in ' '.join(command):
        preset_index = optimized_command.index('-c:v') + 2 if '-c:v' in optimized_command else 1
        optimized_command[preset_index:preset_index] = ['-preset', preset]
    
    # إضافة عدد الخيوط
    if threads and '-threads' not in ' '.join(command):
        optimized_command.insert(1, '-threads')
        optimized_command.insert(2, str(threads))
    
    # إضافة خيارات أخرى لتحسين الأداء
    if '-movflags' not in ' '.join(command):
        optimized_command.extend(['-movflags', '+faststart'])
    
    return optimized_command

def limit_cpu_usage(percent=80):
    """
    تحديد استخدام وحدة المعالجة المركزية.
    
    المعلمات:
        percent (int): النسبة المئوية القصوى لاستخدام وحدة المعالجة المركزية.
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        process.cpu_percent(interval=0.1)
        
        while True:
            cpu_percent = process.cpu_percent(interval=0.1)
            if cpu_percent > percent:
                time.sleep(0.1)
            else:
                break
    except ImportError:
        logger.warning("لم يتم العثور على مكتبة psutil، لا يمكن تحديد استخدام وحدة المعالجة المركزية")
    except Exception as e:
        logger.warning(f"فشل تحديد استخدام وحدة المعالجة المركزية: {str(e)}")

def cleanup_temp_files(directory, max_age=3600):
    """
    تنظيف الملفات المؤقتة.
    
    المعلمات:
        directory (str): مسار المجلد المؤقت.
        max_age (int): العمر الأقصى للملفات بالثواني.
    """
    try:
        if not os.path.exists(directory):
            return
        
        current_time = time.time()
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age:
                    os.remove(file_path)
                    logger.debug(f"تم حذف الملف المؤقت: {file_path}")
    except Exception as e:
        logger.warning(f"فشل تنظيف الملفات المؤقتة: {str(e)}")

@run_in_thread
def schedule_cleanup(directory, interval=3600, max_age=86400):
    """
    جدولة تنظيف الملفات المؤقتة.
    
    المعلمات:
        directory (str): مسار المجلد المؤقت.
        interval (int): الفاصل الزمني بين عمليات التنظيف بالثواني.
        max_age (int): العمر الأقصى للملفات بالثواني.
    """
    while True:
        cleanup_temp_files(directory, max_age)
        time.sleep(interval)
