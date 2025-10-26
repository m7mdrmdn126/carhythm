// Student Interface JavaScript

// Progress tracking
let currentProgress = 0;

function updateProgress(current, total) {
    const percentage = (current / total) * 100;
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
}

// Character count for textareas
function updateCharCount(textarea) {
    const current = textarea.value.length;
    const charCountElement = textarea.parentNode.querySelector('.char-count .current');
    if (charCountElement) {
        charCountElement.textContent = current;
    }
    
    // Visual feedback for character limit
    const limit = textarea.getAttribute('maxlength');
    if (limit) {
        const percentage = (current / limit) * 100;
        if (percentage > 90) {
            textarea.style.borderColor = '#F39C12'; // Warning
        } else if (percentage > 100) {
            textarea.style.borderColor = '#E74C3C'; // Error
        } else {
            textarea.style.borderColor = ''; // Reset
        }
    }
}

// Slider value updates
function updateSliderValue(slider) {
    const valueDisplay = slider.parentNode.querySelector('.value-display');
    if (valueDisplay) {
        valueDisplay.textContent = slider.value + '%';
    }
    
    // Visual feedback
    const percentage = slider.value;
    const hue = (percentage * 120) / 100; // Red to green
    slider.style.background = `linear-gradient(90deg, 
        hsl(${hue}, 70%, 50%) 0%, 
        hsl(${hue}, 70%, 50%) ${percentage}%, 
        #E1E8ED ${percentage}%, 
        #E1E8ED 100%)`;
}

// Auto-save functionality
let autoSaveTimeout;
let lastSavedData = '';

function autoSave() {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
        const form = document.getElementById('questionForm');
        if (!form) return;
        
        const formData = new FormData(form);
        const currentData = Array.from(formData.entries()).toString();
        
        // Only save if data has changed
        if (currentData !== lastSavedData) {
            try {
                const response = await fetch('/student/exam/submit-answers', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    lastSavedData = currentData;
                    showSaveIndicator('Saved automatically', 'success');
                } else {
                    showSaveIndicator('Auto-save failed', 'error');
                }
            } catch (error) {
                showSaveIndicator('Auto-save failed', 'error');
            }
        }
    }, 3000); // Save after 3 seconds of inactivity
}

// Save indicator
function showSaveIndicator(message, type = 'info') {
    let indicator = document.getElementById('saveIndicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'saveIndicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    
    // Set colors based on type
    const colors = {
        success: { bg: '#D4EDDA', color: '#155724', border: '#C3E6CB' },
        error: { bg: '#F8D7DA', color: '#721C24', border: '#F5C6CB' },
        info: { bg: '#CCE7FF', color: '#004085', border: '#B3D9FF' }
    };
    
    const color = colors[type] || colors.info;
    indicator.style.backgroundColor = color.bg;
    indicator.style.color = color.color;
    indicator.style.border = `1px solid ${color.border}`;
    indicator.textContent = message;
    
    // Show indicator
    indicator.style.opacity = '1';
    
    // Hide after 2 seconds
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Form validation
function validateCurrentPage() {
    const form = document.getElementById('questionForm');
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value || (field.type === 'range' && field.value === '')) {
            field.classList.add('error');
            isValid = false;
            
            // Scroll to first error
            if (isValid === false) {
                field.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            field.classList.remove('error');
        }
    });
    
    if (!isValid) {
        showSaveIndicator('Please complete all required fields', 'error');
    }
    
    return isValid;
}

// Navigation functions
function goToPreviousPage() {
    const currentPageElement = document.querySelector('[data-current-page]');
    if (currentPageElement) {
        const currentPage = parseInt(currentPageElement.getAttribute('data-current-page'));
        if (currentPage > 0) {
            window.location.href = `/student/exam/page/${currentPage - 1}`;
        }
    }
}

async function submitAnswers() {
    const form = document.getElementById('questionForm');
    if (!form) return false;
    
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/student/exam/submit-answers', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            return true;
        } else {
            showSaveIndicator('Error saving answers. Please try again.', 'error');
            return false;
        }
    } catch (error) {
        showSaveIndicator('Network error. Please check your connection.', 'error');
        return false;
    }
}

async function submitAndNext() {
    if (!validateCurrentPage()) {
        return;
    }
    
    const success = await submitAnswers();
    if (success) {
        const currentPageElement = document.querySelector('[data-current-page]');
        if (currentPageElement) {
            const currentPage = parseInt(currentPageElement.getAttribute('data-current-page'));
            const totalPages = parseInt(currentPageElement.getAttribute('data-total-pages'));
            
            if (currentPage + 1 < totalPages) {
                window.location.href = `/student/exam/page/${currentPage + 1}`;
            }
        }
    }
}

async function submitAndFinish() {
    if (!validateCurrentPage()) {
        return;
    }
    
    const success = await submitAnswers();
    if (success) {
        window.location.href = '/student/info';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        submitAnswers();
        showSaveIndicator('Saved manually', 'success');
    }
    
    // Ctrl/Cmd + Enter to go to next page
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const nextButton = document.querySelector('[onclick*="submitAndNext"], [onclick*="submitAndFinish"]');
        if (nextButton) {
            nextButton.click();
        }
    }
});

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set up auto-save for form inputs
    const formInputs = document.querySelectorAll('textarea, input[type="range"]');
    formInputs.forEach(input => {
        input.addEventListener('input', autoSave);
        
        // Initialize character counts and slider values
        if (input.tagName === 'TEXTAREA') {
            updateCharCount(input);
        } else if (input.type === 'range') {
            updateSliderValue(input);
        }
    });
    
    // Store current page info
    const currentPage = document.querySelector('[data-current-page]');
    if (!currentPage) {
        // Add data attributes if not present
        const scriptElements = document.querySelectorAll('script');
        scriptElements.forEach(script => {
            const text = script.textContent;
            if (text.includes('currentPage =')) {
                const pageMatch = text.match(/currentPage = (\d+)/);
                const totalMatch = text.match(/totalPages = (\d+)/);
                
                if (pageMatch && totalMatch) {
                    document.body.setAttribute('data-current-page', pageMatch[1]);
                    document.body.setAttribute('data-total-pages', totalMatch[1]);
                }
            }
        });
    }
    
    // Smooth scroll for error fields
    const errorFields = document.querySelectorAll('.error');
    if (errorFields.length > 0) {
        errorFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});

// Page visibility API for saving when user leaves
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // User is leaving the page, save immediately
        clearTimeout(autoSaveTimeout);
        submitAnswers();
    }
});

// Before unload warning for unsaved changes
window.addEventListener('beforeunload', function(e) {
    const form = document.getElementById('questionForm');
    if (form) {
        const formData = new FormData(form);
        const currentData = Array.from(formData.entries()).toString();
        
        if (currentData !== lastSavedData && currentData.length > 0) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    }
});