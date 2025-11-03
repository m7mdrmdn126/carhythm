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

// MCQ Option Selection Handler
function handleRadioSelection(radio) {
    const container = radio.closest('.mcq-container');
    if (container) {
        const options = container.querySelectorAll('.mcq-option');
        options.forEach(opt => opt.classList.remove('selected'));
        radio.closest('.mcq-option').classList.add('selected');
    }
}

// Add ripple effect to buttons
function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    ripple.style.width = ripple.style.height = `${diameter}px`;
    ripple.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    ripple.style.top = `${event.clientY - button.offsetTop - radius}px`;
    ripple.classList.add('ripple');
    
    const rippleEffect = button.querySelector('.ripple');
    if (rippleEffect) {
        rippleEffect.remove();
    }
    
    button.appendChild(ripple);
}

// Intersection Observer for scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    const animatedElements = document.querySelectorAll('.question-card, .feature-card, .mcq-option');
    animatedElements.forEach(el => observer.observe(el));
}

// Smooth scroll to top button
function addScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '↑';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-coral), var(--accent-coral-hover));
        color: white;
        border: none;
        font-size: 24px;
        cursor: pointer;
        opacity: 0;
        transform: scale(0);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
    `;
    
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.transform = 'scale(1)';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.transform = 'scale(0)';
        }
    });
    
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    scrollBtn.addEventListener('mouseenter', () => {
        scrollBtn.style.transform = 'scale(1.1)';
        scrollBtn.style.boxShadow = '0 6px 30px rgba(255, 107, 107, 0.6)';
    });
    
    scrollBtn.addEventListener('mouseleave', () => {
        scrollBtn.style.transform = 'scale(1)';
        scrollBtn.style.boxShadow = '0 4px 20px rgba(255, 107, 107, 0.4)';
    });
}

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
    
    // Add ripple effect to all buttons
    const buttons = document.querySelectorAll('.btn, .btn-primary, .btn-large');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
    
    // Initialize scroll animations
    initScrollAnimations();
    
    // Add scroll to top button
    addScrollToTop();
    
    // MCQ selection handling - Enhanced
    const mcqContainers = document.querySelectorAll('.mcq-container');
    console.log('Found MCQ containers:', mcqContainers.length);
    
    const mcqOptions = document.querySelectorAll('.mcq-option');
    console.log('Found MCQ options:', mcqOptions.length);
    
    mcqOptions.forEach(option => {
        const input = option.querySelector('input[type="radio"], input[type="checkbox"]');
        if (input) {
            console.log('MCQ input found:', input.type, input.name, input.value);
            
            // Mark already selected options on load
            if (input.checked) {
                option.classList.add('selected');
                console.log('Marked as selected:', input.name);
            }
            
            // Handle clicks on the entire option div
            option.addEventListener('click', function(e) {
                // Don't trigger if clicking directly on input (let native behavior work)
                if (e.target !== input) {
                    input.click();
                }
            });
            
            // Handle input changes
            input.addEventListener('change', function() {
                if (this.type === 'radio') {
                    // For radio buttons, remove selected from all in group, then add to this one
                    const container = this.closest('.mcq-container');
                    if (container) {
                        container.querySelectorAll('.mcq-option').forEach(opt => {
                            opt.classList.remove('selected');
                        });
                    }
                    if (this.checked) {
                        option.classList.add('selected');
                    }
                } else if (this.type === 'checkbox') {
                    // For checkboxes, toggle selected state
                    if (this.checked) {
                        option.classList.add('selected');
                    } else {
                        option.classList.remove('selected');
                    }
                }
            });
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