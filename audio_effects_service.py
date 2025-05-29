"""
ملف تنفيذ المؤثرات الصوتية.
يوفر وظائف لإنشاء وإضافة المؤثرات الصوتية للفيديو.
"""

import os
import logging
import subprocess
from flask import current_app

from ..utils.error_handler import VideoProcessingError

logger = logging.getLogger(__name__)

class AudioEffectsService:
    """
    خدمة المؤثرات الصوتية.
    توفر وظائف لإنشاء وإضافة المؤثرات الصوتية للفيديو.
    """
    
    def __init__(self):
        """تهيئة خدمة المؤثرات الصوتية."""
        # التحقق من وجود FFmpeg
        self._check_ffmpeg()
        
        # قائمة المؤثرات الصوتية المتاحة
        self.sound_effects = {
            "dramatic": {
                "name": "دراماتيكي",
                "description": "مؤثر صوتي دراماتيكي للحظات المثيرة",
                "volume": 0.7,  # مستوى الصوت (0.0 - 1.0)
                "fade_in": 1.0,  # مدة التلاشي الداخلي بالثواني
                "fade_out": 2.0  # مدة التلاشي الخارجي بالثواني
            },
            "suspense": {
                "name": "تشويق",
                "description": "مؤثر صوتي للحظات المشوقة والمتوترة",
                "volume": 0.8,
                "fade_in": 0.5,
                "fade_out": 1.5
            },
            "upbeat": {
                "name": "حماسي",
                "description": "مؤثر صوتي حماسي للحظات المرحة والنشطة",
                "volume": 0.9,
                "fade_in": 0.3,
                "fade_out": 1.0
            }
        }
    
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
                raise VideoProcessingError("لم يتم العثور على FFmpeg، وهو مطلوب لمعالجة الصوت")
            
            logger.info("تم العثور على FFmpeg")
        except FileNotFoundError:
            logger.error("لم يتم العثور على FFmpeg")
            raise VideoProcessingError("لم يتم العثور على FFmpeg، وهو مطلوب لمعالجة الصوت")
    
    def get_sound_effects_list(self):
        """
        الحصول على قائمة المؤثرات الصوتية المتاحة.
        
        العائد:
            list: قائمة المؤثرات الصوتية.
        """
        effects_list = []
        for effect_id, effect_data in self.sound_effects.items():
            effects_list.append({
                "id": effect_id,
                "name": effect_data["name"],
                "description": effect_data["description"]
            })
        return effects_list
    
    def get_sound_effect_path(self, effect_id):
        """
        الحصول على مسار ملف المؤثر الصوتي.
        
        المعلمات:
            effect_id (str): معرف المؤثر الصوتي.
        
        العائد:
            str: مسار ملف المؤثر الصوتي، أو None إذا لم يتم العثور على المؤثر.
        """
        # التحقق من وجود المؤثر الصوتي
        if effect_id in self.sound_effects:
            return os.path.join(current_app.config['AUDIO_FOLDER'], f"{effect_id}.mp3")
        
        return None
    
    def create_sound_effect(self, effect_id, duration):
        """
        إنشاء ملف مؤثر صوتي بمدة محددة.
        
        المعلمات:
            effect_id (str): معرف المؤثر الصوتي.
            duration (float): مدة المؤثر الصوتي بالثواني.
        
        العائد:
            str: مسار ملف المؤثر الصوتي المنشأ.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء إنشاء المؤثر الصوتي.
        """
        try:
            # التحقق من وجود المؤثر الصوتي
            if effect_id not in self.sound_effects:
                raise VideoProcessingError(f"المؤثر الصوتي غير موجود: {effect_id}")
            
            # الحصول على مسار ملف المؤثر الصوتي الأصلي
            original_path = self.get_sound_effect_path(effect_id)
            
            # التحقق من وجود ملف المؤثر الصوتي الأصلي
            if not os.path.exists(original_path):
                # إنشاء ملف المؤثر الصوتي الأصلي
                self._generate_sound_effect(effect_id, original_path)
            
            # إنشاء مسار ملف المؤثر الصوتي المؤقت
            temp_path = os.path.join(current_app.config['CACHE_FOLDER'], f"{effect_id}_{duration}.mp3")
            
            # الحصول على معلومات المؤثر الصوتي
            effect_data = self.sound_effects[effect_id]
            
            # إنشاء ملف المؤثر الصوتي بالمدة المحددة
            command = [
                "ffmpeg",
                "-i", original_path,
                "-t", str(duration),
                "-af", f"afade=t=in:st=0:d={effect_data['fade_in']},afade=t=out:st={duration - effect_data['fade_out']}:d={effect_data['fade_out']},volume={effect_data['volume']}",
                "-y",  # الكتابة فوق الملف إذا كان موجودًا
                temp_path
            ]
            
            logger.info(f"إنشاء ملف مؤثر صوتي: {effect_id} بمدة {duration} ثانية")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في إنشاء ملف المؤثر الصوتي: {result.stderr}")
                raise VideoProcessingError(f"خطأ في إنشاء ملف المؤثر الصوتي: {result.stderr}")
            
            logger.info(f"تم إنشاء ملف المؤثر الصوتي بنجاح: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف المؤثر الصوتي: {str(e)}")
            raise VideoProcessingError(f"خطأ في إنشاء ملف المؤثر الصوتي: {str(e)}")
    
    def _generate_sound_effect(self, effect_id, output_path):
        """
        إنشاء ملف المؤثر الصوتي الأصلي.
        
        المعلمات:
            effect_id (str): معرف المؤثر الصوتي.
            output_path (str): مسار ملف المؤثر الصوتي.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء إنشاء المؤثر الصوتي.
        """
        try:
            # إنشاء ملف المؤثر الصوتي حسب النوع
            if effect_id == "dramatic":
                # مؤثر صوتي دراماتيكي
                command = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", "sine=frequency=200:duration=10",
                    "-af", "aecho=0.8:0.9:1000:0.3,areverse,aecho=0.8:0.9:1000:0.3,areverse",
                    "-y",
                    output_path
                ]
            elif effect_id == "suspense":
                # مؤثر صوتي للتشويق
                command = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=10",
                    "-af", "tremolo=f=5:d=0.7",
                    "-y",
                    output_path
                ]
            elif effect_id == "upbeat":
                # مؤثر صوتي حماسي
                command = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", "sine=frequency=880:duration=10",
                    "-af", "chorus=0.5:0.9:50:0.4:0.25:2",
                    "-y",
                    output_path
                ]
            else:
                # مؤثر صوتي افتراضي
                command = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=10",
                    "-y",
                    output_path
                ]
            
            logger.info(f"إنشاء ملف المؤثر الصوتي الأصلي: {effect_id}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في إنشاء ملف المؤثر الصوتي الأصلي: {result.stderr}")
                raise VideoProcessingError(f"خطأ في إنشاء ملف المؤثر الصوتي الأصلي: {result.stderr}")
            
            logger.info(f"تم إنشاء ملف المؤثر الصوتي الأصلي بنجاح: {output_path}")
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف المؤثر الصوتي الأصلي: {str(e)}")
            raise VideoProcessingError(f"خطأ في إنشاء ملف المؤثر الصوتي الأصلي: {str(e)}")
    
    def add_sound_effect_to_video(self, video_path, output_path, effect_id):
        """
        إضافة مؤثر صوتي إلى فيديو.
        
        المعلمات:
            video_path (str): مسار ملف الفيديو.
            output_path (str): مسار ملف الفيديو الناتج.
            effect_id (str): معرف المؤثر الصوتي.
        
        يرفع:
            VideoProcessingError: إذا حدث خطأ أثناء إضافة المؤثر الصوتي.
        """
        try:
            # التحقق من وجود ملف الفيديو
            if not os.path.exists(video_path):
                raise VideoProcessingError(f"ملف الفيديو غير موجود: {video_path}")
            
            # التحقق من وجود المؤثر الصوتي
            if effect_id not in self.sound_effects:
                raise VideoProcessingError(f"المؤثر الصوتي غير موجود: {effect_id}")
            
            # الحصول على مدة الفيديو
            duration = self._get_video_duration(video_path)
            
            # إنشاء ملف المؤثر الصوتي بنفس مدة الفيديو
            sound_effect_path = self.create_sound_effect(effect_id, duration)
            
            # إضافة المؤثر الصوتي إلى الفيديو
            command = [
                "ffmpeg",
                "-i", video_path,
                "-i", sound_effect_path,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", current_app.config['VIDEO_AUDIO_BITRATE'],
                "-shortest",
                "-y",
                output_path
            ]
            
            logger.info(f"إضافة مؤثر صوتي إلى فيديو: {effect_id} -> {output_path}")
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"خطأ في إضافة المؤثر الصوتي إلى الفيديو: {result.stderr}")
                raise VideoProcessingError(f"خطأ في إضافة المؤثر الصوتي إلى الفيديو: {result.stderr}")
            
            logger.info(f"تمت إضافة المؤثر الصوتي إلى الفيديو بنجاح: {output_path}")
            
            # حذف ملف المؤثر الصوتي المؤقت
            if os.path.exists(sound_effect_path):
                os.remove(sound_effect_path)
        except Exception as e:
            logger.error(f"خطأ في إضافة المؤثر الصوتي إلى الفيديو: {str(e)}")
            raise VideoProcessingError(f"خطأ في إضافة المؤثر الصوتي إلى الفيديو: {str(e)}")
    
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
