/**
 * تحسينات إضافية للتوافق مع iPhone وSafari
 * هذا الملف يحتوي على وظائف JavaScript لتحسين تجربة تشغيل الفيديو على مختلف الأجهزة
 */

// كشف نوع الجهاز والمتصفح بشكل دقيق
function detectDeviceAndBrowser() {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    
    // التحقق من نوع الجهاز
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    const isTablet = /iPad|Android(?!.*Mobile)/i.test(userAgent);
    
    // التحقق من نظام التشغيل
    const isIOS = /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
    const isAndroid = /Android/i.test(userAgent);
    
    // التحقق من المتصفح
    const isSafari = /^((?!chrome|android).)*safari/i.test(userAgent);
    const isChrome = /Chrome/i.test(userAgent) && !/Edge|Edg/i.test(userAgent);
    const isFirefox = /Firefox/i.test(userAgent);
    const isEdge = /Edge|Edg/i.test(userAgent);
    
    return {
        isMobile,
        isTablet,
        isIOS,
        isAndroid,
        isSafari,
        isChrome,
        isFirefox,
        isEdge,
        userAgent
    };
}

// تطبيق تحسينات خاصة بالفيديو حسب نوع الجهاز
function applyVideoCompatibilityFixes() {
    const device = detectDeviceAndBrowser();
    const videos = document.querySelectorAll('video');
    
    videos.forEach(video => {
        // إعدادات عامة للتوافق
        video.setAttribute('playsinline', '');
        video.setAttribute('webkit-playsinline', '');
        
        // إصلاحات خاصة بـ iOS
        if (device.isIOS) {
            // تمكين التشغيل التلقائي بدون صوت على iOS
            video.setAttribute('muted', '');
            video.muted = true;
            
            // إضافة معالج أحداث للنقر لتمكين الصوت
            video.addEventListener('click', function() {
                if (this.muted) {
                    this.muted = false;
                }
            });
            
            // إصلاح مشكلة التشغيل التلقائي
            video.addEventListener('loadedmetadata', function() {
                const playPromise = video.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        // السماح بالتفاعل اليدوي إذا فشل التشغيل التلقائي
                        console.log('تم منع التشغيل التلقائي:', error);
                    });
                }
            });
        }
        
        // إصلاحات خاصة بـ Safari
        if (device.isSafari) {
            // التأكد من تحميل الفيديو بشكل صحيح
            video.addEventListener('error', function(e) {
                console.error('خطأ في تحميل الفيديو:', e);
                
                // إعادة تحميل الفيديو بتنسيق متوافق
                const source = video.querySelector('source');
                if (source && source.src.endsWith('.mp4') === false) {
                    const newSrc = source.src.replace(/\.[^/.]+$/, '.mp4');
                    source.src = newSrc;
                    video.load();
                }
            });
        }
    });
    
    // تسجيل معلومات الجهاز للتشخيص
    console.log('معلومات الجهاز:', device);
}

// تحسين روابط التنزيل
function enhanceDownloadLinks() {
    const device = detectDeviceAndBrowser();
    const downloadLinks = document.querySelectorAll('a[download]');
    
    downloadLinks.forEach(link => {
        // إصلاح مشكلة التنزيل على iOS
        if (device.isIOS) {
            link.addEventListener('click', function(e) {
                // على iOS، قد لا يعمل سمة التنزيل، لذا نفتح في نافذة جديدة
                if (!confirm('سيتم فتح الفيديو في نافذة جديدة. اضغط على "حفظ" أو اضغط مطولاً على الفيديو لتنزيله.')) {
                    e.preventDefault();
                    return false;
                }
                
                this.setAttribute('target', '_blank');
                return true;
            });
        }
        
        // تحسين تجربة التنزيل على الأجهزة المحمولة
        if (device.isMobile) {
            link.addEventListener('click', function() {
                // إضافة تأكيد للتنزيل على الأجهزة المحمولة
                gtag('event', 'download_attempt', {
                    'device_type': device.isMobile ? 'mobile' : 'desktop',
                    'os': device.isIOS ? 'iOS' : (device.isAndroid ? 'Android' : 'Other'),
                    'browser': device.isSafari ? 'Safari' : (device.isChrome ? 'Chrome' : 'Other')
                });
            });
        }
    });
}

// تطبيق التحسينات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    applyVideoCompatibilityFixes();
    enhanceDownloadLinks();
    
    // إعادة تطبيق التحسينات عند تغيير محتوى الصفحة ديناميكياً
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                applyVideoCompatibilityFixes();
                enhanceDownloadLinks();
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});
