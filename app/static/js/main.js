/**
 * Main JavaScript file for Football Team Web App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                const alert = new bootstrap.Alert(message);
                alert.close();
            });
        }, 5000);
    }

    // Add active class to current nav item based on URL
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && currentLocation.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentLocation === '/') {
            link.classList.add('active');
        }
    });

    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        };

        backToTopBtn.addEventListener('click', function() {
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        });
    }

    // Form validation styles
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });

    // Image preview for file inputs
    const imageInputs = document.querySelectorAll('input[type=file][accept*="image"]');

    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                const previewId = input.getAttribute('data-preview');

                if (previewId) {
                    const preview = document.getElementById(previewId);

                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };

                    reader.readAsDataURL(file);
                }
            }
        });
    });

    // Date & time formatting
    const dateElements = document.querySelectorAll('.format-date');

    dateElements.forEach(function(element) {
        const date = new Date(element.textContent);
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        element.textContent = date.toLocaleDateString(undefined, options);
    });

    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.password-toggle');

    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const passwordField = document.querySelector(toggle.getAttribute('data-target'));

            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                toggle.querySelector('i').classList.remove('bi-eye');
                toggle.querySelector('i').classList.add('bi-eye-slash');
            } else {
                passwordField.type = 'password';
                toggle.querySelector('i').classList.remove('bi-eye-slash');
                toggle.querySelector('i').classList.add('bi-eye');
            }
        });
    });

    // Game filter on statistics page
    const gameFilter = document.getElementById('gameFilter');
    if (gameFilter) {
        gameFilter.addEventListener('change', function() {
            const gameType = this.value;
            const gameRows = document.querySelectorAll('.game-row');

            gameRows.forEach(function(row) {
                if (gameType === 'all' || row.classList.contains(gameType)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});