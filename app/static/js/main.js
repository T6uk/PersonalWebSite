// Main JavaScript for FC Mara website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Add active class to current nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        // Check if current path starts with the link's href (to handle child routes)
        if (currentPath === link.getAttribute('href') ||
            (currentPath.startsWith(link.getAttribute('href')) &&
             link.getAttribute('href') !== '/' &&
             link.getAttribute('href') !== '/home')) {
            link.classList.add('active');
        }
    });

    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });

    // Add animation to cards when they enter viewport
    if ('IntersectionObserver' in window) {
        const observerCallback = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, {
            root: null,
            threshold: 0.1
        });

        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password strength meter
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.id.includes('password') && !input.id.includes('confirm')) {
            // Create strength meter elements
            const strengthMeter = document.createElement('div');
            strengthMeter.className = 'password-strength-meter mt-1';

            const strengthBar = document.createElement('div');
            strengthBar.className = 'progress';
            strengthBar.style.height = '5px';

            const strengthBarInner = document.createElement('div');
            strengthBarInner.className = 'progress-bar';
            strengthBarInner.style.width = '0%';

            const strengthText = document.createElement('small');
            strengthText.className = 'form-text mt-1';

            // Add elements to DOM
            strengthBar.appendChild(strengthBarInner);
            strengthMeter.appendChild(strengthBar);
            strengthMeter.appendChild(strengthText);

            // Insert after password input
            input.parentNode.insertBefore(strengthMeter, input.nextSibling);

            // Update strength meter on input
            input.addEventListener('input', () => {
                const password = input.value;
                const strength = checkPasswordStrength(password);

                strengthBarInner.style.width = strength.percent + '%';
                strengthText.textContent = strength.message;

                // Update colors
                strengthBarInner.className = 'progress-bar';
                if (strength.percent <= 25) {
                    strengthBarInner.classList.add('bg-danger');
                } else if (strength.percent <= 50) {
                    strengthBarInner.classList.add('bg-warning');
                } else if (strength.percent <= 75) {
                    strengthBarInner.classList.add('bg-info');
                } else {
                    strengthBarInner.classList.add('bg-success');
                }
            });
        }
    });

    // Function to check password strength
    function checkPasswordStrength(password) {
        let strength = 0;
        let message = '';

        if (password.length === 0) {
            return { percent: 0, message: '' };
        }

        // Length check
        if (password.length < 8) {
            message = 'Password is too short';
        } else {
            strength += 25;

            // Character variety checks
            if (/[A-Z]/.test(password)) strength += 15;
            if (/[a-z]/.test(password)) strength += 15;
            if (/[0-9]/.test(password)) strength += 15;
            if (/[^A-Za-z0-9]/.test(password)) strength += 15;

            if (strength > 75) {
                message = 'Strong password';
            } else if (strength > 50) {
                message = 'Good password';
            } else if (strength > 25) {
                message = 'Moderate password';
            } else {
                message = 'Weak password';
            }
        }

        return {
            percent: Math.min(100, strength),
            message: message
        };
    }

    // Table sorting functionality
    const sortableTables = document.querySelectorAll('.table-sortable');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.classList.add('sortable');
            header.insertAdjacentHTML('beforeend', '<span class="sort-icon ms-1"><i class="bi bi-chevron-expand"></i></span>');

            header.addEventListener('click', () => {
                const column = header.cellIndex;
                const sortDir = header.classList.contains('sort-asc') ? 'desc' : 'asc';

                // Reset all headers
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                    h.querySelector('.sort-icon').innerHTML = '<i class="bi bi-chevron-expand"></i>';
                });

                // Update current header
                header.classList.add(`sort-${sortDir}`);
                header.querySelector('.sort-icon').innerHTML =
                    sortDir === 'asc'
                        ? '<i class="bi bi-chevron-up"></i>'
                        : '<i class="bi bi-chevron-down"></i>';

                // Get rows and sort
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));

                const sortedRows = rows.sort((a, b) => {
                    const aValue = a.cells[column].textContent.trim();
                    const bValue = b.cells[column].textContent.trim();

                    // Check if values are numbers
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);

                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return sortDir === 'asc' ? aNum - bNum : bNum - aNum;
                    }

                    // Sort as strings
                    return sortDir === 'asc'
                        ? aValue.localeCompare(bValue)
                        : bValue.localeCompare(aValue);
                });

                // Re-append rows in sorted order
                tbody.innerHTML = '';
                sortedRows.forEach(row => tbody.appendChild(row));
            });
        });
    });

    // Search input highlighting
    const searchInputs = document.querySelectorAll('input[type="search"], input[id*="search"]');
    searchInputs.forEach(searchInput => {
        searchInput.addEventListener('input', () => {
            const searchValue = searchInput.value.trim().toLowerCase();
            if (!searchValue) {
                // Remove all highlighting
                document.querySelectorAll('.search-highlight').forEach(el => {
                    el.outerHTML = el.textContent;
                });
                return;
            }

            // Find the search target (table or list)
            const searchTarget = document.querySelector(searchInput.dataset.searchTarget) ||
                                searchInput.closest('.card').querySelector('table, ul');

            if (!searchTarget) return;

            // Highlight matches in table cells or list items
            const cells = searchTarget.querySelectorAll('td, li');
            cells.forEach(cell => {
                // Remove existing highlights
                while (cell.querySelector('.search-highlight')) {
                    const highlight = cell.querySelector('.search-highlight');
                    highlight.outerHTML = highlight.textContent;
                }

                // Skip if cell content is just HTML (like buttons)
                if (cell.children.length > 0 && cell.textContent.trim().length === 0) return;

                // Apply new highlights
                const text = cell.textContent;
                const lcText = text.toLowerCase();
                const index = lcText.indexOf(searchValue);

                if (index >= 0) {
                    const before = text.substring(0, index);
                    const match = text.substring(index, index + searchValue.length);
                    const after = text.substring(index + searchValue.length);

                    cell.innerHTML = cell.innerHTML.replace(
                        text,
                        `${before}<span class="search-highlight bg-warning">${match}</span>${after}`
                    );
                }
            });
        });
    });

    // Handle Logout Confirmation
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            if (!link.dataset.noConfirm) {
                e.preventDefault();

                if (confirm('Are you sure you want to log out?')) {
                    window.location.href = link.getAttribute('href');
                }
            }
        });
    });
});