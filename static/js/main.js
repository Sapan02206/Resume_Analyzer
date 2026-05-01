// Form submission handling
document.addEventListener('DOMContentLoaded', function() {
    const analyzeForm = document.getElementById('analyzeForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            // Show loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'block';
            }
            
            // Disable submit button
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
            }
        });
    }
    
    // File input validation
    const fileInput = document.getElementById('resume');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileSize = file.size / 1024 / 1024; // in MB
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (fileSize > 16) {
                    alert('File size exceeds 16MB limit. Please choose a smaller file.');
                    fileInput.value = '';
                    return;
                }
                
                if (!['pdf', 'docx'].includes(fileExtension)) {
                    alert('Invalid file format. Please upload a PDF or DOCX file.');
                    fileInput.value = '';
                    return;
                }
            }
        });
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
