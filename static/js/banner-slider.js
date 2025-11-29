/* 🎯 شريط العروض المتحرك في متجر رياض الإلكتروني */

// Advanced animation functions
function animateElement(element, animationClass, duration = 600) {
    return new Promise(resolve => {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
            resolve();
        }, duration);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const banner = document.getElementById('topBanner');
    if (!banner) return;

    const messages = [
        "🌟 خصومات هائلة على الإلكترونيات - حتى 60٪!",
        "🚚 توصيل مجاني للطلبات التي تزيد عن 300 ريال.",
        "💳 ادفع عند الاستلام أو عبر بطاقتك البنكية بسهولة.",
        "🎁 عروض نهاية الأسبوع تبدأ الآن — لا تفوّت الفرصة!",
        "📱 أحدث الهواتف الذكية بأسعار لا تُقاوَم!",
        "💻 كمبيوترات محمولة بمواصفات عالية بخصومات مذهلة!",
        "🔥 عروض الصيف - خصومات تصل إلى 70% على جميع المنتجات!",
        "🎉 احتفالًا بالعيد - هدايا مجانية مع كل طلب!"
    ];

    let index = 0;
    const textElement = banner.querySelector('p');
    
    // إضافة كلاس للنص لتحسين التأثيرات
    if (textElement) {
        textElement.classList.add('banner-text');
        textElement.style.transition = 'opacity 0.5s ease-in-out';
        // Modern design enhancements
        textElement.style.willChange = 'opacity, transform';
    }

    // دالة لتغيير النص مع تأثيرات
    function rotateBanner() {
        if (textElement) {
            // Fade out with advanced animation
            animateElement(textElement, 'animate-fadeOut', 300).then(() => {
                index = (index + 1) % messages.length;
                textElement.innerHTML = messages[index];
                
                // Fade in with advanced animation
                animateElement(textElement, 'animate-fadeIn', 300);
                
                // Add advanced visual effects
                animateElement(textElement, 'animate-bounce', 1000);
            });
        }
    }

    // بدء الدوران كل 4 ثوانٍ
    let intervalId = setInterval(rotateBanner, 4000);

    // عند الضغط على × لإغلاق الشريط
    const closeBtn = document.getElementById('bannerClose');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            // إضافة تأثير اختفاء
            banner.style.opacity = 0;
            banner.style.transform = 'translateY(-100%)';
            banner.style.transition = 'all 0.5s ease-in-out';
            
            setTimeout(() => {
                banner.style.display = 'none';
                localStorage.setItem('bannerClosed', '1');
            }, 500);
        });
        
        if (localStorage.getItem('bannerClosed') === '1') {
            banner.style.display = 'none';
        }
        
        // Modern design enhancements
        // Add hover effect to close button
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.transform = 'scale(1.2) rotate(90deg)';
        });
        
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.transform = 'scale(1) rotate(0deg)';
        });
        
        // Add keyboard accessibility
        closeBtn.setAttribute('tabindex', '0');
        closeBtn.setAttribute('role', 'button');
        closeBtn.setAttribute('aria-label', 'إغلاق الشريط العلوي');
        
        closeBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                closeBtn.click();
            }
        });
    }
    
    // إضافة تأثيرات عند التمرير على الشريط
    banner.addEventListener('mouseenter', () => {
        clearInterval(intervalId);
    });
    
    banner.addEventListener('mouseleave', () => {
        intervalId = setInterval(rotateBanner, 4000);
    });
    
    // Modern responsive design enhancements
    // Pause animation on mobile to save battery
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        banner.addEventListener('touchstart', () => {
            clearInterval(intervalId);
        });
        
        banner.addEventListener('touchend', () => {
            intervalId = setInterval(rotateBanner, 4000);
        });
    }
    
    // Add reduced motion support
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) {
        clearInterval(intervalId);
        if (textElement) {
            textElement.style.transition = 'none';
        }
    }
    
    prefersReducedMotion.addEventListener('change', (e) => {
        if (e.matches) {
            clearInterval(intervalId);
            if (textElement) {
                textElement.style.transition = 'none';
            }
        } else {
            intervalId = setInterval(rotateBanner, 4000);
            if (textElement) {
                textElement.style.transition = 'opacity 0.5s ease-in-out';
            }
        }
    });
    
    // Add ARIA attributes for accessibility
    if (banner) {
        banner.setAttribute('role', 'banner');
        banner.setAttribute('aria-label', 'شريط العروض');
    }
});