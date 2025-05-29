# دليل استخدام الخادم الخلفي لموقع Viral Clip Generator

## مقدمة

هذا الدليل يشرح كيفية استخدام وتشغيل الخادم الخلفي لموقع Viral Clip Generator. الخادم الخلفي مسؤول عن تنزيل فيديوهات YouTube، معالجة الفيديو، وإضافة المؤثرات الصوتية لإنشاء مقاطع فيديو فيروسية.

## متطلبات النظام

- Python 3.8 أو أحدث
- FFmpeg (مطلوب لمعالجة الفيديو)
- مساحة تخزين كافية للفيديوهات المؤقتة والمعالجة

## التثبيت

1. قم بتثبيت FFmpeg على نظامك:
   - على Ubuntu: `sudo apt-get install ffmpeg`
   - على macOS: `brew install ffmpeg`
   - على Windows: قم بتنزيل وتثبيت FFmpeg من الموقع الرسمي

2. قم بإنشاء بيئة Python افتراضية:
   ```bash
   python -m venv venv
   source venv/bin/activate  # على Linux/macOS
   venv\Scripts\activate  # على Windows
   ```

3. قم بتثبيت المتطلبات:
   ```bash
   pip install -r backend/requirements.txt
   ```

## هيكل المشروع

```
viral_clip_generator/
├── backend/
│   ├── api/
│   │   ├── device.py
│   │   ├── video.py
│   │   └── youtube.py
│   ├── config/
│   │   └── config.py
│   ├── models/
│   ├── services/
│   │   ├── audio_effects_service.py
│   │   ├── video_service.py
│   │   └── youtube_service.py
│   ├── tests/
│   │   ├── test_audio_effects_service.py
│   │   ├── test_endpoint_integration.py
│   │   ├── test_video_service.py
│   │   └── test_youtube_service.py
│   ├── utils/
│   │   ├── advanced_logging.py
│   │   ├── cache_manager.py
│   │   ├── error_handler.py
│   │   └── performance_optimization.py
│   ├── app.py
│   └── requirements.txt
└── src/
    ├── static/
    │   ├── css/
    │   │   └── compatibility.css
    │   └── js/
    │       └── compatibility.js
    └── templates/
        └── index.html
```

## تشغيل الخادم

1. قم بتشغيل الخادم الخلفي:
   ```bash
   cd viral_clip_generator
   python backend/app.py
   ```

2. سيتم تشغيل الخادم على المنفذ 5000 افتراضيًا. يمكنك الوصول إليه على العنوان:
   ```
   http://localhost:5000
   ```

## نقاط النهاية API

### فحص الصحة

- **GET /api/health**
  - الوصف: التحقق من حالة الخادم
  - الاستجابة: `{"status": "ok"}`

### معلومات الجهاز

- **GET /api/device/info**
  - الوصف: الحصول على معلومات الجهاز والمتصفح
  - الاستجابة: معلومات الجهاز والمتصفح ونظام التشغيل

### YouTube

- **GET /api/youtube/info**
  - الوصف: الحصول على معلومات فيديو YouTube
  - المعلمات: `videoId` (معرف الفيديو أو رابط YouTube)
  - الاستجابة: معلومات الفيديو (العنوان، المؤلف، المدة، الدقة المتاحة)

- **POST /api/youtube/download**
  - الوصف: تنزيل فيديو YouTube
  - المعلمات: `videoId` (معرف الفيديو أو رابط YouTube)، `resolution` (الدقة المطلوبة)
  - الاستجابة: معلومات الفيديو المنزل (المعرف، المسار)

### الفيديو

- **POST /api/video/upload**
  - الوصف: رفع ملف فيديو
  - المعلمات: `file` (ملف الفيديو)
  - الاستجابة: معلومات الفيديو المرفوع (المعرف، المسار)

- **GET /api/video/analyze**
  - الوصف: تحليل الفيديو لتحديد اللحظات المثيرة
  - المعلمات: `videoId` (معرف الفيديو)
  - الاستجابة: نتائج التحليل (وقت البداية، المدة، مستوى الثقة)

- **POST /api/video/process**
  - الوصف: معالجة الفيديو وإضافة المؤثرات الصوتية
  - المعلمات: `videoId` (معرف الفيديو)، `startTime` (وقت البداية)، `duration` (المدة)، `soundEffect` (معرف المؤثر الصوتي)
  - الاستجابة: معلومات الفيديو المعالج (المعرف، المدة، الرابط)

- **GET /api/video/{videoId}**
  - الوصف: الحصول على الفيديو المعالج
  - المعلمات: `videoId` (معرف الفيديو)
  - الاستجابة: ملف الفيديو

- **GET /api/video/{videoId}/thumbnail**
  - الوصف: الحصول على الصورة المصغرة للفيديو
  - المعلمات: `videoId` (معرف الفيديو)
  - الاستجابة: ملف الصورة المصغرة

### المؤثرات الصوتية

- **GET /api/audio/effects**
  - الوصف: الحصول على قائمة المؤثرات الصوتية المتاحة
  - الاستجابة: قائمة المؤثرات الصوتية (المعرف، الاسم، الوصف)

## أمثلة الاستخدام

### تنزيل ومعالجة فيديو YouTube

1. الحصول على معلومات الفيديو:
   ```bash
   curl -X GET "http://localhost:5000/api/youtube/info?videoId=dQw4w9WgXcQ"
   ```

2. تنزيل الفيديو:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"videoId": "dQw4w9WgXcQ", "resolution": "720p"}' "http://localhost:5000/api/youtube/download"
   ```

3. تحليل الفيديو:
   ```bash
   curl -X GET "http://localhost:5000/api/video/analyze?videoId=VIDEO_ID"
   ```

4. معالجة الفيديو:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"videoId": "VIDEO_ID", "startTime": 10, "duration": 15, "soundEffect": "dramatic"}' "http://localhost:5000/api/video/process"
   ```

5. الحصول على الفيديو المعالج:
   ```bash
   curl -X GET "http://localhost:5000/api/video/PROCESSED_VIDEO_ID" -o processed_video.mp4
   ```

## تحسين الأداء

الخادم الخلفي مصمم لتقليل استهلاك الموارد مع الحفاظ على الأداء العالي:

1. **التخزين المؤقت**: يتم تخزين نتائج العمليات المتكررة مثل معلومات الفيديو والتحليل.
2. **ضغط البيانات**: يتم ضغط الاستجابات لتقليل استهلاك النطاق الترددي.
3. **تنظيف الملفات المؤقتة**: يتم تنظيف الملفات المؤقتة تلقائيًا بعد فترة محددة.
4. **تحسين FFmpeg**: يتم استخدام إعدادات FFmpeg المحسنة لتقليل استهلاك وحدة المعالجة المركزية والذاكرة.

## استكشاف الأخطاء وإصلاحها

1. **مشكلة في تنزيل فيديو YouTube**:
   - تأكد من صحة معرف الفيديو أو الرابط.
   - تحقق من توفر الدقة المطلوبة.
   - تحقق من اتصالك بالإنترنت.

2. **مشكلة في معالجة الفيديو**:
   - تأكد من تثبيت FFmpeg بشكل صحيح.
   - تحقق من وجود مساحة تخزين كافية.
   - تحقق من صحة معلمات المعالجة (وقت البداية، المدة).

3. **مشكلة في الأداء**:
   - قم بزيادة قيمة `CACHE_TIMEOUT` في ملف التكوين.
   - قم بتقليل قيمة `VIDEO_CRF` لتقليل جودة الفيديو وحجمه.
   - قم بزيادة قيمة `CLEANUP_INTERVAL` لتقليل تكرار تنظيف الملفات المؤقتة.

## الخاتمة

هذا الخادم الخلفي مصمم لتوفير تجربة سلسة وفعالة لإنشاء مقاطع فيديو فيروسية من فيديوهات YouTube. يمكن تخصيصه وتوسيعه حسب احتياجاتك الخاصة.
