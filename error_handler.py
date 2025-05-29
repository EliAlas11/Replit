"""
معالج الأخطاء للتطبيق.
يوفر وظائف ومزخرفات لمعالجة الأخطاء بشكل موحد.
"""

import logging
import functools
import traceback
from flask import jsonify, current_app

logger = logging.getLogger(__name__)

class APIError(Exception):
    """فئة الخطأ الأساسية للـ API."""
    
    def __init__(self, message, status_code=400):
        """
        تهيئة خطأ API.
        
        المعلمات:
            message (str): رسالة الخطأ.
            status_code (int): رمز حالة HTTP.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class VideoProcessingError(APIError):
    """خطأ في معالجة الفيديو."""
    pass

class YouTubeError(APIError):
    """خطأ في التعامل مع YouTube."""
    pass

class DeviceError(APIError):
    """خطأ في التعامل مع معلومات الجهاز."""
    pass

def handle_errors(func):
    """
    مزخرف لمعالجة الأخطاء في نقاط نهاية API.
    
    المعلمات:
        func (callable): الدالة المراد تزيينها.
    
    العائد:
        callable: الدالة المزينة.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            # معالجة أخطاء API المعروفة
            logger.warning(f"خطأ API: {str(e)}")
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            # معالجة الأخطاء غير المتوقعة
            error_id = log_exception(e)
            logger.error(f"خطأ غير متوقع: {str(e)}")
            
            # في وضع التطوير، إرجاع تفاصيل الخطأ
            if current_app.debug:
                return jsonify({
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "error_id": error_id
                }), 500
            
            # في وضع الإنتاج، إرجاع رسالة خطأ عامة
            return jsonify({
                "error": "حدث خطأ أثناء معالجة الطلب",
                "error_id": error_id
            }), 500
    
    return wrapper

def log_exception(exception):
    """
    تسجيل استثناء في السجل.
    
    المعلمات:
        exception (Exception): الاستثناء المراد تسجيله.
    
    العائد:
        str: معرف الخطأ.
    """
    import uuid
    import datetime
    
    # إنشاء معرف فريد للخطأ
    error_id = str(uuid.uuid4())
    
    # تسجيل الخطأ مع المعرف
    logger.error(f"خطأ {error_id}: {str(exception)}")
    logger.error(f"تتبع المكدس: {traceback.format_exc()}")
    
    # في التطبيق الحقيقي، يمكن تخزين تفاصيل الخطأ في قاعدة بيانات
    # أو إرسالها إلى خدمة تتبع الأخطاء
    
    return error_id
