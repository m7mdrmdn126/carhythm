// Admin Panel JavaScript

// =============================================
// MODAL FUNCTIONALITY
// =============================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking backdrop
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
                this.classList.remove('show');
                document.body.style.overflow = 'auto';
            }
        });
    });
});

// =============================================
// PAGE MANAGEMENT
// =============================================

function showCreatePageModal() {
    showModal('createPageModal');
}

function hideCreatePageModal() {
    hideModal('createPageModal');
}

function showEditPageModal() {
    showModal('editPageModal');
}

function hideEditPageModal() {
    hideModal('editPageModal');
}

function editPage(id, title, description, orderIndex, isActive, moduleName, moduleEmoji, chapterNumber, estimatedMinutes, completionMessage) {
    document.getElementById('editPageForm').action = `/admin/pages/${id}/edit`;
    document.getElementById('edit_title').value = title || '';
    document.getElementById('edit_description').value = description || '';
    document.getElementById('edit_order_index').value = orderIndex || 0;
    document.getElementById('edit_is_active').checked = isActive;
    
    // Story mode fields
    if (document.getElementById('edit_module_name')) {
        document.getElementById('edit_module_name').value = moduleName || '';
    }
    if (document.getElementById('edit_module_emoji')) {
        document.getElementById('edit_module_emoji').value = moduleEmoji || '';
    }
    if (document.getElementById('edit_chapter_number')) {
        document.getElementById('edit_chapter_number').value = chapterNumber || '';
    }
    if (document.getElementById('edit_estimated_minutes')) {
        document.getElementById('edit_estimated_minutes').value = estimatedMinutes || '';
    }
    if (document.getElementById('edit_completion_message')) {
        document.getElementById('edit_completion_message').value = completionMessage || '';
    }
    
    showEditPageModal();
}

// =============================================
// QUESTION MANAGEMENT
// =============================================

function showCreateQuestionModal() {
    showModal('createQuestionModal');
}

function hideCreateQuestionModal() {
    hideModal('createQuestionModal');
}

function showEditQuestionModal() {
    showModal('editQuestionModal');
}

function hideEditQuestionModal() {
    hideModal('editQuestionModal');
}

function editQuestion(questionId) {
    console.log('Editing question:', questionId);
    // Fetch question data and populate edit modal
    fetch(`/admin/questions/${questionId}/data`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Question data received:', data);
            // Set form action
            const form = document.getElementById('editQuestionForm');
            if (form) {
                form.action = `/admin/questions/${questionId}/edit`;
                console.log('Form action set to:', form.action);
            } else {
                console.error('Edit form not found!');
            }
            
            // Populate basic fields
            const questionText = document.getElementById('edit_question_text');
            if (questionText) {
                questionText.value = data.question_text || '';
                console.log('Set question text:', questionText.value);
            } else {
                console.error('edit_question_text field not found');
            }
            
            const questionTextAr = document.getElementById('edit_question_text_ar');
            if (questionTextAr) questionTextAr.value = data.question_text_ar || '';
            
            const questionType = document.getElementById('edit_question_type');
            if (questionType) questionType.value = data.question_type || '';
            
            const orderIndex = document.getElementById('edit_order_index');
            if (orderIndex) orderIndex.value = data.order_index || 0;
            
            const isRequired = document.getElementById('edit_is_required');
            if (isRequired) isRequired.checked = data.is_required || false;
            
            // Populate slider fields
            const sliderMin = document.getElementById('edit_slider_min_label');
            if (sliderMin) sliderMin.value = data.slider_min_label || '';
            
            const sliderMinAr = document.getElementById('edit_slider_min_label_ar');
            if (sliderMinAr) sliderMinAr.value = data.slider_min_label_ar || '';
            
            const sliderMax = document.getElementById('edit_slider_max_label');
            if (sliderMax) sliderMax.value = data.slider_max_label || '';
            
            const sliderMaxAr = document.getElementById('edit_slider_max_label_ar');
            if (sliderMaxAr) sliderMaxAr.value = data.slider_max_label_ar || '';
            
            // Populate essay fields
            const essayLimit = document.getElementById('edit_essay_char_limit');
            if (essayLimit) essayLimit.value = data.essay_char_limit || '';
            
            // Populate story mode fields
            const sceneTitle = document.getElementById('edit_scene_title');
            if (sceneTitle) sceneTitle.value = data.scene_title || '';
            
            const sceneTitleAr = document.getElementById('edit_scene_title_ar');
            if (sceneTitleAr) sceneTitleAr.value = data.scene_title_ar || '';
            
            const sceneNarrative = document.getElementById('edit_scene_narrative');
            if (sceneNarrative) sceneNarrative.value = data.scene_narrative || '';
            
            const sceneNarrativeAr = document.getElementById('edit_scene_narrative_ar');
            if (sceneNarrativeAr) sceneNarrativeAr.value = data.scene_narrative_ar || '';
            
            const sceneImageUrl = document.getElementById('edit_scene_image_url');
            if (sceneImageUrl) sceneImageUrl.value = data.scene_image_url || '';
            
            const sceneTheme = document.getElementById('edit_scene_theme');
            if (sceneTheme) sceneTheme.value = data.scene_theme || '';
            
            // Toggle fields based on question type
            if (typeof toggleEditQuestionTypeFields === 'function') {
                toggleEditQuestionTypeFields();
            }
            
            console.log('About to show modal');
            showEditQuestionModal();
        })
        .catch(error => {
            console.error('Error fetching question:', error);
            showToast('Failed to load question data', 'error');
        });
}

function toggleQuestionTypeFields() {
    const type = document.getElementById('question_type').value;
    const sliderFields = document.getElementById('sliderFields');
    const essayFields = document.getElementById('essayFields');
    const mcqFields = document.getElementById('mcqFields');
    const orderingFields = document.getElementById('orderingFields');
    
    // Hide all fields first
    if (sliderFields) sliderFields.style.display = 'none';
    if (essayFields) essayFields.style.display = 'none';
    if (mcqFields) mcqFields.style.display = 'none';
    if (orderingFields) orderingFields.style.display = 'none';
    
    // Show relevant fields
    if (type === 'slider' && sliderFields) sliderFields.style.display = 'block';
    if (type === 'essay' && essayFields) essayFields.style.display = 'block';
    if (type === 'mcq' && mcqFields) mcqFields.style.display = 'block';
    if (type === 'ordering' && orderingFields) orderingFields.style.display = 'block';
}

function addMcqOption() {
    const container = document.getElementById('mcqOptionsContainer');
    const optionCount = container.children.length + 1;
    const optionHtml = `
        <div class="mcq-option" style="display: flex; gap: 8px; margin-bottom: 8px; align-items: center;">
            <input type="text" name="mcq_option" placeholder="Option ${optionCount}" required style="flex: 1;">
            <label style="display: flex; align-items: center; gap: 4px; margin: 0;">
                <input type="checkbox" name="mcq_correct" value="${optionCount - 1}">
                <span>Correct</span>
            </label>
            <button type="button" onclick="removeMcqOption(this)" class="btn btn-sm btn-danger">×</button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', optionHtml);
}

function removeMcqOption(button) {
    const container = document.getElementById('mcqOptionsContainer');
    if (container.children.length > 2) {
        button.parentElement.remove();
    } else {
        showToast('Must have at least 2 options', 'error');
    }
}

function addOrderingOption() {
    const container = document.getElementById('orderingOptionsContainer');
    const optionCount = container.children.length + 1;
    const optionHtml = `
        <div class="ordering-option" style="display: flex; gap: 8px; margin-bottom: 8px;">
            <input type="text" name="ordering_option" placeholder="Item ${optionCount}" required style="flex: 1;">
            <button type="button" onclick="removeOrderingOption(this)" class="btn btn-sm btn-danger">×</button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', optionHtml);
}

function removeOrderingOption(button) {
    const container = document.getElementById('orderingOptionsContainer');
    if (container.children.length > 2) {
        button.parentElement.remove();
    } else {
        showToast('Must have at least 2 items', 'error');
    }
}

// =============================================
// CATEGORY MANAGEMENT
// =============================================

function showCreateCategoryModal() {
    showModal('createCategoryModal');
}

function hideCreateCategoryModal() {
    hideModal('createCategoryModal');
}

function showEditCategoryModal() {
    showModal('editCategoryModal');
}

function hideEditCategoryModal() {
    hideModal('editCategoryModal');
}

function editCategory(id, name, description, color, isActive) {
    document.getElementById('editCategoryForm').action = `/admin/categories/${id}/edit`;
    document.getElementById('edit_category_name').value = name || '';
    document.getElementById('edit_category_description').value = description || '';
    document.getElementById('edit_category_color').value = color || '#3498db';
    document.getElementById('edit_category_is_active').checked = isActive;
    showEditCategoryModal();
}

// =============================================
// BULK OPERATIONS
// =============================================

function toggleAllCheckboxes(masterCheckbox) {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = masterCheckbox.checked;
    });
    updateBulkActionsVisibility();
}

function updateBulkActionsVisibility() {
    const checkedCount = document.querySelectorAll('tbody input[type="checkbox"]:checked').length;
    const bulkActions = document.getElementById('bulkActions');
    if (bulkActions) {
        bulkActions.style.display = checkedCount > 0 ? 'block' : 'none';
    }
}

function getSelectedIds() {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function bulkDelete() {
    const ids = getSelectedIds();
    if (ids.length === 0) {
        showToast('No items selected', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${ids.length} item(s)?`)) {
        return;
    }
    
    // Send bulk delete request
    fetch('/admin/results/bulk-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: ids })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(data.message || 'Failed to delete items', 'error');
        }
    })
    .catch(error => {
        showToast('Error deleting items', 'error');
        console.error('Error:', error);
    });
}

// =============================================
// UTILITIES
// =============================================

function validateForm(formId) {
    const form = document.getElementById(formId);
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}

// Auto-resize textareas
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize auto-resize for all textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // Initial resize
        autoResizeTextarea(textarea);
    });
    
    // Add change listeners to checkboxes for bulk actions
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsVisibility);
    });
});

// File upload preview
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Search functionality for tables
function searchTable(searchInputId, tableId) {
    const input = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();

        for (let i = 1; i < rows.length; i++) { // Skip header row
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let match = false;

            for (let j = 0; j < cells.length; j++) {
                const cell = cells[j];
                if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                    match = true;
                    break;
                }
            }

            row.style.display = match ? '' : 'none';
        }
    });
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const colors = {
        success: '#27AE60',
        error: '#E74C3C',
        warning: '#F39C12',
        info: '#4A90E2'
    };
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 100000;
        opacity: 0;
        transition: opacity 0.3s ease;
        font-weight: 500;
        max-width: 300px;
    `;
    
    document.body.appendChild(toast);
    
    // Fade in
    setTimeout(() => toast.style.opacity = '1', 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// Confirmation dialogs
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Export table data to CSV
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.querySelectorAll('tr'));
    
    const csvContent = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => {
            const text = cell.textContent.trim().replace(/"/g, '""');
            return `"${text}"`;
        }).join(',');
    }).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Dropdown toggle
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.matches('.dropdown-toggle')) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    }
});

// Loading spinner
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'loadingSpinner';
    spinner.innerHTML = '<div class="spinner"></div>';
    spinner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999999;
    `;
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        document.body.removeChild(spinner);
    }
}

// Calculate scores for response
function calculateScores(responseId) {
    if (!confirm('Calculate scores for this response?')) return;
    
    showLoadingSpinner();
    
    fetch(`/admin/results/${responseId}/calculate-scores`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner();
        if (data.success) {
            showToast('Scores calculated successfully!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.message || 'Failed to calculate scores', 'error');
        }
    })
    .catch(error => {
        hideLoadingSpinner();
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    });
}