// app/static/js/main.js

// Example: Add confirmation dialog for delete buttons
document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[action*="/delete"]'); // Select forms whose action contains /delete

    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Get the entity type (e.g., 'supplier', 'intern', 'user') for a better message
            let entityType = 'item';
            if (form.action.includes('/suppliers/')) {
                entityType = 'supplier';
            } else if (form.action.includes('/interns/')) {
                entityType = 'intern';
            } else if (form.action.includes('/users/')) {
                entityType = 'user';
            }

            const confirmation = confirm(`Are you sure you want to delete this ${entityType}?`);
            if (!confirmation) {
                event.preventDefault(); // Stop form submission if user cancels
            }
        });
    });

    // Basic image preview for file inputs (Add this if you have image uploads)
    const pictureInputs = document.querySelectorAll('input[type="file"][name="picture"]');
    pictureInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                const previewId = event.target.id + '_preview'; // e.g., 'picture_preview'
                let previewElement = document.getElementById(previewId);

                // Create preview element if it doesn't exist
                if (!previewElement) {
                    previewElement = document.createElement('img');
                    previewElement.id = previewId;
                    previewElement.style.maxWidth = '150px';
                    previewElement.style.maxHeight = '150px';
                    previewElement.style.marginTop = '10px';
                    // Insert after the file input's parent div (adjust as needed)
                    event.target.closest('.mb-3').appendChild(previewElement);
                }

                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                    previewElement.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                // Hide or clear preview if no file is selected
                 const previewElement = document.getElementById(event.target.id + '_preview');
                 if (previewElement) {
                     previewElement.src = '#';
                     previewElement.style.display = 'none';
                 }
            }
        });
    });

}); // End DOMContentLoaded