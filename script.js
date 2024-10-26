document.addEventListener('DOMContentLoaded', function () {
    // Login form submission handling
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Client-side validation
            if (username === '' || password === '') {
                errorMessage.textContent = 'Please fill in both fields.';
                return;
            }

            // Backend authentication
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        window.location.href = '/dashboard'; // Redirect on success
                    } else {
                        errorMessage.textContent = result.message;
                    }
                } else {
                    errorMessage.textContent = 'Invalid response from server. Please try again.';
                }
            } catch (error) {
                errorMessage.textContent = 'An error occurred during login. Please try again.';
            }
        });
    }

    // Logout button handling
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', function () {
            window.location.href = '/logout'; // Redirect to logout endpoint
        });
    }

    // Borrow and Return Form Validation
    const borrowReturnForms = document.querySelectorAll('form[action="/borrow"], form[action="/return"]');
    borrowReturnForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            const bookCode = form.querySelector('input[name="book_code"]').value;
            const dateField = form.querySelector('input[type="date"]');

            if (bookCode === '' || dateField.value === '') {
                event.preventDefault();
                alert('Please fill in all fields.');
            }
        });
    });

    // Fetching and updating fine amount dynamically
    const totalFineElement = document.getElementById('total-fine');
    if (totalFineElement) {
        fetch('/get_fine_amount')  // Create this route in your Flask app
            .then(response => response.json())
            .then(data => {
                totalFineElement.textContent = data.total_fine;
            })
            .catch(error => console.error('Error fetching fine amount:', error));
    }

    // Auto-scrolling functionality for recommended books
    const bookList = document.getElementById('book-list');
    const scrollSpeed = 0.1; // Slow scrolling speed
    const scrollInterval = 30; // Interval in milliseconds

    function autoScroll() {
        if (bookList.scrollTop + bookList.clientHeight >= bookList.scrollHeight) {
            bookList.scrollTop = 0; // Reset to top when reaching the end
        } else {
            bookList.scrollTop += scrollSpeed; // Incremental scroll
        }
    }

    // Start the auto-scrolling
    setInterval(autoScroll, scrollInterval);
});
