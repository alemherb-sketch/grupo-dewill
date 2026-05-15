// Admin JS Utilities
document.addEventListener('DOMContentLoaded', () => {
    // Dismiss alerts
    document.querySelectorAll('.admin-alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });

    // Image preview on file input change
    const fileInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    // Try to find a preview container
                    const container = this.closest('.form-group');
                    let preview = container.querySelector('.img-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'img-preview';
                        preview.style = 'max-width: 200px; max-height: 200px; margin-top: 10px; border-radius: 4px; display: block;';
                        container.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});
