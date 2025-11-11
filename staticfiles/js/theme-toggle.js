/* 💡 تبديل الوضع (داكن ↔ فاتح) لمتجر رياض الإلكتروني */

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

  // التحقق من التفضيل المحفوظ في localStorage
    const savedTheme = localStorage.getItem('themeMode');
    if (savedTheme === 'light') {
    body.classList.remove('theme-dark');
    body.classList.add('theme-light');
    themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
    } else {
    body.classList.add('theme-dark');
    themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }

  // عند الضغط على الزر
    themeToggle.addEventListener('click', () => {
    if (body.classList.contains('theme-dark')) {
        body.classList.remove('theme-dark');
        body.classList.add('theme-light');
        localStorage.setItem('themeMode', 'light');
        themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
    } else {
        body.classList.remove('theme-light');
        body.classList.add('theme-dark');
        localStorage.setItem('themeMode', 'dark');
        themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }
    });
});