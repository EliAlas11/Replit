"""
نقطة البداية الرئيسية لتطبيق Flask.
يقوم بإنشاء وتهيئة تطبيق Flask وتسجيل جميع نقاط النهاية API.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix
import concurrent.futures

from .config.config import config

def create_app(config_name=None):
    """
    إنشاء وتهيئة تطبيق Flask.
    
    المعلمات:
        config_name (str): اسم التكوين المراد استخدامه ('development', 'testing', 'production').
                          إذا لم يتم تحديده، يتم استخدام متغير البيئة FLASK_CONFIG أو 'default'.
    
    العائد:
        Flask: تطبيق Flask مهيأ.
    """
    # تحديد التكوين المناسب
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # إنشاء تطبيق Flask
    app = Flask(__name__)
    
    # تطبيق التكوين
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # إعداد التسجيل
    setup_logging(app)
    
    # إعداد CORS للسماح بالطلبات من أصول مختلفة
    CORS(app)
    
    # إعداد ضغط الاستجابات
    Compress(app)
    
    # إصلاح رؤوس البروكسي
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # إنشاء مجمع الخيوط للعمليات المتوازية
    app.executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=app.config['THREAD_POOL_SIZE']
    )
    
    # تسجيل نقاط النهاية
    register_blueprints(app)
    
    # إضافة رؤوس التخزين المؤقت
    @app.after_request
    def add_cache_headers(response):
        # تخزين مؤقت للموارد الثابتة
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        # تخزين مؤقت قصير للصفحات الديناميكية
        else:
            response.headers['Cache-Control'] = 'public, max-age=60'
        
        return response
    
    # تنظيف الموارد عند إغلاق التطبيق
    @app.teardown_appcontext
    def cleanup_resources(exception=None):
        app.logger.debug("تنظيف الموارد عند إغلاق التطبيق")
    
    return app

def setup_logging(app):
    """
    إعداد التسجيل للتطبيق.
    
    المعلمات:
        app (Flask): تطبيق Flask.
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    log_format = app.config['LOG_FORMAT']
    log_file = app.config['LOG_FILE']
    
    # إعداد مسجل الملف
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(log_level)
    
    # إعداد مسجل وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(log_level)
    
    # إضافة المسجلات إلى تطبيق Flask
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # تعطيل مسجل Werkzeug الافتراضي في وضع الإنتاج
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    app.logger.info(f"تم بدء التطبيق في وضع {app.config['ENV']}")

def register_blueprints(app):
    """
    تسجيل جميع مخططات API في التطبيق.
    
    المعلمات:
        app (Flask): تطبيق Flask.
    """
    # استيراد مخططات API
    from .api.video import video_bp
    from .api.youtube import youtube_bp
    from .api.device import device_bp
    
    # تسجيل المخططات
    app.register_blueprint(video_bp, url_prefix='/api/video')
    app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
    app.register_blueprint(device_bp, url_prefix='/api/device')
    
    # تسجيل مسار الصفحة الرئيسية
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # تسجيل مسار حالة API
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'online',
            'version': '1.0.0',
            'environment': app.config['ENV']
        })
    
    app.logger.info("تم تسجيل جميع مخططات API")

# استيراد الوحدات المطلوبة لتسجيل المسارات
from flask import jsonify, render_template, request

# إنشاء تطبيق باستخدام التكوين الافتراضي
app = create_app()

if __name__ == '__main__':
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000)
