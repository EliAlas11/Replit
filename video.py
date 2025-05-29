"""
مخطط API لمعالجة الفيديو.
يوفر نقاط نهاية لمعالجة الفيديو وإضافة المؤثرات الصوتية.
"""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from ..services.video_service import VideoService
from ..utils.cache_manager import CacheManager
from ..utils.error_handler import handle_errors, VideoProcessingError

# إنشاء مخطط API للفيديو
video_bp = Blueprint('video', __name__)
logger = logging.getLogger(__name__)

# إنشاء مدير التخزين المؤقت
cache = CacheManager()

# إنشاء خدمة معالجة الفيديو
video_service = VideoService()

@video_bp.route('/process', methods=['POST'])
@handle_errors
def process_video():
    """
    معالجة الفيديو وإضافة المؤثرات الصوتية.
    
    طلب JSON:
        {
            "videoId": "معرف الفيديو (من YouTube أو ملف محمل)",
            "startTime": "وقت البداية (اختياري، بالثواني)",
            "duration": "المدة (اختياري، بالثواني)",
            "soundEffect": "نوع المؤثر الصوتي (اختياري)"
        }
    
    الاستجابة:
        {
            "success": true,
            "videoId": "معرف الفيديو المعالج",
            "duration": "مدة الفيديو المعالج",
            "url": "عنوان URL للفيديو المعالج"
        }
    """
    # التحقق من البيانات المستلمة
    data = request.json
    if not data or 'videoId' not in data:
        return jsonify({"error": "معرف الفيديو مطلوب"}), 400
    
    video_id = data.get('videoId')
    start_time = data.get('startTime')
    duration = data.get('duration')
    sound_effect = data.get('soundEffect')
    
    # التحقق من وجود النتيجة في ذاكرة التخزين المؤقت
    cache_key = f"processed_{video_id}_{start_time}_{duration}_{sound_effect}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"تم استرجاع نتيجة معالجة الفيديو من ذاكرة التخزين المؤقت: {video_id}")
        return jsonify(cached_result)
    
    # تنفيذ معالجة الفيديو في خيط منفصل
    logger.info(f"بدء معالجة الفيديو: {video_id}")
    
    # إنشاء معرف فريد للفيديو المعالج
    output_id = str(uuid.uuid4())
    
    # معالجة الفيديو
    result = current_app.executor.submit(
        video_service.process_video,
        video_id=video_id,
        output_id=output_id,
        start_time=start_time,
        duration=duration,
        sound_effect=sound_effect
    ).result()
    
    # تخزين النتيجة في ذاكرة التخزين المؤقت
    cache.set(cache_key, result)
    
    logger.info(f"تمت معالجة الفيديو بنجاح: {video_id} -> {output_id}")
    return jsonify(result)

@video_bp.route('/<video_id>', methods=['GET'])
@handle_errors
def get_video(video_id):
    """
    الحصول على الفيديو المعالج.
    
    المعلمات:
        video_id (str): معرف الفيديو المعالج.
    
    الاستجابة:
        ملف الفيديو (video/mp4).
    """
    try:
        # التحقق من صحة معرف الفيديو
        if not video_id or not video_service.is_valid_id(video_id):
            return jsonify({"error": "معرف فيديو غير صالح"}), 400
        
        # الحصول على مسار الفيديو
        video_path = video_service.get_video_path(video_id)
        
        # التحقق من وجود الفيديو
        if not os.path.exists(video_path):
            return jsonify({"error": "الفيديو غير موجود"}), 404
        
        logger.info(f"إرسال الفيديو: {video_id}")
        return send_file(video_path, mimetype='video/mp4')
    except Exception as e:
        logger.error(f"خطأ في الحصول على الفيديو: {str(e)}")
        return jsonify({"error": str(e)}), 500

@video_bp.route('/thumbnail/<video_id>', methods=['GET'])
@handle_errors
def get_thumbnail(video_id):
    """
    الحصول على صورة مصغرة للفيديو المعالج.
    
    المعلمات:
        video_id (str): معرف الفيديو المعالج.
    
    الاستجابة:
        ملف الصورة (image/jpeg).
    """
    try:
        # التحقق من صحة معرف الفيديو
        if not video_id or not video_service.is_valid_id(video_id):
            return jsonify({"error": "معرف فيديو غير صالح"}), 400
        
        # الحصول على مسار الصورة المصغرة
        thumbnail_path = video_service.get_thumbnail_path(video_id)
        
        # إنشاء صورة مصغرة إذا لم تكن موجودة
        if not os.path.exists(thumbnail_path):
            video_path = video_service.get_video_path(video_id)
            if not os.path.exists(video_path):
                return jsonify({"error": "الفيديو غير موجود"}), 404
            
            # إنشاء الصورة المصغرة
            video_service.create_thumbnail(video_path, thumbnail_path)
        
        logger.info(f"إرسال الصورة المصغرة: {video_id}")
        return send_file(thumbnail_path, mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"خطأ في الحصول على الصورة المصغرة: {str(e)}")
        return jsonify({"error": str(e)}), 500

@video_bp.route('/upload', methods=['POST'])
@handle_errors
def upload_video():
    """
    تحميل ملف فيديو.
    
    الطلب:
        ملف فيديو (multipart/form-data).
    
    الاستجابة:
        {
            "success": true,
            "videoId": "معرف الفيديو المحمل"
        }
    """
    # التحقق من وجود الملف في الطلب
    if 'file' not in request.files:
        return jsonify({"error": "لم يتم تحديد ملف"}), 400
    
    file = request.files['file']
    
    # التحقق من اسم الملف
    if file.filename == '':
        return jsonify({"error": "لم يتم تحديد اسم الملف"}), 400
    
    # التحقق من امتداد الملف
    if not video_service.allowed_file(file.filename):
        allowed_extensions = ', '.join(current_app.config['ALLOWED_EXTENSIONS'])
        return jsonify({
            "error": f"امتداد الملف غير مسموح به. الامتدادات المسموح بها: {allowed_extensions}"
        }), 400
    
    try:
        # حفظ الملف بمعرف فريد
        video_id = str(uuid.uuid4())
        filename = secure_filename(f"{video_id}.mp4")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        logger.info(f"تم تحميل الفيديو بنجاح: {video_id}")
        return jsonify({
            "success": True,
            "videoId": video_id
        })
    except Exception as e:
        logger.error(f"خطأ في تحميل الفيديو: {str(e)}")
        return jsonify({"error": str(e)}), 500

@video_bp.route('/effects', methods=['GET'])
@handle_errors
def get_sound_effects():
    """
    الحصول على قائمة المؤثرات الصوتية المتاحة.
    
    الاستجابة:
        {
            "effects": [
                {
                    "id": "معرف المؤثر",
                    "name": "اسم المؤثر",
                    "description": "وصف المؤثر"
                },
                ...
            ]
        }
    """
    try:
        # الحصول على قائمة المؤثرات الصوتية
        effects = video_service.get_sound_effects()
        
        logger.info(f"تم استرجاع {len(effects)} مؤثر صوتي")
        return jsonify({"effects": effects})
    except Exception as e:
        logger.error(f"خطأ في الحصول على المؤثرات الصوتية: {str(e)}")
        return jsonify({"error": str(e)}), 500
