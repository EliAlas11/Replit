"""
مخطط API لتنزيل فيديوهات YouTube.
يوفر نقاط نهاية للبحث وتنزيل فيديوهات YouTube.
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..services.youtube_service import YouTubeService
from ..utils.cache_manager import CacheManager
from ..utils.error_handler import handle_errors, YouTubeError

# إنشاء مخطط API لـ YouTube
youtube_bp = Blueprint('youtube', __name__)
logger = logging.getLogger(__name__)

# إنشاء مدير التخزين المؤقت
cache = CacheManager()

# إنشاء خدمة YouTube
youtube_service = YouTubeService()

@youtube_bp.route('/info', methods=['GET'])
@handle_errors
def get_video_info():
    """
    الحصول على معلومات فيديو YouTube.
    
    المعلمات:
        video_id (str): معرف فيديو YouTube أو رابط.
    
    الاستجابة:
        {
            "videoId": "معرف الفيديو",
            "title": "عنوان الفيديو",
            "author": "مؤلف الفيديو",
            "length": "مدة الفيديو بالثواني",
            "thumbnail_url": "رابط الصورة المصغرة",
            "available_resolutions": ["720p", "480p", "360p", ...]
        }
    """
    # الحصول على معرف الفيديو من المعلمات
    video_id_or_url = request.args.get('video_id')
    if not video_id_or_url:
        return jsonify({"error": "معرف الفيديو أو الرابط مطلوب"}), 400
    
    # التحقق من وجود النتيجة في ذاكرة التخزين المؤقت
    cache_key = f"youtube_info_{video_id_or_url}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"تم استرجاع معلومات فيديو YouTube من ذاكرة التخزين المؤقت: {video_id_or_url}")
        return jsonify(cached_result)
    
    try:
        # استخراج معرف الفيديو إذا كان رابطًا
        video_id = youtube_service.extract_video_id(video_id_or_url)
        if not video_id:
            return jsonify({"error": "معرف فيديو YouTube غير صالح"}), 400
        
        # الحصول على معلومات الفيديو
        logger.info(f"جاري الحصول على معلومات فيديو YouTube: {video_id}")
        video_info = youtube_service.get_video_info(video_id)
        
        # تخزين النتيجة في ذاكرة التخزين المؤقت
        cache.set(cache_key, video_info)
        
        return jsonify(video_info)
    except YouTubeError as e:
        logger.error(f"خطأ في الحصول على معلومات فيديو YouTube: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء معالجة الطلب"}), 500

@youtube_bp.route('/download', methods=['POST'])
@handle_errors
def download_video():
    """
    تنزيل فيديو YouTube.
    
    طلب JSON:
        {
            "videoId": "معرف فيديو YouTube أو رابط",
            "resolution": "الدقة المطلوبة (اختياري، الافتراضي: 720p)"
        }
    
    الاستجابة:
        {
            "success": true,
            "videoId": "معرف الفيديو المحلي",
            "originalId": "معرف فيديو YouTube الأصلي",
            "title": "عنوان الفيديو",
            "path": "المسار المحلي للفيديو (للاستخدام الداخلي فقط)"
        }
    """
    # التحقق من البيانات المستلمة
    data = request.json
    if not data or 'videoId' not in data:
        return jsonify({"error": "معرف الفيديو أو الرابط مطلوب"}), 400
    
    video_id_or_url = data.get('videoId')
    resolution = data.get('resolution', current_app.config['YOUTUBE_DEFAULT_RESOLUTION'])
    
    try:
        # استخراج معرف الفيديو إذا كان رابطًا
        video_id = youtube_service.extract_video_id(video_id_or_url)
        if not video_id:
            return jsonify({"error": "معرف فيديو YouTube غير صالح"}), 400
        
        # التحقق من وجود النتيجة في ذاكرة التخزين المؤقت
        cache_key = f"youtube_download_{video_id}_{resolution}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"تم استرجاع نتيجة تنزيل فيديو YouTube من ذاكرة التخزين المؤقت: {video_id}")
            return jsonify(cached_result)
        
        # تنزيل الفيديو في خيط منفصل
        logger.info(f"بدء تنزيل فيديو YouTube: {video_id} بدقة {resolution}")
        
        result = current_app.executor.submit(
            youtube_service.download_video,
            video_id=video_id,
            resolution=resolution
        ).result()
        
        # تخزين النتيجة في ذاكرة التخزين المؤقت
        cache.set(cache_key, result)
        
        logger.info(f"تم تنزيل فيديو YouTube بنجاح: {video_id}")
        return jsonify(result)
    except YouTubeError as e:
        logger.error(f"خطأ في تنزيل فيديو YouTube: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء معالجة الطلب"}), 500

@youtube_bp.route('/search', methods=['GET'])
@handle_errors
def search_videos():
    """
    البحث عن فيديوهات YouTube.
    
    المعلمات:
        query (str): استعلام البحث.
        max_results (int, اختياري): الحد الأقصى لعدد النتائج (الافتراضي: 10).
    
    الاستجابة:
        {
            "results": [
                {
                    "videoId": "معرف الفيديو",
                    "title": "عنوان الفيديو",
                    "author": "مؤلف الفيديو",
                    "length": "مدة الفيديو بالثواني",
                    "thumbnail_url": "رابط الصورة المصغرة"
                },
                ...
            ]
        }
    """
    # الحصول على معلمات البحث
    query = request.args.get('query')
    max_results = request.args.get('max_results', 10, type=int)
    
    if not query:
        return jsonify({"error": "استعلام البحث مطلوب"}), 400
    
    # التحقق من وجود النتيجة في ذاكرة التخزين المؤقت
    cache_key = f"youtube_search_{query}_{max_results}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"تم استرجاع نتائج بحث YouTube من ذاكرة التخزين المؤقت: {query}")
        return jsonify(cached_result)
    
    try:
        # البحث عن الفيديوهات
        logger.info(f"جاري البحث في YouTube عن: {query}")
        results = youtube_service.search_videos(query, max_results)
        
        # تخزين النتيجة في ذاكرة التخزين المؤقت
        cache.set(cache_key, {"results": results})
        
        return jsonify({"results": results})
    except YouTubeError as e:
        logger.error(f"خطأ في البحث في YouTube: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء معالجة الطلب"}), 500

@youtube_bp.route('/trending', methods=['GET'])
@handle_errors
def get_trending_videos():
    """
    الحصول على الفيديوهات الرائجة على YouTube.
    
    المعلمات:
        max_results (int, اختياري): الحد الأقصى لعدد النتائج (الافتراضي: 10).
        category (str, اختياري): فئة الفيديوهات (الافتراضي: جميع الفئات).
    
    الاستجابة:
        {
            "results": [
                {
                    "videoId": "معرف الفيديو",
                    "title": "عنوان الفيديو",
                    "author": "مؤلف الفيديو",
                    "length": "مدة الفيديو بالثواني",
                    "thumbnail_url": "رابط الصورة المصغرة"
                },
                ...
            ]
        }
    """
    # الحصول على المعلمات
    max_results = request.args.get('max_results', 10, type=int)
    category = request.args.get('category', '')
    
    # التحقق من وجود النتيجة في ذاكرة التخزين المؤقت
    cache_key = f"youtube_trending_{max_results}_{category}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"تم استرجاع الفيديوهات الرائجة من ذاكرة التخزين المؤقت")
        return jsonify(cached_result)
    
    try:
        # الحصول على الفيديوهات الرائجة
        logger.info(f"جاري الحصول على الفيديوهات الرائجة على YouTube")
        results = youtube_service.get_trending_videos(max_results, category)
        
        # تخزين النتيجة في ذاكرة التخزين المؤقت
        cache.set(cache_key, {"results": results})
        
        return jsonify({"results": results})
    except YouTubeError as e:
        logger.error(f"خطأ في الحصول على الفيديوهات الرائجة: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء معالجة الطلب"}), 500
