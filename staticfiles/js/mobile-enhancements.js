/* ===============================
   Mobile Enhancements for Luxury E-Commerce
   =============================== */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle functionality
    const mobileMenuButton = document.createElement('button');
    mobileMenuButton.className = 'mobile-menu-toggle';
    mobileMenuButton.setAttribute('aria-label', 'Toggle navigation menu');
    mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
    
    const headerInner = document.querySelector('.header-inner');
    if (headerInner) {
        headerInner.insertBefore(mobileMenuButton, headerInner.firstChild);
    }
    
    const navLinks = document.querySelector('.nav-links');
    
    mobileMenuButton.addEventListener('click', function() {
        navLinks.classList.toggle('mobile-open');
        this.classList.toggle('active');
        
        // Change icon based on state
        const icon = this.querySelector('i');
        if (navLinks.classList.contains('mobile-open')) {
            icon.className = 'fas fa-times';
        } else {
            icon.className = 'fas fa-bars';
        }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navLinks.classList.contains('mobile-open') && 
            !navLinks.contains(e.target) && 
            !mobileMenuButton.contains(e.target)) {
            navLinks.classList.remove('mobile-open');
            mobileMenuButton.classList.remove('active');
            mobileMenuButton.querySelector('i').className = 'fas fa-bars';
        }
    });
    
    // Enhanced touch support for product cards
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        // Add touch feedback
        card.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        card.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        });
        
        // Prevent accidental taps during scroll
        let touchStartTime = 0;
        card.addEventListener('touchstart', function() {
            touchStartTime = new Date().getTime();
        });
        
        card.addEventListener('touchend', function(e) {
            const touchEndTime = new Date().getTime();
            const touchDuration = touchEndTime - touchStartTime;
            
            // If touch duration is less than 100ms, it's likely a scroll, not a tap
            if (touchDuration < 100) {
                e.preventDefault();
            }
        });
    });
    
    // Mobile search enhancement
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // Add search focus enhancement for mobile
        searchInput.addEventListener('focus', function() {
            // Scroll to top on mobile when search is focused
            if (window.innerWidth <= 768) {
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        });
        
        // Add voice search support if available
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const voiceButton = document.createElement('button');
            voiceButton.type = 'button';
            voiceButton.className = 'voice-search-btn';
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceButton.setAttribute('aria-label', 'Voice search');
            
            searchInput.parentNode.style.position = 'relative';
            searchInput.parentNode.appendChild(voiceButton);
            
            voiceButton.addEventListener('click', function() {
                try {
                    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = document.documentElement.lang || 'en-US';
                    recognition.start();
                    
                    recognition.onresult = function(event) {
                        const transcript = event.results[0][0].transcript;
                        searchInput.value = transcript;
                        searchInput.dispatchEvent(new Event('input'));
                    };
                    
                    recognition.onerror = function(event) {
                        console.error('Speech recognition error', event.error);
                    };
                } catch (error) {
                    console.error('Voice search error:', error);
                }
            });
        }
    }
    
    // Mobile cart enhancements
    const cartButtons = document.querySelectorAll('.add-to-cart-btn');
    cartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add visual feedback for mobile
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            this.disabled = true;
            
            // Restore button after a short delay
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 1000);
        });
    });
    
    // Mobile-specific animations
    if (window.innerWidth <= 768) {
        // Add swipe gestures for product navigation
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        document.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipeGesture();
        });
        
        function handleSwipeGesture() {
            const swipeThreshold = 50;
            
            if (touchStartX - touchEndX > swipeThreshold) {
                // Swipe left - next product
                const nextButton = document.querySelector('.product-next-btn');
                if (nextButton) nextButton.click();
            }
            
            if (touchEndX - touchStartX > swipeThreshold) {
                // Swipe right - previous product
                const prevButton = document.querySelector('.product-prev-btn');
                if (prevButton) prevButton.click();
            }
        }
        
        // Add pull-to-refresh functionality
        let startY = 0;
        let currentY = 0;
        
        document.addEventListener('touchstart', e => {
            startY = e.touches[0].pageY;
        });
        
        document.addEventListener('touchmove', e => {
            currentY = e.touches[0].pageY;
            const diff = currentY - startY;
            
            // Only trigger on top of page
            if (window.scrollY === 0 && diff > 0) {
                document.body.style.transform = `translateY(${Math.min(diff / 3, 100)}px)`;
            }
        });
        
        document.addEventListener('touchend', () => {
            // Reset position
            document.body.style.transform = '';
            
            // Refresh if pulled enough
            const diff = currentY - startY;
            if (diff > 150) {
                window.location.reload();
            }
        });
    }
    
    // Performance optimization for mobile
    // Lazy load images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // Add reduced motion support
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) {
        // Disable animations for users who prefer reduced motion
        document.body.classList.add('reduce-motion');
    }
    
    // Add orientation change handling
    window.addEventListener('orientationchange', function() {
        // Reset any fixed positioning that might break on orientation change
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 100);
    });
    
    // Add PWA installation prompt support
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later
        deferredPrompt = e;
        
        // Show install button if desired
        // const installButton = document.getElementById('install-pwa');
        // if (installButton) {
        //     installButton.style.display = 'block';
        //     installButton.addEventListener('click', () => {
        //         // Hide the install button
        //         installButton.style.display = 'none';
        //         // Show the install prompt
        //         deferredPrompt.prompt();
        //         // Wait for the user to respond to the prompt
        //         deferredPrompt.userChoice.then((choiceResult) => {
        //             if (choiceResult.outcome === 'accepted') {
        //                 console.log('User accepted the install prompt');
        //             } else {
        //                 console.log('User dismissed the install prompt');
        //             }
        //             deferredPrompt = null;
        //         });
        //     });
        // }
    });
});