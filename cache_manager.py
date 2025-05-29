"""
مدير التخزين المؤقت للتطبيق.
يوفر واجهة بسيطة للتخزين المؤقت للبيانات.
"""

import time
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class CacheManager:
    """
    مدير التخزين المؤقت للتطبيق.
    يستخدم لتخزين نتائج العمليات المكلفة مؤقتًا لتحسين الأداء.
    """
    
    def __init__(self):
        """تهيئة مدير التخزين المؤقت."""
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        """
        الحصول على قيمة من ذاكرة التخزين المؤقت.
        
        المعلمات:
            key (str): مفتاح العنصر.
        
        العائد:
            أي: القيمة المخزنة، أو None إذا لم يتم العثور على المفتاح أو انتهت صلاحيته.
        """
        # التحقق مما إذا كان التخزين المؤقت معطلاً
        if not current_app.config.get('CACHE_ENABLED', True):
            return None
        
        # التحقق من وجود المفتاح
        if key not in self.cache:
            return None
        
        # التحقق من انتهاء الصلاحية
        timestamp = self.timestamps.get(key, 0)
        max_age = current_app.config.get('CACHE_MAX_AGE', 3600)  # الافتراضي: ساعة واحدة
        
        if time.time() - timestamp > max_age:
            # انتهت صلاحية العنصر، إزالته من ذاكرة التخزين المؤقت
            logger.debug(f"انتهت صلاحية العنصر في ذاكرة التخزين المؤقت: {key}")
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        logger.debug(f"تم استرجاع العنصر من ذاكرة التخزين المؤقت: {key}")
        return self.cache[key]
    
    def set(self, key, value):
        """
        تخزين قيمة في ذاكرة التخزين المؤقت.
        
        المعلمات:
            key (str): مفتاح العنصر.
            value (أي): القيمة المراد تخزينها.
        """
        # التحقق مما إذا كان التخزين المؤقت معطلاً
        if not current_app.config.get('CACHE_ENABLED', True):
            return
        
        # التحقق من حجم ذاكرة التخزين المؤقت
        max_size = current_app.config.get('CACHE_MAX_SIZE', 100)
        
        # إذا وصلت ذاكرة التخزين المؤقت إلى الحد الأقصى، إزالة أقدم عنصر
        if len(self.cache) >= max_size and key not in self.cache:
            oldest_key = min(self.timestamps, key=lambda k: self.timestamps[k])
            logger.debug(f"إزالة أقدم عنصر من ذاكرة التخزين المؤقت: {oldest_key}")
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        # تخزين القيمة والطابع الزمني
        self.cache[key] = value
        self.timestamps[key] = time.time()
        logger.debug(f"تم تخزين العنصر في ذاكرة التخزين المؤقت: {key}")
    
    def delete(self, key):
        """
        حذف عنصر من ذاكرة التخزين المؤقت.
        
        المعلمات:
            key (str): مفتاح العنصر.
        
        العائد:
            bool: True إذا تم حذف العنصر، False إذا لم يتم العثور على المفتاح.
        """
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            logger.debug(f"تم حذف العنصر من ذاكرة التخزين المؤقت: {key}")
            return True
        return False
    
    def clear(self):
        """حذف جميع العناصر من ذاكرة التخزين المؤقت."""
        self.cache.clear()
        self.timestamps.clear()
        logger.debug("تم مسح ذاكرة التخزين المؤقت")
    
    def cleanup_expired(self):
        """حذف جميع العناصر منتهية الصلاحية من ذاكرة التخزين المؤقت."""
        current_time = time.time()
        max_age = current_app.config.get('CACHE_MAX_AGE', 3600)
        
        # تحديد المفاتيح منتهية الصلاحية
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if current_time - timestamp > max_age
        ]
        
        # حذف العناصر منتهية الصلاحية
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
        
        if expired_keys:
            logger.debug(f"تم حذف {len(expired_keys)} عنصر منتهي الصلاحية من ذاكرة التخزين المؤقت")
