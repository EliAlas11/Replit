import os
import sys
import uuid
import json
import time
import random
from flask import Flask, request, jsonify, send_file, render_template, url_for
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import cv2
import numpy as np
from werkzeug.utils import secure_filename

# إعداد التطبيق
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['PROCESSED_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 ميجابايت كحد أقصى

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# التحقق من امتدادات الملفات المسموح بها
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# تنزيل فيديو من YouTube
def download_youtube_video(video_id):
    try:
        # إنشاء مسار الملف
        filename = f"{video_id}.mp4"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # التحقق مما إذا كان الفيديو موجودًا بالفعل
        if os.path.exists(filepath):
            return filepath
        
        # تنزيل الفيديو
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            raise Exception("لم يتم العثور على تدفق فيديو مناسب")
        
        # تنزيل الفيديو إلى المجلد المحدد
        stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)
        
        return filepath
    except Exception as e:
        print(f"خطأ في تنزيل فيديو YouTube: {str(e)}")
        raise

# تحليل الفيديو لتحديد اللحظات المثيرة
def analyze_video(video_path):
    try:
        # فتح الفيديو
        video = VideoFileClip(video_path)
        duration = video.duration
        
        # في التطبيق الحقيقي، سنستخدم خوارزميات معالجة الفيديو والذكاء الاصطناعي
        # لتحديد اللحظات المثيرة. هنا نستخدم محاكاة بسيطة.
        
        # تحديد مدة المقطع (بين 10 و 15 ثانية)
        clip_duration = min(random.randint(10, 15), duration)
        
        # تحديد وقت البداية (مع ترك مساحة كافية للمقطع)
        max_start_time = max(0, duration - clip_duration)
        start_time = random.uniform(0, max_start_time)
        
        # إغلاق الفيديو
        video.close()
        
        return {
            "start_time": start_time,
            "duration": clip_duration
        }
    except Exception as e:
        print(f"خطأ في تحليل الفيديو: {str(e)}")
        raise

# إضافة مؤثرات صوتية للفيديو
def add_sound_effects(video_path, start_time, duration):
    try:
        # إنشاء معرف فريد للملف
        output_id = str(uuid.uuid4())
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{output_id}.mp4")
        
        # قص المقطع المحدد من الفيديو
        video = VideoFileClip(video_path).subclip(start_time, start_time + duration)
        
        # قائمة المؤثرات الصوتية
        sound_effects = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds', 'suspense.mp3'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds', 'dramatic.mp3'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds', 'upbeat.mp3')
        ]
        
        # اختيار مؤثر صوتي عشوائي
        sound_effect_path = random.choice(sound_effects)
        
        # في التطبيق الحقيقي، سنتحقق من وجود الملف
        # هنا نتخطى ذلك للمحاكاة
        
        # إضافة المؤثر الصوتي (في التطبيق الحقيقي)
        # sound = AudioFileClip(sound_effect_path)
        # video = video.set_audio(sound)
        
        # حفظ الفيديو النهائي
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        # إغلاق الفيديو
        video.close()
        
        return output_id
    except Exception as e:
        print(f"خطأ في إضافة المؤثرات الصوتية: {str(e)}")
        raise

# المسارات (Routes)
@app.route('/api/process', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_id = data.get('videoId')
        
        if not video_id:
            return jsonify({"error": "معرف الفيديو مطلوب"}), 400
        
        # تنزيل الفيديو
        video_path = download_youtube_video(video_id)
        
        # تحليل الفيديو
        analysis = analyze_video(video_path)
        
        # إضافة المؤثرات الصوتية
        output_id = add_sound_effects(video_path, analysis['start_time'], analysis['duration'])
        
        return jsonify({
            "success": True,
            "videoId": output_id,
            "duration": analysis['duration']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video/<video_id>', methods=['GET'])
def get_video(video_id):
    try:
        video_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{video_id}.mp4")
        
        if not os.path.exists(video_path):
            return jsonify({"error": "الفيديو غير موجود"}), 404
        
        return send_file(video_path, mimetype='video/mp4')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/thumbnail/<video_id>', methods=['GET'])
def get_thumbnail(video_id):
    try:
        video_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{video_id}.mp4")
        thumbnail_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{video_id}_thumb.jpg")
        
        if not os.path.exists(video_path):
            return jsonify({"error": "الفيديو غير موجود"}), 404
        
        # إنشاء صورة مصغرة إذا لم تكن موجودة
        if not os.path.exists(thumbnail_path):
            video = cv2.VideoCapture(video_path)
            success, frame = video.read()
            
            if success:
                cv2.imwrite(thumbnail_path, frame)
                video.release()
            else:
                return jsonify({"error": "فشل في إنشاء صورة مصغرة"}), 500
        
        return send_file(thumbnail_path, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/device-info', methods=['POST'])
def device_info():
    try:
        data = request.json
        # تسجيل معلومات الجهاز للتحليل (في التطبيق الحقيقي)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# تشغيل التطبيق
if __name__ == '__main__':
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
