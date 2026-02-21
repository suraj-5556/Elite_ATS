// Global utilities
const navLinks = document.querySelectorAll('.nav-link');
const currentPath = window.location.pathname;

navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath || 
        (currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/')) {
        link.style.color = 'rgba(255,255,255,0.95)';
        link.style.background = 'rgba(124, 58, 237, 0.15)';
    }
});

// Intersection Observer for animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.step-card, .tech-item, .stat-card, .job-card').forEach(el => {
    observer.observe(el);
});
