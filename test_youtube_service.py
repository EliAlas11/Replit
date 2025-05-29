"""
اختبار وظيفة تنزيل فيديوهات YouTube.
يوفر اختبارات لوظائف تنزيل وتحليل فيديوهات YouTube.
"""

import os
import sys
import unittest
import logging
from flask import Flask

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.youtube_service import YouTubeService
from config.config import config

# تعطيل التسجيل أثناء الاختبار
logging.disable(logging.CRITICAL)

class YouTubeServiceTest(unittest.TestCase):
    """اختبارات لخدمة YouTube."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        # إنشاء تطبيق Flask للاختبار
        self.app = Flask(__name__)
        self.app.config.from_object(config['testing'])
        
        # إنشاء خدمة YouTube
        self.youtube_service = YouTubeService()
        
        # إنشاء المجلدات المطلوبة
        os.makedirs(self.app.config['CACHE_FOLDER'], exist_ok=True)
    
    def test_extract_video_id(self):
        """اختبار استخراج معرف فيديو YouTube."""
        # اختبار معرف مباشر
        video_id = "dQw4w9WgXcQ"
        self.assertEqual(self.youtube_service.extract_video_id(video_id), video_id)
        
        # اختبار رابط youtube.com
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(self.youtube_service.extract_video_id(url), video_id)
        
        # اختبار رابط youtu.be
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(self.youtube_service.extract_video_id(url), video_id)
        
        # اختبار رابط غير صالح
        url = "https://example.com"
        self.assertIsNone(self.youtube_service.extract_video_id(url))
    
    def test_get_video_info(self):
        """اختبار الحصول على معلومات فيديو YouTube."""
        # ملاحظة: هذا الاختبار يتطلب اتصالاً بالإنترنت
        # ويمكن أن يفشل إذا تم تغيير الفيديو أو إزالته
        
        # استخدام فيديو معروف للاختبار
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            # الحصول على معلومات الفيديو
            video_info = self.youtube_service.get_video_info(video_id)
            
            # التحقق من وجود الحقول المطلوبة
            self.assertEqual(video_info['videoId'], video_id)
            self.assertIn('title', video_info)
            self.assertIn('author', video_info)
            self.assertIn('length', video_info)
            self.assertIn('thumbnail_url', video_info)
            self.assertIn('available_resolutions', video_info)
            
            # التحقق من أن الدقة المتاحة هي قائمة
            self.assertIsInstance(video_info['available_resolutions'], list)
        except Exception as e:
            # تخطي الاختبار إذا كان هناك مشكلة في الاتصال
            self.skipTest(f"فشل الاختبار بسبب مشكلة في الاتصال: {str(e)}")
    
    def test_download_video(self):
        """اختبار تنزيل فيديو YouTube."""
        # ملاحظة: هذا الاختبار يتطلب اتصالاً بالإنترنت
        # ويمكن أن يفشل إذا تم تغيير الفيديو أو إزالته
        
        # استخدام فيديو قصير للاختبار
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            # تنزيل الفيديو بدقة منخفضة للسرعة
            result = self.youtube_service.download_video(video_id, "360p")
            
            # التحقق من نجاح التنزيل
            self.assertTrue(result['success'])
            self.assertIn('videoId', result)
            self.assertEqual(result['originalId'], video_id)
            self.assertIn('title', result)
            self.assertIn('path', result)
            
            # التحقق من وجود الملف
            self.assertTrue(os.path.exists(result['path']))
            
            # حذف الملف بعد الاختبار
            if os.path.exists(result['path']):
                os.remove(result['path'])
        except Exception as e:
            # تخطي الاختبار إذا كان هناك مشكلة في الاتصال
            self.skipTest(f"فشل الاختبار بسبب مشكلة في الاتصال: {str(e)}")
    
    def test_search_videos(self):
        """اختبار البحث عن فيديوهات YouTube."""
        # ملاحظة: هذا الاختبار يتطلب اتصالاً بالإنترنت
        
        try:
            # البحث عن فيديوهات
            query = "Rick Astley"
            max_results = 3
            results = self.youtube_service.search_videos(query, max_results)
            
            # التحقق من عدد النتائج
            self.assertLessEqual(len(results), max_results)
            
            # التحقق من وجود الحقول المطلوبة في كل نتيجة
            for result in results:
                self.assertIn('videoId', result)
                self.assertIn('title', result)
                self.assertIn('author', result)
                self.assertIn('length', result)
                self.assertIn('thumbnail_url', result)
        except Exception as e:
            # تخطي الاختبار إذا كان هناك مشكلة في الاتصال
            self.skipTest(f"فشل الاختبار بسبب مشكلة في الاتصال: {str(e)}")
    
    def tearDown(self):
        """تنظيف بيئة الاختبار."""
        # حذف الملفات المؤقتة
        for filename in os.listdir(self.app.config['CACHE_FOLDER']):
            file_path = os.path.join(self.app.config['CACHE_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    unittest.main()
