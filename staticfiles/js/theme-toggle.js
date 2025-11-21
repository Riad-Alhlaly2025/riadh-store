/* 💡 تبديل الوضع (داكن ↔ فاتح) لمتجر رياض الإلكتروني */

// Ripple effect function
function createRipple(event) {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
    circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
    circle.classList.add('ripple');
    
    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
}

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // التحقق من التفضيل المحفوظ في localStorage
    const savedTheme = localStorage.getItem('themeMode') || 'dark';
    if (savedTheme === 'light') {
        body.classList.remove('theme-dark');
        body.classList.add('theme-light');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    } else {
        body.classList.add('theme-dark');
        body.classList.remove('theme-light');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }

    // Add ripple effect to all icon buttons
    const iconButtons = document.querySelectorAll('.icon-btn');
    iconButtons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
    
    // عند الضغط على زر تبديل الوضع
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            // إضافة تأثير انتقال
            themeToggle.style.transform = 'rotate(180deg) scale(1.2)';
            setTimeout(() => {
                themeToggle.style.transform = 'rotate(0deg) scale(1)';
            }, 300);
            
            // تبديل الوضع
            if (body.classList.contains('theme-dark')) {
                body.classList.remove('theme-dark');
                body.classList.add('theme-light');
                localStorage.setItem('themeMode', 'light');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                body.classList.remove('theme-light');
                body.classList.add('theme-dark');
                localStorage.setItem('themeMode', 'dark');
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            }
        });
    }
    
    // Add prefers-color-scheme support
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    if (savedTheme === 'dark' || (savedTheme !== 'light' && prefersDarkScheme.matches)) {
        body.classList.add('theme-dark');
        body.classList.remove('theme-light');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    } else {
        body.classList.remove('theme-dark');
        body.classList.add('theme-light');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
    
    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('themeMode')) {
            if (e.matches) {
                body.classList.add('theme-dark');
                body.classList.remove('theme-light');
                if (themeToggle) {
                    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                }
            } else {
                body.classList.remove('theme-dark');
                body.classList.add('theme-light');
                if (themeToggle) {
                    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                }
            }
        }
    });
});