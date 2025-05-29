"""
مخطط API لمعلومات الجهاز.
يوفر نقاط نهاية لتسجيل وتحليل معلومات الجهاز.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from ..utils.error_handler import handle_errors

# إنشاء مخطط API للجهاز
device_bp = Blueprint('device', __name__)
logger = logging.getLogger(__name__)

@device_bp.route('/info', methods=['POST'])
@handle_errors
def device_info():
    """
    تسجيل معلومات الجهاز للتحليل.
    
    طلب JSON:
        {
            "deviceType": "نوع الجهاز (mobile/desktop)",
            "os": "نظام التشغيل",
            "browser": "المتصفح",
            "screenWidth": "عرض الشاشة",
            "screenHeight": "ارتفاع الشاشة",
            "userAgent": "وكيل المستخدم"
        }
    
    الاستجابة:
        {
            "success": true,
            "optimizations": {
                "videoFormat": "تنسيق الفيديو الموصى به",
                "videoQuality": "جودة الفيديو الموصى بها",
                "uiMode": "وضع واجهة المستخدم الموصى به"
            }
        }
    """
    try:
        # الحصول على بيانات الجهاز
        data = request.json
        if not data:
            return jsonify({"error": "لم يتم توفير بيانات الجهاز"}), 400
        
        # تسجيل معلومات الجهاز
        logger.info(f"معلومات الجهاز: {data}")
        
        # تحديد التحسينات المناسبة للجهاز
        optimizations = get_device_optimizations(data)
        
        return jsonify({
            "success": True,
            "optimizations": optimizations
        })
    except Exception as e:
        logger.error(f"خطأ في معالجة معلومات الجهاز: {str(e)}")
        return jsonify({"error": str(e)}), 500

@device_bp.route('/compatibility', methods=['GET'])
@handle_errors
def check_compatibility():
    """
    التحقق من توافق الجهاز مع الميزات المختلفة.
    
    المعلمات:
        user_agent (str): وكيل المستخدم.
    
    الاستجابة:
        {
            "videoPlayback": true/false,
            "videoDownload": true/false,
            "webShare": true/false,
            "notifications": true/false
        }
    """
    try:
        # الحصول على وكيل المستخدم
        user_agent = request.args.get('user_agent', '')
        
        # تحليل وكيل المستخدم
        compatibility = analyze_user_agent(user_agent)
        
        return jsonify(compatibility)
    except Exception as e:
        logger.error(f"خطأ في التحقق من التوافق: {str(e)}")
        return jsonify({"error": str(e)}), 500

@device_bp.route('/statistics', methods=['GET'])
@handle_errors
def get_device_statistics():
    """
    الحصول على إحصائيات الأجهزة المستخدمة.
    
    الاستجابة:
        {
            "devices": {
                "mobile": "نسبة الأجهزة المحمولة",
                "desktop": "نسبة أجهزة سطح المكتب"
            },
            "browsers": {
                "chrome": "نسبة متصفح Chrome",
                "safari": "نسبة متصفح Safari",
                "firefox": "نسبة متصفح Firefox",
                "other": "نسبة المتصفحات الأخرى"
            },
            "os": {
                "windows": "نسبة نظام Windows",
                "macos": "نسبة نظام MacOS",
                "ios": "نسبة نظام iOS",
                "android": "نسبة نظام Android",
                "other": "نسبة الأنظمة الأخرى"
            }
        }
    """
    try:
        # في التطبيق الحقيقي، هذه البيانات ستأتي من قاعدة بيانات
        # هنا نستخدم بيانات ثابتة للتوضيح
        statistics = {
            "devices": {
                "mobile": 65,
                "desktop": 35
            },
            "browsers": {
                "chrome": 45,
                "safari": 30,
                "firefox": 15,
                "other": 10
            },
            "os": {
                "windows": 30,
                "macos": 15,
                "ios": 25,
                "android": 25,
                "other": 5
            }
        }
        
        return jsonify(statistics)
    except Exception as e:
        logger.error(f"خطأ في الحصول على إحصائيات الأجهزة: {str(e)}")
        return jsonify({"error": str(e)}), 500

# وظائف مساعدة

def get_device_optimizations(device_data):
    """
    تحديد التحسينات المناسبة للجهاز.
    
    المعلمات:
        device_data (dict): بيانات الجهاز.
    
    العائد:
        dict: التحسينات الموصى بها.
    """
    optimizations = {
        "videoFormat": "mp4",
        "videoQuality": "720p",
        "uiMode": "auto"
    }
    
    # تحديد تنسيق الفيديو المناسب
    if device_data.get('os') == 'iOS' or device_data.get('browser') == 'Safari':
        optimizations["videoFormat"] = "mp4"
    else:
        optimizations["videoFormat"] = "mp4"  # يمكن استخدام webm للمتصفحات الأخرى
    
    # تحديد جودة الفيديو المناسبة
    if device_data.get('deviceType') == 'mobile':
        # التحقق من عرض الشاشة
        screen_width = device_data.get('screenWidth', 0)
        if screen_width and int(screen_width) < 768:
            optimizations["videoQuality"] = "480p"
        else:
            optimizations["videoQuality"] = "720p"
    else:
        optimizations["videoQuality"] = "720p"
    
    # تحديد وضع واجهة المستخدم المناسب
    if device_data.get('os') == 'iOS' or device_data.get('os') == 'Android':
        optimizations["uiMode"] = "mobile"
    else:
        optimizations["uiMode"] = "desktop"
    
    return optimizations

def analyze_user_agent(user_agent):
    """
    تحليل وكيل المستخدم لتحديد التوافق.
    
    المعلمات:
        user_agent (str): وكيل المستخدم.
    
    العائد:
        dict: معلومات التوافق.
    """
    # في التطبيق الحقيقي، سيتم تحليل وكيل المستخدم بشكل أكثر تفصيلاً
    # هنا نستخدم تحليل بسيط للتوضيح
    
    is_mobile = 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent
    is_ios = 'iPhone' in user_agent or 'iPad' in user_agent
    is_safari = 'Safari' in user_agent and not 'Chrome' in user_agent
    
    compatibility = {
        "videoPlayback": True,  # معظم المتصفحات الحديثة تدعم تشغيل الفيديو
        "videoDownload": not (is_ios and is_safari),  # Safari على iOS لا يدعم تنزيل الفيديو مباشرة
        "webShare": is_mobile,  # واجهة Web Share API متوفرة غالبًا على الأجهزة المحمولة
        "notifications": not is_ios  # iOS يقيد الإشعارات
    }
    
    return compatibility
