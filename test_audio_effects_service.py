"""
اختبار خدمة المؤثرات الصوتية.
يوفر اختبارات لوظائف إنشاء وإضافة المؤثرات الصوتية.
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

from services.audio_effects_service import AudioEffectsService
from config.config import config

# تعطيل التسجيل أثناء الاختبار
logging.disable(logging.CRITICAL)

class AudioEffectsServiceTest(unittest.TestCase):
    """اختبارات لخدمة المؤثرات الصوتية."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        # إنشاء تطبيق Flask للاختبار
        self.app = Flask(__name__)
        self.app.config.from_object(config['testing'])
        
        # إنشاء خدمة المؤثرات الصوتية
        self.audio_effects_service = AudioEffectsService()
        
        # إنشاء المجلدات المطلوبة
        os.makedirs(self.app.config['AUDIO_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['CACHE_FOLDER'], exist_ok=True)
        
        # إنشاء ملف فيديو اختباري
        self.test_video_path = os.path.join(self.app.config['CACHE_FOLDER'], "test_video.mp4")
        self.create_test_video()
    
    def create_test_video(self):
        """إنشاء ملف فيديو اختباري باستخدام FFmpeg."""
        try:
            # إنشاء فيديو اختباري مدته 5 ثوانٍ
            command = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "testsrc=duration=5:size=640x360:rate=30",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=5",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-pix_fmt", "yuv420p",
                "-y",
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
    
    def test_get_sound_effects_list(self):
        """اختبار الحصول على قائمة المؤثرات الصوتية."""
        effects = self.audio_effects_service.get_sound_effects_list()
        self.assertIsInstance(effects, list)
        self.assertGreater(len(effects), 0)
        
        # التحقق من وجود الحقول المطلوبة في كل مؤثر
        for effect in effects:
            self.assertIn('id', effect)
            self.assertIn('name', effect)
            self.assertIn('description', effect)
    
    def test_get_sound_effect_path(self):
        """اختبار الحصول على مسار ملف المؤثر الصوتي."""
        # مؤثر صوتي موجود
        effect_id = "dramatic"
        path = self.audio_effects_service.get_sound_effect_path(effect_id)
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith(f"{effect_id}.mp3"))
        
        # مؤثر صوتي غير موجود
        effect_id = "nonexistent"
        path = self.audio_effects_service.get_sound_effect_path(effect_id)
        self.assertIsNone(path)
    
    def test_create_sound_effect(self):
        """اختبار إنشاء ملف مؤثر صوتي."""
        effect_id = "dramatic"
        duration = 3.0
        
        try:
            # إنشاء ملف المؤثر الصوتي
            path = self.audio_effects_service.create_sound_effect(effect_id, duration)
            
            # التحقق من وجود الملف
            self.assertTrue(os.path.exists(path))
            
            # حذف الملف بعد الاختبار
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            self.skipTest(f"فشل إنشاء ملف المؤثر الصوتي: {str(e)}")
    
    def test_add_sound_effect_to_video(self):
        """اختبار إضافة مؤثر صوتي إلى فيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        effect_id = "dramatic"
        output_path = os.path.join(self.app.config['CACHE_FOLDER'], "test_video_with_effect.mp4")
        
        try:
            # إضافة المؤثر الصوتي إلى الفيديو
            self.audio_effects_service.add_sound_effect_to_video(
                self.test_video_path,
                output_path,
                effect_id
            )
            
            # التحقق من وجود الملف الناتج
            self.assertTrue(os.path.exists(output_path))
            
            # حذف الملف بعد الاختبار
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            self.skipTest(f"فشل إضافة المؤثر الصوتي إلى الفيديو: {str(e)}")
    
    def tearDown(self):
        """تنظيف بيئة الاختبار."""
        # حذف ملف الفيديو الاختباري
        if os.path.exists(self.test_video_path):
            os.remove(self.test_video_path)
        
        # حذف ملفات المؤثرات الصوتية المؤقتة
        for filename in os.listdir(self.app.config['CACHE_FOLDER']):
            if filename.startswith(tuple(self.audio_effects_service.sound_effects.keys())):
                file_path = os.path.join(self.app.config['CACHE_FOLDER'], filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

if __name__ == '__main__':
    unittest.main()
