document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add active class to current nav item
    var currentLocation = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function(link) {
        var linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || currentLocation.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });

    // File input custom text
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = this.files[0].name;
            var nextSibling = this.nextElementSibling;
            nextSibling.innerText = fileName;
        });
    });

    // Confirmation for delete actions
    document.querySelectorAll('.btn-delete').forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
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