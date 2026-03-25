// Root static/admin/js/public_quiz_admin.js

(function($) {
    $(document).ready(function() {
        // Function to copy full URL to clipboard
        window.copyQuizLink = function(relativeUrl) {
            // Get the full URL based on current window location
            const fullUrl = window.location.origin + relativeUrl;
            
            // Use modern clipboard API if available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(fullUrl).then(function() {
                    showToast('Quiz link copied to clipboard!', 'success');
                }).catch(function(err) {
                    fallbackCopy(fullUrl);
                });
            } else {
                fallbackCopy(fullUrl);
            }
        };

        function fallbackCopy(text) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('Link copied to clipboard!', 'success');
        }

        function showToast(message, type) {
            // Remove any existing toasts
            $('.toast-notification').remove();
            
            // Create toast notification
            const toast = $('<div>')
                .addClass(`toast-notification alert alert-${type}`)
                .text(message)
                .appendTo('body');
            
            setTimeout(() => {
                toast.css('animation', 'slideOut 0.3s ease');
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        }

        // Add click handlers to all copy buttons
        $('.copy-quiz-link').on('click', function(e) {
            e.preventDefault();
            const url = $(this).data('url');
            copyQuizLink(url);
        });
    });
})(django.jQuery);