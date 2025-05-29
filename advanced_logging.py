"""
وحدة تسجيل متقدمة للتطبيق.
توفر إعدادات وتكوينات متقدمة للتسجيل البرمجي.
"""

import os
import logging
import logging.handlers
import time
import json
from flask import request, g, has_request_context
from datetime import datetime

class RequestFormatter(logging.Formatter):
    """
    منسق مخصص للتسجيل يضيف معلومات الطلب.
    """
    
    def format(self, record):
        """
        تنسيق سجل التسجيل مع إضافة معلومات الطلب.
        
        المعلمات:
            record (LogRecord): سجل التسجيل.
        
        العائد:
            str: السجل المنسق.
        """
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.path = request.path
            
            # إضافة معرف الطلب إذا كان متاحًا
            if hasattr(g, 'request_id'):
                record.request_id = g.request_id
            else:
                record.request_id = 'no-request-id'
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.path = None
            record.request_id = 'no-request-context'
        
        return super().format(record)

class JsonFormatter(logging.Formatter):
    """
    منسق JSON للتسجيل.
    """
    
    def format(self, record):
        """
        تنسيق سجل التسجيل كـ JSON.
        
        المعلمات:
            record (LogRecord): سجل التسجيل.
        
        العائد:
            str: سلسلة JSON.
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # إضافة معلومات الطلب إذا كانت متاحة
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'url'):
            log_data['url'] = record.url
        if hasattr(record, 'remote_addr'):
            log_data['remote_addr'] = record.remote_addr
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        
        # إضافة معلومات الاستثناء إذا كانت متاحة
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1])
            }
        
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging(app):
    """
    إعداد التسجيل للتطبيق.
    
    المعلمات:
        app (Flask): تطبيق Flask.
    """
    # الحصول على مستوى التسجيل من التكوين
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # إنشاء مسار ملف التسجيل
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)
    
    # إعداد منسق التسجيل
    if app.config.get('LOG_FORMAT_JSON', False):
        formatter = JsonFormatter()
    else:
        formatter = RequestFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
        )
    
    # إعداد مسجل الملف
    file_handler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10485760,  # 10 ميجابايت
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # إعداد مسجل وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # إعداد مسجل الجذر
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # إزالة المسجلات الموجودة
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # إضافة المسجلات الجديدة
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # تعطيل مسجل Werkzeug الافتراضي في وضع الإنتاج
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # تسجيل بدء التطبيق
    app.logger.info(f"تم بدء التطبيق في وضع {app.config['ENV']}")
    
    # إضافة وظيفة لتعيين معرف الطلب
    @app.before_request
    def set_request_id():
        """تعيين معرف فريد لكل طلب."""
        import uuid
        g.request_id = str(uuid.uuid4())
        g.request_start_time = time.time()
    
    # إضافة وظيفة لتسجيل معلومات الطلب بعد الانتهاء
    @app.after_request
    def log_request_info(response):
        """تسجيل معلومات الطلب بعد الانتهاء."""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            app.logger.info(
                f"طلب {request.method} {request.path} - الحالة: {response.status_code} - المدة: {duration:.4f}s"
            )
        return response
    
    return app
