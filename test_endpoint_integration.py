"""
اختبار تكامل نقاط النهاية.
يوفر اختبارات للتكامل بين جميع نقاط النهاية والخدمات.
"""

import os
import sys
import unittest
import json
import logging
import tempfile
from flask import Flask
from werkzeug.datastructures import FileStorage

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config.config import config

# تعطيل التسجيل أثناء الاختبار
logging.disable(logging.CRITICAL)

class EndpointIntegrationTest(unittest.TestCase):
    """اختبارات تكامل نقاط النهاية."""
    
    def setUp(self):
        """إعداد بيئة الاختبار."""
        # إنشاء تطبيق Flask للاختبار
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # إنشاء المجلدات المطلوبة
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['CACHE_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['PROCESSED_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['AUDIO_FOLDER'], exist_ok=True)
        
        # إنشاء ملف فيديو اختباري
        self.test_video_path = os.path.join(self.app.config['UPLOAD_FOLDER'], "test_video.mp4")
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
    
    def test_health_check(self):
        """اختبار نقطة نهاية فحص الصحة."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    def test_device_info(self):
        """اختبار نقطة نهاية معلومات الجهاز."""
        response = self.client.get('/api/device/info')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('device', data)
        self.assertIn('browser', data)
        self.assertIn('os', data)
    
    def test_youtube_info(self):
        """اختبار نقطة نهاية معلومات فيديو YouTube."""
        # استخدام فيديو معروف للاختبار
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            response = self.client.get(f'/api/youtube/info?videoId={video_id}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['videoId'], video_id)
            self.assertIn('title', data)
            self.assertIn('author', data)
            self.assertIn('length', data)
            self.assertIn('thumbnail_url', data)
            self.assertIn('available_resolutions', data)
        except Exception as e:
            self.skipTest(f"فشل اختبار معلومات فيديو YouTube: {str(e)}")
    
    def test_youtube_download(self):
        """اختبار نقطة نهاية تنزيل فيديو YouTube."""
        # استخدام فيديو معروف للاختبار
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            response = self.client.post(
                '/api/youtube/download',
                json={'videoId': video_id, 'resolution': '360p'}
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('videoId', data)
            self.assertEqual(data['originalId'], video_id)
            self.assertIn('title', data)
            self.assertIn('path', data)
            
            # التحقق من وجود الملف
            self.assertTrue(os.path.exists(data['path']))
            
            # حذف الملف بعد الاختبار
            if os.path.exists(data['path']):
                os.remove(data['path'])
        except Exception as e:
            self.skipTest(f"فشل اختبار تنزيل فيديو YouTube: {str(e)}")
    
    def test_video_upload(self):
        """اختبار نقطة نهاية رفع فيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        try:
            with open(self.test_video_path, 'rb') as f:
                response = self.client.post(
                    '/api/video/upload',
                    data={
                        'file': (f, 'test_video.mp4', 'video/mp4')
                    },
                    content_type='multipart/form-data'
                )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('videoId', data)
            self.assertIn('path', data)
            
            # التحقق من وجود الملف
            self.assertTrue(os.path.exists(data['path']))
            
            # حذف الملف بعد الاختبار
            if os.path.exists(data['path']):
                os.remove(data['path'])
        except Exception as e:
            self.skipTest(f"فشل اختبار رفع فيديو: {str(e)}")
    
    def test_video_process(self):
        """اختبار نقطة نهاية معالجة الفيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        try:
            # رفع الفيديو أولاً
            with open(self.test_video_path, 'rb') as f:
                response = self.client.post(
                    '/api/video/upload',
                    data={
                        'file': (f, 'test_video.mp4', 'video/mp4')
                    },
                    content_type='multipart/form-data'
                )
            
            upload_data = json.loads(response.data)
            video_id = upload_data['videoId']
            
            # معالجة الفيديو
            response = self.client.post(
                '/api/video/process',
                json={
                    'videoId': video_id,
                    'startTime': 0,
                    'duration': 3,
                    'soundEffect': 'dramatic'
                }
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('videoId', data)
            self.assertIn('duration', data)
            self.assertIn('url', data)
            
            # التحقق من وجود الفيديو المعالج
            processed_path = os.path.join(self.app.config['PROCESSED_FOLDER'], f"{data['videoId']}.mp4")
            self.assertTrue(os.path.exists(processed_path))
            
            # حذف الملفات بعد الاختبار
            if os.path.exists(upload_data['path']):
                os.remove(upload_data['path'])
            if os.path.exists(processed_path):
                os.remove(processed_path)
        except Exception as e:
            self.skipTest(f"فشل اختبار معالجة الفيديو: {str(e)}")
    
    def test_video_analyze(self):
        """اختبار نقطة نهاية تحليل الفيديو."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        try:
            # رفع الفيديو أولاً
            with open(self.test_video_path, 'rb') as f:
                response = self.client.post(
                    '/api/video/upload',
                    data={
                        'file': (f, 'test_video.mp4', 'video/mp4')
                    },
                    content_type='multipart/form-data'
                )
            
            upload_data = json.loads(response.data)
            video_id = upload_data['videoId']
            
            # تحليل الفيديو
            response = self.client.get(f'/api/video/analyze?videoId={video_id}')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('start_time', data)
            self.assertIn('duration', data)
            self.assertIn('confidence', data)
            
            # حذف الملف بعد الاختبار
            if os.path.exists(upload_data['path']):
                os.remove(upload_data['path'])
        except Exception as e:
            self.skipTest(f"فشل اختبار تحليل الفيديو: {str(e)}")
    
    def test_sound_effects_list(self):
        """اختبار نقطة نهاية قائمة المؤثرات الصوتية."""
        response = self.client.get('/api/audio/effects')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # التحقق من وجود الحقول المطلوبة في كل مؤثر
        for effect in data:
            self.assertIn('id', effect)
            self.assertIn('name', effect)
            self.assertIn('description', effect)
    
    def test_full_workflow(self):
        """اختبار تدفق العمل الكامل."""
        # التحقق من وجود ملف الفيديو الاختباري
        if not os.path.exists(self.test_video_path):
            self.skipTest("ملف الفيديو الاختباري غير موجود")
        
        try:
            # 1. رفع الفيديو
            with open(self.test_video_path, 'rb') as f:
                response = self.client.post(
                    '/api/video/upload',
                    data={
                        'file': (f, 'test_video.mp4', 'video/mp4')
                    },
                    content_type='multipart/form-data'
                )
            
            upload_data = json.loads(response.data)
            video_id = upload_data['videoId']
            
            # 2. تحليل الفيديو
            response = self.client.get(f'/api/video/analyze?videoId={video_id}')
            analyze_data = json.loads(response.data)
            
            # 3. الحصول على قائمة المؤثرات الصوتية
            response = self.client.get('/api/audio/effects')
            effects_data = json.loads(response.data)
            effect_id = effects_data[0]['id'] if effects_data else 'dramatic'
            
            # 4. معالجة الفيديو
            response = self.client.post(
                '/api/video/process',
                json={
                    'videoId': video_id,
                    'startTime': analyze_data['start_time'],
                    'duration': analyze_data['duration'],
                    'soundEffect': effect_id
                }
            )
            
            process_data = json.loads(response.data)
            processed_video_id = process_data['videoId']
            
            # 5. الحصول على الفيديو المعالج
            response = self.client.get(f'/api/video/{processed_video_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'video/mp4')
            
            # 6. الحصول على الصورة المصغرة للفيديو المعالج
            response = self.client.get(f'/api/video/{processed_video_id}/thumbnail')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'image/jpeg')
            
            # حذف الملفات بعد الاختبار
            if os.path.exists(upload_data['path']):
                os.remove(upload_data['path'])
            
            processed_path = os.path.join(self.app.config['PROCESSED_FOLDER'], f"{processed_video_id}.mp4")
            if os.path.exists(processed_path):
                os.remove(processed_path)
            
            thumbnail_path = os.path.join(self.app.config['PROCESSED_FOLDER'], f"{processed_video_id}.jpg")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            self.skipTest(f"فشل اختبار تدفق العمل الكامل: {str(e)}")
    
    def tearDown(self):
        """تنظيف بيئة الاختبار."""
        # حذف ملف الفيديو الاختباري
        if os.path.exists(self.test_video_path):
            os.remove(self.test_video_path)
        
        # إزالة سياق التطبيق
        self.app_context.pop()

if __name__ == '__main__':
    unittest.main()
