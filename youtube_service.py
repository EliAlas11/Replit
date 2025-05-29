"""
خدمة YouTube.
توفر وظائف للبحث وتنزيل فيديوهات YouTube.
"""

import os
import re
import uuid
import logging
from flask import current_app
from pytube import YouTube, Search
from urllib.parse import urlparse, parse_qs

from ..utils.error_handler import YouTubeError

logger = logging.getLogger(__name__)

class YouTubeService:
    """
    خدمة للتعامل مع فيديوهات YouTube.
    توفر وظائف للبحث وتنزيل الفيديوهات.
    """
    
    def __init__(self):
        """تهيئة خدمة YouTube."""
        pass
    
    def extract_video_id(self, video_id_or_url):
        """
        استخراج معرف فيديو YouTube من رابط أو معرف.
        
        المعلمات:
            video_id_or_url (str): معرف الفيديو أو رابط YouTube.
        
        العائد:
            str: معرف فيديو YouTube، أو None إذا لم يتم العثور على معرف صالح.
        """
        # التحقق مما إذا كان المدخل هو معرف فيديو مباشر
        if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id_or_url):
            return video_id_or_url
        
        # محاولة استخراج معرف الفيديو من الرابط
        try:
            # التعامل مع روابط youtu.be
            if 'youtu.be' in video_id_or_url:
                path = urlparse(video_id_or_url).path
                return path.strip('/')
            
            # التعامل مع روابط youtube.com
            if 'youtube.com' in video_id_or_url:
                query = urlparse(video_id_or_url).query
                params = parse_qs(query)
                if 'v' in params:
                    return params['v'][0]
            
            # لم يتم العثور على معرف فيديو صالح
            logger.warning(f"لم يتم العثور على معرف فيديو صالح في: {video_id_or_url}")
            return None
        except Exception as e:
            logger.error(f"خطأ في استخراج معرف فيديو YouTube: {str(e)}")
            return None
    
    def get_video_info(self, video_id):
        """
        الحصول على معلومات فيديو YouTube.
        
        المعلمات:
            video_id (str): معرف فيديو YouTube.
        
        العائد:
            dict: معلومات الفيديو.
        
        يرفع:
            YouTubeError: إذا حدث خطأ أثناء الحصول على معلومات الفيديو.
        """
        try:
            # إنشاء كائن YouTube
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            
            # الحصول على معلومات الفيديو
            video_info = {
                "videoId": video_id,
                "title": yt.title,
                "author": yt.author,
                "length": yt.length,
                "thumbnail_url": yt.thumbnail_url,
                "available_resolutions": []
            }
            
            # الحصول على الدقة المتاحة
            for stream in yt.streams.filter(progressive=True):
                if stream.resolution:
                    video_info["available_resolutions"].append(stream.resolution)
            
            # إزالة التكرارات وترتيب الدقة
            video_info["available_resolutions"] = sorted(
                list(set(video_info["available_resolutions"])),
                key=lambda x: int(x.replace('p', '')),
                reverse=True
            )
            
            return video_info
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات فيديو YouTube: {str(e)}")
            raise YouTubeError(f"خطأ في الحصول على معلومات الفيديو: {str(e)}")
    
    def download_video(self, video_id, resolution=None):
        """
        تنزيل فيديو YouTube.
        
        المعلمات:
            video_id (str): معرف فيديو YouTube.
            resolution (str, اختياري): الدقة المطلوبة (مثل "720p").
        
        العائد:
            dict: معلومات الفيديو المنزل.
        
        يرفع:
            YouTubeError: إذا حدث خطأ أثناء تنزيل الفيديو.
        """
        try:
            # إنشاء كائن YouTube
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            
            # تحديد الدقة المطلوبة
            if not resolution:
                resolution = current_app.config['YOUTUBE_DEFAULT_RESOLUTION']
            
            # البحث عن التدفق المناسب
            stream = yt.streams.filter(progressive=True, resolution=resolution).first()
            
            # إذا لم يتم العثور على التدفق المطلوب، استخدام دقة بديلة
            if not stream:
                fallback_resolution = current_app.config['YOUTUBE_FALLBACK_RESOLUTION']
                logger.warning(f"لم يتم العثور على دقة {resolution}، استخدام {fallback_resolution} بدلاً من ذلك")
                stream = yt.streams.filter(progressive=True, resolution=fallback_resolution).first()
            
            # إذا لم يتم العثور على أي تدفق، استخدام أعلى دقة متاحة
            if not stream:
                logger.warning(f"لم يتم العثور على دقة محددة، استخدام أعلى دقة متاحة")
                stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
            
            # إذا لم يتم العثور على أي تدفق، رفع خطأ
            if not stream:
                raise YouTubeError("لم يتم العثور على تدفق فيديو مناسب")
            
            # إنشاء معرف فريد للفيديو المنزل
            local_id = str(uuid.uuid4())
            
            # تحديد مسار الحفظ
            filename = f"{local_id}.mp4"
            output_path = os.path.join(current_app.config['CACHE_FOLDER'], filename)
            
            # تنزيل الفيديو
            logger.info(f"جاري تنزيل فيديو YouTube: {video_id} بدقة {stream.resolution}")
            stream.download(output_path=os.path.dirname(output_path), filename=filename)
            
            # التحقق من وجود الملف
            if not os.path.exists(output_path):
                raise YouTubeError("فشل تنزيل الفيديو")
            
            # إرجاع معلومات الفيديو المنزل
            return {
                "success": True,
                "videoId": local_id,
                "originalId": video_id,
                "title": yt.title,
                "path": output_path
            }
        except Exception as e:
            logger.error(f"خطأ في تنزيل فيديو YouTube: {str(e)}")
            raise YouTubeError(f"خطأ في تنزيل الفيديو: {str(e)}")
    
    def search_videos(self, query, max_results=10):
        """
        البحث عن فيديوهات YouTube.
        
        المعلمات:
            query (str): استعلام البحث.
            max_results (int, اختياري): الحد الأقصى لعدد النتائج.
        
        العائد:
            list: قائمة نتائج البحث.
        
        يرفع:
            YouTubeError: إذا حدث خطأ أثناء البحث.
        """
        try:
            # إنشاء كائن البحث
            search = Search(query)
            
            # الحصول على النتائج
            results = []
            for video in search.results[:max_results]:
                results.append({
                    "videoId": video.video_id,
                    "title": video.title,
                    "author": video.author,
                    "length": video.length,
                    "thumbnail_url": video.thumbnail_url
                })
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث في YouTube: {str(e)}")
            raise YouTubeError(f"خطأ في البحث: {str(e)}")
    
    def get_trending_videos(self, max_results=10, category=None):
        """
        الحصول على الفيديوهات الرائجة على YouTube.
        
        المعلمات:
            max_results (int, اختياري): الحد الأقصى لعدد النتائج.
            category (str, اختياري): فئة الفيديوهات.
        
        العائد:
            list: قائمة الفيديوهات الرائجة.
        
        يرفع:
            YouTubeError: إذا حدث خطأ أثناء الحصول على الفيديوهات الرائجة.
        """
        try:
            # ملاحظة: pytube لا توفر واجهة برمجة للفيديوهات الرائجة
            # في التطبيق الحقيقي، يمكن استخدام YouTube Data API
            # هنا نستخدم بيانات ثابتة للتوضيح
            
            # قائمة الفيديوهات الرائجة الافتراضية
            trending_videos = [
                {
                    "videoId": "dQw4w9WgXcQ",
                    "title": "Rick Astley - Never Gonna Give You Up",
                    "author": "Rick Astley",
                    "length": 213,
                    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
                },
                {
                    "videoId": "9bZkp7q19f0",
                    "title": "PSY - GANGNAM STYLE(강남스타일)",
                    "author": "officialpsy",
                    "length": 252,
                    "thumbnail_url": "https://i.ytimg.com/vi/9bZkp7q19f0/hqdefault.jpg"
                }
            ]
            
            # في التطبيق الحقيقي، يمكن تصفية النتائج حسب الفئة
            # هنا نتجاهل معلمة الفئة
            
            return trending_videos[:max_results]
        except Exception as e:
            logger.error(f"خطأ في الحصول على الفيديوهات الرائجة: {str(e)}")
            raise YouTubeError(f"خطأ في الحصول على الفيديوهات الرائجة: {str(e)}")
