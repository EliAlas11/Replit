/**
 * تحسينات إضافية لخدمة الفيديو لأجهزة iPhone وSafari
 * هذا الملف يحتوي على وظائف Node.js لتحسين تقديم الفيديو على مختلف الأجهزة
 */

const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const mime = require('mime-types');

// تكوين خيارات التدفق للفيديو
const streamOptions = {
  highWaterMark: 64 * 1024, // تحسين حجم المخزن المؤقت
  defaultMaxListeners: 100 // زيادة الحد الأقصى للمستمعين
};

// تحسين تقديم الفيديو مع دعم التدفق الجزئي
router.get('/videos/:id', (req, res) => {
  const videoId = req.params.id;
  let videoPath = path.join(__dirname, '..', 'videos', 'processed', `${videoId}.mp4`);
  
  // التحقق من وجود الملف، وإذا لم يكن موجوداً استخدم ملف العينة
  if (!fs.existsSync(videoPath)) {
    videoPath = path.join(__dirname, '..', 'videos', 'sample.mp4');
    if (!fs.existsSync(videoPath)) {
      return res.status(404).send('الفيديو غير موجود');
    }
  }
  
  // الحصول على معلومات الملف
  const stat = fs.statSync(videoPath);
  const fileSize = stat.size;
  const mimeType = mime.lookup(videoPath) || 'video/mp4';
  
  // التعامل مع طلبات النطاق (Range requests) للتدفق الجزئي
  const range = req.headers.range;
  
  if (range) {
    // تحليل نطاق الطلب
    const parts = range.replace(/bytes=/, '').split('-');
    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
    const chunkSize = (end - start) + 1;
    
    // إعداد الرأس للتدفق الجزئي
    const headers = {
      'Content-Range': `bytes ${start}-${end}/${fileSize}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': chunkSize,
      'Content-Type': mimeType,
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=3600'
    };
    
    // إضافة رؤوس خاصة لـ Safari
    const userAgent = req.headers['user-agent'] || '';
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      headers['X-Content-Type-Options'] = 'nosniff';
    }
    
    // إضافة رؤوس خاصة لـ iOS
    if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      headers['X-Playback-Session-Id'] = req.query.playbackSessionId || Date.now().toString();
    }
    
    // إرسال استجابة جزئية
    res.writeHead(206, headers);
    
    // إنشاء تدفق للجزء المطلوب من الملف
    const fileStream = fs.createReadStream(videoPath, {
      ...streamOptions,
      start,
      end
    });
    
    // معالجة أخطاء التدفق
    fileStream.on('error', (error) => {
      console.error('خطأ في تدفق الفيديو:', error);
      if (!res.headersSent) {
        res.status(500).send('خطأ في تدفق الفيديو');
      } else {
        res.end();
      }
    });
    
    // تدفق البيانات إلى الاستجابة
    fileStream.pipe(res);
  } else {
    // إذا لم يتم تحديد نطاق، إرسال الملف كاملاً
    const headers = {
      'Content-Length': fileSize,
      'Content-Type': mimeType,
      'Accept-Ranges': 'bytes',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=3600'
    };
    
    // إضافة رؤوس خاصة لـ Safari
    const userAgent = req.headers['user-agent'] || '';
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      headers['X-Content-Type-Options'] = 'nosniff';
    }
    
    res.writeHead(200, headers);
    
    // إنشاء تدفق للملف كاملاً
    const fileStream = fs.createReadStream(videoPath, streamOptions);
    
    // معالجة أخطاء التدفق
    fileStream.on('error', (error) => {
      console.error('خطأ في تدفق الفيديو:', error);
      if (!res.headersSent) {
        res.status(500).send('خطأ في تدفق الفيديو');
      } else {
        res.end();
      }
    });
    
    // تدفق البيانات إلى الاستجابة
    fileStream.pipe(res);
  }
});

// تحسين تنزيل الفيديو
router.get('/download/:id', (req, res) => {
  const videoId = req.params.id;
  let videoPath = path.join(__dirname, '..', 'videos', 'processed', `${videoId}.mp4`);
  
  // التحقق من وجود الملف، وإذا لم يكن موجوداً استخدم ملف العينة
  if (!fs.existsSync(videoPath)) {
    videoPath = path.join(__dirname, '..', 'videos', 'sample.mp4');
    if (!fs.existsSync(videoPath)) {
      return res.status(404).send('الفيديو غير موجود');
    }
  }
  
  // الحصول على معلومات الملف
  const stat = fs.statSync(videoPath);
  const fileSize = stat.size;
  const fileName = `viral-clip-${videoId}.mp4`;
  
  // إعداد الرأس للتنزيل
  const headers = {
    'Content-Length': fileSize,
    'Content-Type': 'video/mp4',
    'Content-Disposition': `attachment; filename="${fileName}"`,
    'Access-Control-Allow-Origin': '*'
  };
  
  // إضافة رؤوس خاصة لـ Safari
  const userAgent = req.headers['user-agent'] || '';
  if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
    headers['X-Content-Type-Options'] = 'nosniff';
  }
  
  // إضافة رؤوس خاصة لـ iOS
  if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
    // تغيير طريقة التنزيل لـ iOS
    headers['Content-Disposition'] = `inline; filename="${fileName}"`;
  }
  
  res.writeHead(200, headers);
  
  // إنشاء تدفق للملف
  const fileStream = fs.createReadStream(videoPath, streamOptions);
  
  // معالجة أخطاء التدفق
  fileStream.on('error', (error) => {
    console.error('خطأ في تنزيل الفيديو:', error);
    if (!res.headersSent) {
      res.status(500).send('خطأ في تنزيل الفيديو');
    } else {
      res.end();
    }
  });
  
  // تدفق البيانات إلى الاستجابة
  fileStream.pipe(res);
});

module.exports = router;
