/* 🎯 شريط العروض المتحرك في متجر رياض الإلكتروني */

document.addEventListener('DOMContentLoaded', () => {
    const banner = document.getElementById('topBanner');
    if (!banner) return;

    const messages = [
    "🌟 خصومات هائلة على الإلكترونيات - حتى 60٪!",
    "🚚 توصيل مجاني للطلبات التي تزيد عن 300 ريال.",
    "💳 ادفع عند الاستلام أو عبر بطاقتك البنكية بسهولة.",
    "🎁 عروض نهاية الأسبوع تبدأ الآن — لا تفوّت الفرصة!"
    ];

    let index = 0;
    const textElement = banner.querySelector('.banner-text');

  // دالة لتغيير النص كل 5 ثوانٍ
    function rotateBanner() {
    textElement.style.opacity = 0;
    setTimeout(() => {
        index = (index + 1) % messages.length;
        textElement.innerHTML = messages[index];
        textElement.style.opacity = 1;
    }, 500);
    }

    setInterval(rotateBanner, 5000);

  // عند الضغط على × لإغلاق الشريط
    const closeBtn = document.getElementById('bannerClose');
    if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        banner.style.display = 'none';
        localStorage.setItem('bannerClosed', '1');
    });
    if (localStorage.getItem('bannerClosed') === '1') {
        banner.style.display = 'none';
    }
}
});