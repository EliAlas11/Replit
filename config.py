"""
وحدة التكوين الرئيسية للتطبيق.
تحتوي على جميع إعدادات التكوين للخادم الخلفي.
"""

import os
from pathlib import Path

# المسارات الأساسية
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
CACHE_FOLDER = os.path.join(BASE_DIR, 'cache')
AUDIO_FOLDER = os.path.join(BASE_DIR, 'assets', 'sounds')

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# إعدادات التطبيق
class Config:
    """فئة التكوين الأساسية."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'مفتاح-سري-افتراضي-للتطوير'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 ميجابايت كحد أقصى
    UPLOAD_FOLDER = UPLOAD_FOLDER
    PROCESSED_FOLDER = PROCESSED_FOLDER
    CACHE_FOLDER = CACHE_FOLDER
    AUDIO_FOLDER = AUDIO_FOLDER
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
    
    # إعدادات تنزيل YouTube
    YOUTUBE_DEFAULT_RESOLUTION = '720p'
    YOUTUBE_FALLBACK_RESOLUTION = '480p'
    YOUTUBE_CACHE_DURATION = 86400  # 24 ساعة بالثواني
    
    # إعدادات معالجة الفيديو
    VIDEO_MAX_DURATION = 60  # الحد الأقصى لمدة الفيديو المسموح بها (بالثواني)
    VIDEO_DEFAULT_CLIP_DURATION = 15  # المدة الافتراضية للمقطع (بالثواني)
    VIDEO_ENCODING_PRESET = 'veryfast'  # إعداد ترميز الفيديو (للتوازن بين السرعة والجودة)
    VIDEO_CRF = 23  # عامل معدل الجودة الثابت (أقل = جودة أعلى، مدى: 0-51)
    VIDEO_AUDIO_BITRATE = '128k'  # معدل بت الصوت
    
    # إعدادات التخزين المؤقت
    CACHE_ENABLED = True
    CACHE_MAX_AGE = 86400  # 24 ساعة بالثواني
    CACHE_MAX_SIZE = 100  # الحد الأقصى لعدد العناصر في ذاكرة التخزين المؤقت
    
    # إعدادات التسجيل
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(BASE_DIR, 'app.log')
    
    # إعدادات الأداء
    THREAD_POOL_SIZE = 4  # حجم مجمع الخيوط للعمليات المتوازية
    
    @staticmethod
    def init_app(app):
        """تهيئة التطبيق بإعدادات إضافية."""
        pass

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير."""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """إعدادات بيئة الاختبار."""
    DEBUG = False
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    # استخدام مجلدات مؤقتة للاختبار
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'test_uploads')
    PROCESSED_FOLDER = os.path.join(BASE_DIR, 'test_processed')
    CACHE_FOLDER = os.path.join(BASE_DIR, 'test_cache')
    
    @classmethod
    def init_app(cls, app):
        """تهيئة التطبيق لبيئة الاختبار."""
        Config.init_app(app)
        # إنشاء المجلدات المؤقتة للاختبار
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.PROCESSED_FOLDER, exist_ok=True)
        os.makedirs(cls.CACHE_FOLDER, exist_ok=True)

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج."""
    DEBUG = False
    TESTING = False
    
    # استخدام مفتاح سري من متغيرات البيئة في الإنتاج
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'يجب-تعيين-مفتاح-سري-في-الإنتاج'
    
    # إعدادات أداء محسنة للإنتاج
    VIDEO_ENCODING_PRESET = 'medium'  # توازن أفضل بين الجودة والسرعة
    THREAD_POOL_SIZE = 8  # المزيد من الخيوط للإنتاج
    
    @classmethod
    def init_app(cls, app):
        """تهيئة التطبيق لبيئة الإنتاج."""
        Config.init_app(app)
        # إعدادات إضافية للإنتاج يمكن إضافتها هنا

# قاموس التكوينات المتاحة
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
