document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add active class to current nav item
    highlightCurrentNavItem();

    // File input custom text
    setupFileInputs();

    // Confirmation for delete actions
    setupDeleteConfirmations();

    // Add smooth scrolling to all links
    setupSmoothScrolling();

    // Animate elements when they come into view
    setupScrollAnimations();

    // Setup mobile menu toggle
    setupMobileMenu();

    // Setup card hover effects
    setupCardHoverEffects();
});

// Highlight current nav item based on URL
function highlightCurrentNavItem() {
    var currentLocation = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function(link) {
        var linkPath = link.getAttribute('href');
        if (linkPath && (currentLocation === linkPath ||
            (currentLocation.startsWith(linkPath) && linkPath !== '/' && linkPath.length > 1))) {
            link.classList.add('active');

            // Also highlight parent dropdown if inside one
            var dropdown = link.closest('.dropdown');
            if (dropdown) {
                dropdown.querySelector('.dropdown-toggle').classList.add('active');
            }
        }
    });
}

// Setup custom file inputs
function setupFileInputs() {
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = this.files[0].name;
            var nextSibling = this.nextElementSibling;
            nextSibling.innerText = fileName;
        });
    });
}

// Setup delete confirmations
function setupDeleteConfirmations() {
    document.querySelectorAll('.btn-delete, [data-confirm]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item? This action cannot be undone.';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// Setup smooth scrolling
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70, // Offset for fixed header
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Setup scroll animations
function setupScrollAnimations() {
    // Only run if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        const appearItems = document.querySelectorAll('.appear-animation');

        const appearOnScroll = new IntersectionObserver(function(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('appear');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        appearItems.forEach(item => {
            appearOnScroll.observe(item);
        });
    }
}

// Setup mobile menu toggle
function setupMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
}

// Setup card hover effects
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// Add animation class to elements
function addAppearAnimations() {
    const animationElements = [
        { selector: '.card', baseDelay: 0 },
        { selector: '.jumbotron', baseDelay: 0 },
        { selector: '.profile-img', baseDelay: 0 },
        { selector: '.list-group-item', baseDelay: 50, increment: true }
    ];

    animationElements.forEach(element => {
        const items = document.querySelectorAll(element.selector);
        items.forEach((item, index) => {
            item.classList.add('appear-animation');

            const delay = element.increment ?
                element.baseDelay * index : element.baseDelay;

            if (delay > 0) {
                item.style.transitionDelay = delay + 'ms';
            }
        });
    });
}

// Call this function at the end of DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // Other initialization functions...

    // Add appear animations
    addAppearAnimations();
});

// Create context-specific functions for the templates
function get_upcoming_events(limit) {
    // In a real application, this would query the database
    // For the template, we'll return an empty array
    return [];
}

function get_latest_team_stats() {
    // In a real application, this would query the database
    // For the template, we'll return null
    return null;
}

function get_recent_trophies(limit) {
    // In a real application, this would query the database
    // For the template, we'll return an empty array
    return [];
}

function get_recent_events(limit) {
    // In a real application, this would query the database
    // For the template, we'll return an empty array
    return [];
}

// Add some CSS animations
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .appear-animation {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .appear-animation.appear {
            opacity: 1;
            transform: translateY(0);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse {
            animation: pulse 2s infinite ease-in-out;
        }
    `;
    document.head.appendChild(style);
});