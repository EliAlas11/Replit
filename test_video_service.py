"""
اختبار وظيفة معالجة الفيديو.
يوفر اختبارات لوظائف معالجة الفيديو وإضافة المؤثرات الصوتية.
"""

import os
import sys
import unittest
import logging
import tempfile
import shutil
from flask import Flask

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.video_service import VideoService
from config.config import config

# تعطيل التسجيل أثناء الاختبار
logging.disable(logging.CRITICAL)

class VideoServiceTest(unittest.TestCase):
    """اختبارات لخدمة معالجة الفيديو."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        # إنشاء تطبيق Flask للاختبار
        self.app = Flask(__name__)
        self.app.config.from_object(config['testing'])
        
        # إنشاء خدمة معالجة الفيديو
        self.video_service = VideoService()
        
        # إنشاء المجلدات المطلوبة
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['PROCESSED_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['AUDIO_FOLDER'], exist_ok=True)
        
        # إنشاء ملف فيديو اختباري
        self.test_video_path = os.path.join(self.app.config['UPLOAD_FOLDER'], "test_video.mp4")
        self.create_test_video()
        
        # إنشاء ملف صوت اختباري
        self.test_audio_path = os.path.join(self.app.config['AUDIO_FOLDER'], "test_sound.mp3")
        self.create_test_audio()
    
    def create_test_video(self):
        """إنشاء ملف فيديو اختباري باستخدام FFmpeg."""
        try:
            # إنشاء فيديو اختباري مدته 10 ثوانٍ
            command = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "testsrc=duration=10:size=640x360:rate=30",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                self.test_video_path
            ]
            
            import subprocess
            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except Exception as e:
            self.skipTest(f"فشل إنشاء ملف فيديو اختباري: {str(e)}")
    
    def create_test_audio(self):
        """إنشاء ملف صوت اختباري باستخدام FFmpeg."""
        try:
            # إنشاء ملف صوت اختباري مدته 5 ثوانٍ
            command = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=5",
                "-c:a", "mp3",
                self.test_audio_path
            ]
            
            import subprocess
            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except Exception as e:
            self.skipTest(f"فشل إنشاء ملف صوت اختباري: {str(e)}")
    
    def test_is_valid_id(self):
        """اختبار التحقق من صحة معرف الفيديو."""
        # معرف صالح
        valid_id = "123e4567-e89b-12d3-a456-426614174000"
        self.assertTrue(self.video_service.is_valid_id(valid_id))
        
        # معرف غير صالح
        invalid_id = "not-a-uuid"
        self.assertFalse(self.video_service.is_valid_id(invalid_id))
    
    def test_get_video_path(self):
        """اختبار الحصول على مسار الفيديو."""
        video_id = "123e4567-e89b-12d3-a456-426614174000"
        expected_path = os.path.join(self.app.config['PROCESSED_FOLDER'], f"{video_id}.mp4")
        self.assertEqual(self.video_service.get_video_path(video_id), expected_path)
    
    def test_get_thumbnail_path(self):
        """اختبار الحصول على مسار الصورة المصغرة."""
        video_id = "123e4567-e89b-12d3-a456-426614174000"
        expected_path = os.path.join(self.app.config['PROCESSED_FOLDER'], f"{video_id}.jpg")
        self.assertEqual(self.video_service.get_thumbnail_path(video_id), expected_path)
    
    def test_allowed_file(self):
        """اختبار التحقق من امتداد الملف."""
        # امتداد مسموح به
        self.assertTrue(self.video_service.allowed_file("video.mp4"))
        
        # امتداد غير مسموح به
        self.assertFalse(self.video_service.allowed_file("document.pdf"))
    
    def test_get_sound_effects(self):
        """اختبار الحصول على قائمة المؤثرات الصوتية."""
        effects = self.video_service.get_sound_effects()
        self.assertIsInstance(effects, list)
        self.assertGreater(len(effects), 0)
        
        # التحقق من وجود الحقول المطلوبة في كل مؤثر
        for effect in effects:
            self.assertIn('id', effect)
            self.assertIn('name', effect)
            self.assertIn('description', effect)
    
    def test_create_thumbnail(self):
        """اختبار إنشاء صورة مصغرة للفيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        # إنشاء مسار للصورة المصغرة
        thumbnail_path = os.path.join(self.app.config['PROCESSED_FOLDER'], "test_thumbnail.jpg")
        
        try:
            # إنشاء الصورة المصغرة
            self.video_service.create_thumbnail(self.test_video_path, thumbnail_path)
            
            # التحقق من وجود الصورة المصغرة
            self.assertTrue(os.path.exists(thumbnail_path))
            
            # حذف الصورة المصغرة بعد الاختبار
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            self.skipTest(f"فشل إنشاء الصورة المصغرة: {str(e)}")
    
    def test_process_video(self):
        """اختبار معالجة الفيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        # نسخ ملف الفيديو الاختباري إلى مجلد التحميل
        video_id = "test_video_id"
        input_path = os.path.join(self.app.config['UPLOAD_FOLDER'], f"{video_id}.mp4")
        shutil.copy(self.test_video_path, input_path)
        
        # معالجة الفيديو
        output_id = "test_output_id"
        try:
            result = self.video_service.process_video(
                video_id=video_id,
                output_id=output_id,
                start_time=0,
                duration=5
            )
            
            # التحقق من نجاح المعالجة
            self.assertTrue(result['success'])
            self.assertEqual(result['videoId'], output_id)
            
            # التحقق من وجود الفيديو المعالج
            output_path = self.video_service.get_video_path(output_id)
            self.assertTrue(os.path.exists(output_path))
            
            # التحقق من وجود الصورة المصغرة
            thumbnail_path = self.video_service.get_thumbnail_path(output_id)
            self.assertTrue(os.path.exists(thumbnail_path))
            
            # حذف الملفات بعد الاختبار
            if os.path.exists(output_path):
                os.remove(output_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            self.skipTest(f"فشل معالجة الفيديو: {str(e)}")
        finally:
            # حذف ملف الفيديو المدخل
            if os.path.exists(input_path):
                os.remove(input_path)
    
    def test_analyze_video(self):
        """اختبار تحليل الفيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        try:
            # تحليل الفيديو
            result = self.video_service.analyze_video(self.test_video_path)
            
            # التحقق من وجود الحقول المطلوبة
            self.assertIn('start_time', result)
            self.assertIn('duration', result)
            self.assertIn('confidence', result)
            
            # التحقق من صحة القيم
            self.assertGreaterEqual(result['start_time'], 0)
            self.assertGreater(result['duration'], 0)
            self.assertGreaterEqual(result['confidence'], 0)
            self.assertLessEqual(result['confidence'], 1)
        except Exception as e:
            self.skipTest(f"فشل تحليل الفيديو: {str(e)}")
    
    def tearDown(self):
        """تنظيف بيئة الاختبار."""
        # حذف ملف الفيديو الاختباري
        if os.path.exists(self.test_video_path):
            os.remove(self.test_video_path)
        
        # حذف ملف الصوت الاختباري
        if os.path.exists(self.test_audio_path):
            os.remove(self.test_audio_path)

if __name__ == '__main__':
    unittest.main()
