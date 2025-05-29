"""
خدمة معالجة الفيديو.
توفر وظائف لمعالجة الفيديو وإضافة المؤثرات الصوتية.
"""

import os
import re
import uuid
import logging
import subprocess
from flask import current_app

from ..utils.error_handler import VideoProcessingError

logger = logging.getLogger(__name__)

class VideoService:
    """
    خدمة لمعالجة الفيديو.
    توفر وظائف لاقتطاع المقاطع وإضافة المؤثرات الصوتية.
    """
    
    def __init__(self):
        """تهيئة خدمة معالجة الفيديو."""
        # التحقق من وجود FFmpeg
        self._check_ffmpeg()
        
        # قائمة المؤثرات الصوتية المتاحة
        self.sound_effects = [
            {
                "id": "dramatic",
                "name": "دراماتيكي",
                "description": "مؤثر صوتي دراماتيكي للحظات المثيرة"
            },
            {
                "id": "suspense",
                "name": "تشويق",
                "description": "مؤثر صوتي للحظات المشوقة والمتوترة"
            },
            {
                "id": "upbeat",
                "name": "حماسي",
                "description": "مؤثر صوتي حماسي للحظات المرحة والنشطة"
            }
        ]
    
    def _check_ffmpeg(self):
        """
        التحقق من وجود FFmpeg.
        
        يرفع:
            VideoProcessingError: إذا لم يتم العثور على FFmpeg.
        """
        try:
            # التحقق من وجود FFmpeg
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error("لم يتم العثور على FFmpeg")
                raise VideoProcessingError("لم يتم العثور على FFmpeg، وهو مطلوب لمعالجة الفيديو")
            
            logger.info("تم العثور على FFmpeg")
        except FileNotFoundError:
            logger.error("لم يتم العثور على FFmpeg")
            raise VideoProcessingError("لم يتم العثور على FFmpeg، وهو مطلوب لمعالجة الفيديو")
    
    def is_valid_id(self, video_id):
        """
        التحقق من صحة معرف الفيديو.
        
        المعلمات:
            video_id (str): معرف الفيديو.
        
        العائد:
            bool: True إذا كان المعرف صالحًا، False خلاف ذلك.
        """
        # التحقق من أن المعرف هو UUID صالح
        try:
            uuid.UUID(video_id)
            return True
        except ValueError:
            return False
    
    def get_video_path(self, video_id):
        """
        الحصول على مسار الفيديو.
        
        المعلمات:
            video_id (str): معرف الفيديو.
        
        العائد:
            str: مسار الفيديو.
        """
        return os.path.join(current_app.config['PROCESSED_FOLDER'], f"{video_id}.mp4")
    
    def get_thumbnail_path(self, video_id):
        """
        الحصول على مسار الصورة المصغرة.
        
        المعلمات:
            video_id (str): معرف الفيديو.
        
        العائد:
            str: مسار الصورة المصغرة.
        """
        return os.path.join(current_app.config['PROCESSED_FOLDER'], f"{video_id}.jpg")
    
    def allowed_file(self, filename):
        """
        التحقق مما إذا كان امتداد الملف مسموحًا به.
        
        المعلمات:
            filename (str): اسم الملف.
        
        العائد:
            bool: True إذا كان الامتداد مسموحًا به، False خلاف ذلك.
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    def get_sound_effects(self):
        """
        الحصول على قائمة المؤثرات الصوتية المتاحة.
        
        العائد:
            list: قائمة المؤثرات الصوتية.
        """
        return self.sound_effects
    
    def get_sound_effect_path(self, effect_id):
        """
        الحصول على مسار ملف المؤثر الصوتي.
        
        المعلمات:
            effect_id (str): معرف المؤثر الصوتي.
        
        العائد:
            str: مسار ملف المؤثر الصوتي، أو None إذا لم يتم العثور على المؤثر.
        """
        # التحقق من وجود المؤثر الصوتي
        for effect in self.sound_effects:
            if effect['id'] == effect_id:
                return os.path.join(current_app.config['AUDIO_FOLDER'], f"{effect_id}.mp3")
        
        return None
    
    def create_thumbnail(self, video_path, thumbnail_path):
        """
        إنشاء صورة مصغرة للفيديو.
        
        المعلمات:
            video_path (str): مسار الفيديو.
            thumbnail_path (str): مسار الصورة المصغرة.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء إنشاء الصورة المصغرة.
        """
        try:
            # التحقق من وجود الفيديو
            if not os.path.exists(video_path):
                raise VideoProcessingError(f"الفيديو غير موجود: {video_path}")
            
            # إنشاء الصورة المصغرة باستخدام FFmpeg
            command = [
                "ffmpeg",
                "-i", video_path,
                "-ss", "00:00:01",  # لقطة من الثانية الأولى
                "-vframes", "1",
                "-q:v", "2",
                thumbnail_path
            ]
            
            logger.info(f"إنشاء صورة مصغرة للفيديو: {video_path}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في إنشاء الصورة المصغرة: {result.stderr}")
                raise VideoProcessingError(f"خطأ في إنشاء الصورة المصغرة: {result.stderr}")
            
            logger.info(f"تم إنشاء الصورة المصغرة بنجاح: {thumbnail_path}")
        except Exception as e:
            logger.error(f"خطأ في إنشاء الصورة المصغرة: {str(e)}")
            raise VideoProcessingError(f"خطأ في إنشاء الصورة المصغرة: {str(e)}")
    
    def process_video(self, video_id, output_id, start_time=None, duration=None, sound_effect=None):
        """
        معالجة الفيديو وإضافة المؤثرات الصوتية.
        
        المعلمات:
            video_id (str): معرف الفيديو المصدر.
            output_id (str): معرف الفيديو الناتج.
            start_time (float, اختياري): وقت البداية بالثواني.
            duration (float, اختياري): المدة بالثواني.
            sound_effect (str, اختياري): معرف المؤثر الصوتي.
        
        العائد:
            dict: معلومات الفيديو المعالج.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء معالجة الفيديو.
        """
        try:
            # تحديد مسارات الملفات
            input_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{video_id}.mp4")
            if not os.path.exists(input_path):
                input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{video_id}.mp4")
            
            output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], f"{output_id}.mp4")
            
            # التحقق من وجود الفيديو المصدر
            if not os.path.exists(input_path):
                raise VideoProcessingError(f"الفيديو المصدر غير موجود: {input_path}")
            
            # تحديد وقت البداية والمدة
            if start_time is None:
                # إذا لم يتم تحديد وقت البداية، استخدام الثانية 0
                start_time = 0
            
            if duration is None:
                # إذا لم يتم تحديد المدة، استخدام المدة الافتراضية
                duration = current_app.config['VIDEO_DEFAULT_CLIP_DURATION']
            
            # التحقق من صحة وقت البداية والمدة
            if not isinstance(start_time, (int, float)) or start_time < 0:
                raise VideoProcessingError(f"وقت البداية غير صالح: {start_time}")
            
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise VideoProcessingError(f"المدة غير صالحة: {duration}")
            
            # تحديد مسار المؤثر الصوتي
            sound_effect_path = None
            if sound_effect:
                sound_effect_path = self.get_sound_effect_path(sound_effect)
                if not sound_effect_path or not os.path.exists(sound_effect_path):
                    logger.warning(f"المؤثر الصوتي غير موجود: {sound_effect}")
                    sound_effect_path = None
            
            # إعداد أمر FFmpeg
            command = [
                "ffmpeg",
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(duration)
            ]
            
            # إضافة المؤثر الصوتي إذا كان متاحًا
            if sound_effect_path:
                command.extend([
                    "-i", sound_effect_path,
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[a]",
                    "-map", "0:v",
                    "-map", "[a]"
                ])
            
            # إضافة معلمات الترميز
            command.extend([
                "-c:v", "libx264",
                "-preset", current_app.config['VIDEO_ENCODING_PRESET'],
                "-crf", str(current_app.config['VIDEO_CRF']),
                "-c:a", "aac",
                "-b:a", current_app.config['VIDEO_AUDIO_BITRATE'],
                "-movflags", "+faststart",  # لتحسين التشغيل عبر الإنترنت
                output_path
            ])
            
            # تنفيذ أمر FFmpeg
            logger.info(f"معالجة الفيديو: {input_path} -> {output_path}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في معالجة الفيديو: {result.stderr}")
                raise VideoProcessingError(f"خطأ في معالجة الفيديو: {result.stderr}")
            
            # إنشاء صورة مصغرة للفيديو المعالج
            thumbnail_path = self.get_thumbnail_path(output_id)
            self.create_thumbnail(output_path, thumbnail_path)
            
            # الحصول على مدة الفيديو الناتج
            actual_duration = self._get_video_duration(output_path)
            
            logger.info(f"تمت معالجة الفيديو بنجاح: {output_path}")
            
            # إرجاع معلومات الفيديو المعالج
            return {
                "success": True,
                "videoId": output_id,
                "duration": actual_duration,
                "url": f"/api/video/{output_id}"
            }
        except Exception as e:
            logger.error(f"خطأ في معالجة الفيديو: {str(e)}")
            raise VideoProcessingError(f"خطأ في معالجة الفيديو: {str(e)}")
    
    def _get_video_duration(self, video_path):
        """
        الحصول على مدة الفيديو.
        
        المعلمات:
            video_path (str): مسار الفيديو.
        
        العائد:
            float: مدة الفيديو بالثواني.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء الحصول على مدة الفيديو.
        """
        try:
            # استخدام FFprobe للحصول على مدة الفيديو
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في الحصول على مدة الفيديو: {result.stderr}")
                raise VideoProcessingError(f"خطأ في الحصول على مدة الفيديو: {result.stderr}")
            
            # تحويل الناتج إلى رقم عشري
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            logger.error(f"خطأ في الحصول على مدة الفيديو: {str(e)}")
            raise VideoProcessingError(f"خطأ في الحصول على مدة الفيديو: {str(e)}")
    
    def analyze_video(self, video_path):
        """
        تحليل الفيديو لتحديد اللحظات المثيرة.
        
        المعلمات:
            video_path (str): مسار الفيديو.
        
        العائد:
            dict: نتائج التحليل.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء تحليل الفيديو.
        """
        try:
            # في التطبيق الحقيقي، يمكن استخدام خوارزميات معالجة الصور والفيديو
            # لتحديد اللحظات المثيرة في الفيديو
            # هنا نستخدم تحليل بسيط للتوضيح
            
            # الحصول على مدة الفيديو
            duration = self._get_video_duration(video_path)
            
            # تحديد وقت البداية (ثلث المدة)
            start_time = duration / 3
            
            # تحديد مدة المقطع (15 ثانية أو ثلث المدة، أيهما أقل)
            clip_duration = min(15, duration / 3)
            
            # إرجاع نتائج التحليل
            return {
                "start_time": start_time,
                "duration": clip_duration,
                "confidence": 0.8  # مستوى الثقة في التحليل
            }
        except Exception as e:
            logger.error(f"خطأ في تحليل الفيديو: {str(e)}")
            raise VideoProcessingError(f"خطأ في تحليل الفيديو: {str(e)}")
